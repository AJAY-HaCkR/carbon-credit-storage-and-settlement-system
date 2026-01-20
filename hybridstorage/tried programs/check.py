from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

latest = w3.eth.block_number

for blk in range(latest, max(latest-5,0), -1):
    block = w3.eth.get_block(blk, full_transactions=True)
    for tx in block.transactions:
        print("Block", blk, "Input:", tx.input)
