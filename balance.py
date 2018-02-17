def handle_coinbase(tx):
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
    block_hash = restore_from_checkpoint(client)
    data = client.getblock(block_hash, 2)
    count = 0
    while 'nextblockhash' in data:
        for i, tx in enumerate(data['tx']):
            if i == 0:
                handle_coinbase(tx)
                continue
            handle_tx(tx, client)
        count += 1
        if count % 10 == 0:
            checkpoint(data['hash'])
        if count % 100 == 0:
            logger.info('Finished hash %s', data['hash'])
        data = client.getblock(data['nextblockhash'], 2)