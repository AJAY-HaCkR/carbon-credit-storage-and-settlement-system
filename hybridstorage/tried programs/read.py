from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

latest = w3.eth.block_number
count = 0

for blk in range(1, latest + 1):
    block = w3.eth.get_block(blk, full_transactions=True)

    for tx in block.transactions:
        raw = tx.input

        if not raw:
            continue

        try:
            # raw is already bytes
            decoded = raw.decode("utf-8")
            data = json.loads(decoded)

            print("AUDIT RECORD FOUND")
            print("Block:", blk)
            print("Tx Hash:", tx.hash.hex())
            print("Audit Hash:", data["hash"])
            print("Certificates:", data["certificates"])
            print("Timestamp:", data["timestamp"])
            print("-" * 50)

            count += 1

        except Exception as e:
            continue

print("TOTAL AUDITS FOUND:", count)
