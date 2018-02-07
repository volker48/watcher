import json
import logging
import time

import sys

from collections import Counter
from functools import lru_cache
from pprint import pprint

from pathlib import Path

from rpc import BTCRPCClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SATOSHI = 1e8


def load_watchlist():
    """
    Reads a JSON file of the form {'addresses': ['addr1', 'addr2', ..., 'addrn']} containing
    BTC addresses to monitor.
    :return: A set of BTC addresses
    """
    with open('watchlist.json') as f:
        watchlist = json.load(f)
    addresses = watchlist.get('addresses', [])
    return set(addresses)


def handle_coinbase(tx, addresses):
    """
    Function to handle the coinbase transaction of every block, the first transaction
    :param tx: The tx dictionary
    :param addresses: the dictionary of addresses
    :return: None
    """
    vout = tx['vout'][0]
    if 'addresses' not in vout['scriptPubKey']:
        pprint(vout)
        return
    address = vout['scriptPubKey']['addresses'][0]
    addresses[address] += vout['value'] * SATOSHI


def handle_tx(tx, addresses, client):
    handle_inputs(tx, addresses, client)
    handle_outputs(tx, addresses)


def handle_inputs(tx, addresses, client):
    for vin in tx['vin']:
        input_val, address = get_input(vin, client)
        if address:
            addresses[address] -= input_val


def handle_outputs(tx, addresses):
    for vout in tx['vout']:
        script_pub_key = vout['scriptPubKey']
        if 'addresses' not in script_pub_key:
            continue
        address = script_pub_key['addresses'][0]
        value = vout['value'] * SATOSHI
        addresses[address] += value


def get_input(vin, client):
    # Function to cache the most recent 1048576 transactions so we don't have to keep querying bitcoind
    @lru_cache(1 << 20)
    def get_tx(txid):
        return client.gettx(txid)

    txid = vin['txid']
    output_index = vin['vout']
    tx = get_tx(txid)
    output = tx['vout'][output_index]
    if 'addresses' not in output['scriptPubKey']:
        return None, None
    return output['value'] * SATOSHI, output['scriptPubKey']['addresses'][0]


def get_balances(client):
    block_hash, addresses = restore_from_checkpoint(client)
    data = client.getblock(block_hash, 2)
    count = 0
    while 'nextblockhash' in data:
        for i, tx in enumerate(data['tx']):
            if i == 0:
                handle_coinbase(tx, addresses)
                continue
            handle_tx(tx, addresses, client)
        count += 1
        if count % 10 == 0:
            checkpoint('balance_checkpoint.txt', addresses, data['hash'])
        if count % 100 == 0:
            logger.info('Finished hash %s', data['hash'])
        data = client.getblock(data['nextblockhash'], 2)
    return addresses


def restore_from_checkpoint(client):
    balance_path = Path('balance_checkpoint.txt')
    address_path = Path('balances.json')
    if not balance_path.exists() or not address_path.exists():
        logger.info('No checkpoint found starting from block 0')
        addresses = Counter()
        block_hash = client.getblockhash(0)
    else:
        with balance_path.open('r') as balance_file, address_path.open('r') as address_file:
            block_hash = balance_file.readline()
            addresses = Counter(json.load(address_file))
            logger.info('Checkpoint found, starting from blockhash %s', block_hash)
    return block_hash, addresses


def checkpoint(checkpoint_name, addresses, hash):
    with open(checkpoint_name, 'w') as out:
        out.write(hash)
    with open('balances.json', 'w') as out:
        json.dump(addresses, out)


def main():
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        print('Please pass a username and password when running the script like: python monitor.py user pass')
        return
    client = BTCRPCClient(username, password)
    addresses = get_balances(client)
    with open('balances.json', 'w') as o:
        json.dump(addresses, o)
    return
    watchlist = load_watchlist()
    tip = client.getbestblockhash()
    logger.info('Starting at blockhash %s', tip)
    while True:
        blockdata = client.getblock(tip)
        transactions = blockdata.get('tx')
        for transaction in transactions:
            outputs = transaction.get('vout')
            for output in outputs:
                addresses = output['scriptPubKey'].get('addresses', [])
                for address in addresses:
                    if address in watchlist:
                        # TODO: Put this data somewhere permanent like a database
                        logger.info('Found new deposit of %f to address %s', output.get('value'), address)
        last_tip = tip
        while last_tip == tip:
            tip = client.getbestblockhash()
            logger.debug('tip %s last tip %s', tip, last_tip)
            # Could probably sleep even longer
            time.sleep(1)
        logger.info('New block %s', tip)


if __name__ == '__main__':
    main()
