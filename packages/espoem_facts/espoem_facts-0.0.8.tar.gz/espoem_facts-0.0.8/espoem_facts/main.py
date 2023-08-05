import logging
import time
import argparse
import os
import random

from steem import Steem
from steem.post import Post
from .facts import FACTS


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logging.basicConfig()


class TxListener:

    def __init__(self, steemd_instance, account):
        self.s = steemd_instance
        self.account = account

    def get_random_fact(self):
        random_index = random.randint(0, len(FACTS))
        return FACTS[random_index]

    def get_last_block_height(self):
        try:
            props = self.s.get_dynamic_global_properties()
            return props['head_block_number']
        except Exception as e:
            return self.get_last_block_height()

    def handle_operation(self, op_type, op_value):
        if op_type != "comment":
            return

        if op_value.get("author") == self.account:
            return

        if 'espoem' in op_value.get("body"):
            p = Post(op_value)
            repliers = [r.get("author") for r in p.get_replies()]
            if self.account in repliers:
                logger.info("Already stated facts on this. Skipping.")
                return

            p.reply(self.get_random_fact(), author=self.account)
            logger.info("Replied to %s" % p.identifier)
            time.sleep(20)

    def parse_block(self, block_id):
        logger.info("Parsing %s", block_id)

        # get all operations in the related block id
        operation_data = self.s.get_ops_in_block(
            block_id, virtual_only=False)

        for operation in operation_data:
            self.handle_operation(*operation['op'][0:2])

    def listen_blocks(self, starting_point=None):
        if not starting_point:
            starting_point = self.get_last_block_height()
        while True:
            while (self.get_last_block_height() - starting_point) > 0:
                starting_point += 1
                self.parse_block(starting_point)

            logger.info("Sleeping for 3 seconds...")
            time.sleep(3)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("account", help="account")
    args = parser.parse_args()

    steemd_instance = Steem(
        nodes=["https://rpc.buildteam.io"],
        keys=os.getenv("ESPOEM_FACTS_POSTING_WIF")
    )

    tx_listener = TxListener(
        steemd_instance=steemd_instance,
        account=args.account
    )

    tx_listener.listen_blocks()


if __name__ == '__main__':
    main()