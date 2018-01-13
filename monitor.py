import json
import logging
import requests
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BTCRPCClient(object):
    """
    RPC client for communicating with bitcoind.
    """

    def __init__(self, username, password, host='127.0.0.1', port='18332'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.service_url = f"http://{host}:{port}"

    def _make_request(self, rpcmethod, *args):
        """
        Handles formatting the request JSON that will be sent to bitcoind.
        :param rpcmethod: The name of the RPC method to call on bitcoind
        :param args: Additional arguments for the method
        :return: the deserialized JSON result of calling the RPC method on bitcoind
        """
        logger.debug('Args %s', args)
        payload = {'method': rpcmethod, 'params': args, 'id': 'BTCRPCClient', 'jsonrpc': '1.0'}
        logger.debug('payload %s', payload)
        resp = requests.post(self.service_url, json=payload, auth=(self.username, self.password))
        logger.debug('resp body: %s', resp.text)
        resp.raise_for_status()
        resp_json = resp.json()
        if resp_json.get('Error') is not None:
            logger.error('Error making RPC request: ', resp_json.get('Error'))
        return resp_json

    def getbestblockhash(self):
        """
        Queries bitcoind for the tip of the blockchain hash
        :return: string hash of the tip of the block chain
        """
        resp_json = self._make_request('getbestblockhash')
        return resp_json.get('result')

    def getblock(self, blockhash, verbosity=2):
        """
        Queries bitcoind for the data about block :blockhash:

        If verbosity is 0, returns a string that is serialized, hex-encoded data for block 'hash'.
        If verbosity is 1, returns an Object with information about block <hash>.
        If verbosity is 2, returns an Object with information about block <hash> and information about each transaction.

        :param blockhash: The hash of the block to lookup.
        :param verbosity: How verbose the response from bitcoind should be.
        :return: The data for the block with hash :blockhash:
        """

        resp_json = self._make_request('getblock', blockhash, verbosity)
        return resp_json.get('result')


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


def main():
    client = BTCRPCClient('marcus', 'test')
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
                        logger.info('Found new deposit of %f to address %s', output.get('value'), address)
        last_tip = tip
        while last_tip == tip:
            tip = client.getbestblockhash()
            logger.debug('tip %s last tip %s', tip, last_tip)
            time.sleep(1)
        logger.info('New block %s', tip)


if __name__ == '__main__':
    main()
