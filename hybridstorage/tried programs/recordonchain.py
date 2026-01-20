from web3 import Web3
import json
import hashlib
from datetime import datetime

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
account = w3.eth.accounts[0]

filepath = "E:\\final year project\\offchain\\audit reports\\Final_M_V_PSPCL_FY_24-25__1.pdf"

with open(filepath, "rb") as f:
    pdfhash = hashlib.sha256(f.read()).hexdigest()

data = {
    "hash": pdfhash,
    "certificates": 12,
    "timestamp": datetime.utcnow().isoformat()
}

tx = {
    "from": account,
    "to": account,
    "value": 0,
    "data": w3.to_hex(text=json.dumps(data))
}

txhash = w3.eth.send_transaction(tx)
print("Blockchain Transaction Hash:", txhash.hex())
