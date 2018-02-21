import logging
import requests

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
        self.session = requests.Session()
        self.session.auth = (self.username, self.password)

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
        resp = self.session.post(self.service_url, json=payload)
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

    def getblockhash(self, block_number):
        """

        :param block_number:
        :return: String hash of :block_number:
        """
        resp_json = self._make_request('getblockhash', block_number)
        return resp_json.get('result')

    def getblockcount(self):
        """
        Returns the number of blocks in the longest blockchain.
        :return: integer number of blocks in the longest blockchain
        """

        resp_json = self._make_request('getblockcount')
        return resp_json.get('result')

    def gettx(self, txid):
        resp_json = self._make_request('getrawtransaction', txid, 2)
        return resp_json.get('result')

    def sendtoaddress(self, address, amount):
        resp_json = self._make_request('sendtoaddress', address, amount)
        return resp_json.get('result')
