from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

latest = w3.eth.block_number
audits = []

for blk in range(1, latest + 1):
    block = w3.eth.get_block(blk, full_transactions=True)

    for tx in block.transactions:
        raw = tx.input
        if not raw:
            continue

        try:
            decoded = raw.decode("utf-8")
            data = json.loads(decoded)

            record = {
                "block": blk,
                "tx": tx.hash.hex(),
                "company": data["metadata"]["company_id"],
                "credits": data["metadata"]["carbon_credits"],
                "status": data["metadata"]["credit_status"],
                "target": data["metadata"]["govt_target"],
                "achieved": data["metadata"]["achieved_reduction"],
                "time": data["metadata"]["timestamp"]
            }

            audits.append(record)

        except:
            continue

print("AUDITS FROM BLOCKCHAIN\n")

for a in audits:
    print("Block:", a["block"])
    print("Tx:", a["tx"])
    print("Company:", a["company"])
    print("Credits:", a["credits"])
    print("Status:", a["status"])
    print("Target:", a["target"])
    print("Achieved:", a["achieved"])
    print("Time:", a["time"])
    print("-" * 40)

print("TOTAL AUDITS:", len(audits))
