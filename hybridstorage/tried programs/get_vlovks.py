from web3 import Web3
from datetime import datetime

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

latest = w3.eth.block_number

print("BLOCK DETAILS FROM GANACHE\n")

for blk in range(1, latest + 1):
    block = w3.eth.get_block(blk)

    timestamp = datetime.fromtimestamp(block.timestamp)

    print("Block Number:", block.number)
    print("Timestamp:", timestamp)
    print("Transactions:", len(block.transactions))
    print("Gas Used:", block.gasUsed)
    print("Gas Limit:", block.gasLimit)
    print("-" * 40)
