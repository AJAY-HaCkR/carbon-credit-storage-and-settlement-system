from web3 import Web3
import json
import hashlib
from datetime import datetime

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

sender = w3.eth.accounts[0]
receiver = w3.eth.accounts[1]

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

doc_hash = file_hash("E:\\final year project\\offchain\\audit reports\\Final_M_V_PSPCL_FY_24-25__1.pdf")

metadata = {
    "company_id": "COMP_1024",
    "timestamp": datetime.utcnow().isoformat(),
    "document_hash": doc_hash,
    "carbon_credits": 30,
    "credit_status": "TRADED",
    "govt_target": 200,
    "achieved_reduction": 230
}

metadata_json = json.dumps(metadata, sort_keys=True)
metadata_hash = hashlib.sha256(metadata_json.encode()).hexdigest()

payload = json.dumps({
    "metadata_hash": metadata_hash,
    "metadata": metadata
}).encode("utf-8")

tx = {
    "from": sender,
    "to": receiver,
    "value": 0,
    "data": payload,
    "gas": 300000
}

tx_hash = w3.eth.send_transaction(tx)

print("ON-CHAIN STORAGE SUCCESS")
print("Transaction Hash:", tx_hash.hex())
print("Metadata Hash:", metadata_hash)
