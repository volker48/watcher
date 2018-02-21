from flask import request, jsonify

from app import create_app
from rpc import BTCRPCClient

app = create_app()


@app.route('/withdrawal', methods=['POST'])
def withdrawal():
    data = request.get_json()
    client = BTCRPCClient(app.config['RPC_USER'], app.config['RPC_PASS'])
    txid = client.sendtoaddress(data['address'], data['amount'])
    return jsonify(txid=txid)
