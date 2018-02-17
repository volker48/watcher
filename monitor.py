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
    if c:
        hash = c.hash
        block = client.getblock(hash)
        if 'nextblockhash' in block:
            hash = block['nextblockhash']
    else:
        hash = client.getbestblockhash()
    return hash


def checkpoint(block_hash):
    c = Checkpoint(hash=block_hash)
    current_checkpoint = Checkpoint.query.one_or_none()
    if current_checkpoint:
        db.session.delete(current_checkpoint)
    db.session.add(c)
    db.session.commit()


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
        tip = restore_from_checkpoint(client)
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
            while last_tip == tip:
                tip = client.getbestblockhash()
                logger.debug('tip %s last tip %s', tip, last_tip)
                # Could probably sleep even longer
                time.sleep(3)
            logger.info('New block %s', tip)


if __name__ == '__main__':
    main()
