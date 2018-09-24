import requests

from operator import itemgetter

from flask import request, jsonify, abort
from collections import Counter

from app import create_app
from rpc import BTCRPCClient

app = create_app()

TX_FEE = 1e-5


@app.route('/withdrawal', methods=['POST'])
def withdrawal():
    """
    Accepts an HTTP POST method with a JSON body

    The JSON is expected to be an object with the following properties.

    {
        "input_address": {"output_address": "address", "amount": btc_amount}
    }

    Where input_address is the BTC address that has unspent funds.
    Output address is the address to withdraw to and BTC amount is the amount
    to be sent to output_address.

    :return:
    """
    data = request.get_json()
    client = BTCRPCClient(app.config['RPC_USER'], app.config['RPC_PASS'])
    for input_addr, output_data in data.items():
        output_address, withdraw_amount = output_data['output_address'], output_data['amount']
        utxos = client.list_unspent(input_addr)
        total_available = sum(map(itemgetter('amount'), utxos))

        # TODO: Not sure how we want to handle the tx FEE. That is, do we want it to be dynamic or static? If static
        # What should it be set to? If dynamic, how do we figure it out
        if withdraw_amount > (total_available - TX_FEE):
            abort(400)

        utxos = sorted(utxos, key=itemgetter('amount'), reverse=True)
        inputs = []
        outputs = {output_address: withdraw_amount}
        if (utxos[0] - TX_FEE) > withdraw_amount:
            change = utxos[0] - TX_FEE - withdraw_amount
            if change > 0:
                outputs[input_addr] = change




    txid = client.sendtoaddress(data['address'], data['amount'])
    return jsonify(txid=txid)
