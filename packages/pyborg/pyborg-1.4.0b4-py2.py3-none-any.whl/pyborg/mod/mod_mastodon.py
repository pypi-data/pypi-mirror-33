import logging
import time
import sys

import arrow
import lxml.html
import requests
import toml
from mastodon import Mastodon

logger = logging.getLogger(__name__)


class PyborgMastodon(object):
    """docstring for PyborgMastodon"""
    def __init__(self, conf_file):
        self.toml_file = conf_file
        self.settings = toml.load(conf_file)
        self.last_look = arrow.get(self.settings['mastodon']['last_look'])
        self.multiplexing = True
        self.multi_server = self.settings['pyborg']['multi_server']

    def teardown(self):
        self.settings['mastodon']['last_look'] = self.last_look
        with open(self.toml_file, "w") as f:
            toml.dump(self.settings, f)
        if not self.multiplexing:
            self.pyborg.save_all()

    def learn(self, body):
        if self.multiplexing:
            try:
                ret = requests.post("http://{}:2001/learn".format(self.multi_server), data={"body": body})
                if ret.status_code > 499:
                    logger.error("Internal Server Error in pyborg_http. see logs.")
                else:
                    ret.raise_for_status()
            except requests.exceptions.ConnectionError as e:
                logger.exception(e)
                self.teardown()
                sys.exit(7)
        else:
            self.pyborg.learn(body)

    def reply(self, body):
        if self.multiplexing:
            try:
                ret = requests.post("http://{}:2001/reply".format(self.multi_server), data={"body": body})
                if ret.status_code == requests.codes.ok:
                    reply = ret.text
                    logger.debug("got reply: %s", reply)
                elif ret.status_code > 499:
                    logger.error("Internal Server Error in pyborg_http. see logs.")
                    return
                else:
                    ret.raise_for_status()
                return reply
            except requests.exceptions.ConnectionError as e:
                logger.exception(e)
                self.teardown()
                sys.exit(7)
        else:
            return self.pyborg.reply(body)

    def should_reply_direct(self, usern):
        should_reply = []
        should_reply.extend([a['acct'] for a in self.mastodon.account_followers(self.my_id)])  # is this cached?
        return usern in should_reply

    def is_reply_to_me(self, item):
        logger.debug(item)
        try:
            if item["in_reply_to_account_id"] == self.my_id:
                return True
            else:
                return False
        except KeyError:
            return False

    def handle_toots(self, toots):
        for item in toots:
            logger.debug(arrow.get(item["created_at"]) > self.last_look)
            logger.debug(item['content'])
            logger.debug(arrow.get(item["created_at"]) - self.last_look)
            if (arrow.get(item["created_at"]) > self.last_look or True) and item["account"]["id"] is not self.my_id:
                logger.debug("Got New Toot: {}".format(item))
                fromacct = item['account']['acct']  # to check if we've banned them?
                parsed_html = lxml.html.fromstring(item['content'])
                body = parsed_html.text_content()
                if self.settings['pyborg']['learning']:
                    self.learn(body)
                reply = self.reply(body)
                if reply and (self.should_reply_direct(fromacct) or self.is_reply_to_me(item)):
                    self.mastodon.status_post(reply, in_reply_to_id=item['id'])
                else:
                    logger.info("Couldn't toot.")

    def start(self):
        self.mastodon = Mastodon(
            client_id='pyborg_mastodon_clientcred.secret',
            access_token='pyborg_mastodon_usercred.secret',
            api_base_url=self.settings['mastodon']['base_url']
        )
        self.my_id = self.mastodon.account_verify_credentials()['id']

        while True:
            tl = self.mastodon.timeline()
            toots = []
            mentions = [notif['status'] for notif in self.mastodon.notifications() if notif['type'] == "mention"]
            toots.extend(tl)
            toots.extend(mentions)
            self.handle_toots(toots)
            self.last_look = arrow.utcnow()
            logger.debug("Sleeping for {} seconds".format(self.settings['mastodon']['cooldown']))
            time.sleep(self.settings['mastodon']['cooldown'])
