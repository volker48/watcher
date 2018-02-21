import json
import logging
import time

import sys

from app import create_app
from models import Checkpoint, db, Address, Watchlist
from rpc import BTCRPCClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SATOSHI = 1e8


def restore_from_checkpoint(client):
    c = Checkpoint.query.one_or_none()
    should_wait = False
    if c:
        hash = c.hash
        block = client.getblock(hash)
        if 'nextblockhash' in block:
            # A block exists after the checkpoint, set that as our current block
            hash = block['nextblockhash']
        else:
            # If the checkpoint is at the newest block, then we need to wait for a new block since
            # this block was already processed
            should_wait = True
    else:
        # No checkpoint starting from the best block
        hash = client.getbestblockhash()
    return hash, should_wait


def checkpoint(block_hash):
    """
    Save the most recently processed block hash to the database
    :param block_hash: The hash of the most recently processed hash
    :return: None
    """
    cp = Checkpoint.query.one_or_none()
    if cp is None:
        cp = Checkpoint()
    cp.hash = block_hash
    db.session.add(cp)
    db.session.commit()


def wait_for_new_block(client, last_tip, tip):
    """
    Poll the bitcoin daemon for a new block
    :param client: BTCRPCClient
    :param last_tip: the last processed tip
    :param tip: the current tip
    :return: the hash of the new tip
    """
    while last_tip == tip:
        tip = client.getbestblockhash()
        logger.debug('tip %s last tip %s', tip, last_tip)
        time.sleep(3)
    logger.info('New block %s', tip)
    return tip


def main():
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        print('Please pass a username and password when running the script like: python monitor.py user pass')
        return
    client = BTCRPCClient(username, password)
    app = create_app()
    with app.app_context():
        tip, wait_for_block = restore_from_checkpoint(client)
        if wait_for_block:
            tip = wait_for_new_block(client, tip, tip)
        logger.info('Starting at blockhash %s', tip)
        while True:
            blockdata = client.getblock(tip)
            transactions = blockdata.get('tx', [])
            for transaction in transactions:
                outputs = transaction.get('vout', [])
                for output in outputs:
                    addresses = output['scriptPubKey'].get('addresses', [])
                    for hash in addresses:
                        if Watchlist.is_on_watchlist(hash):
                            address = Address.get_or_create(hash)
                            address.balance += output.get('value', 0.0) * SATOSHI
                            db.session.add(address)
                            db.session.commit()
                            logger.info('Found new deposit of %f to address %s', output.get('value'), address)
            checkpoint(tip)
            last_tip = tip
            tip = wait_for_new_block(client, last_tip, tip)


if __name__ == '__main__':
    main()
