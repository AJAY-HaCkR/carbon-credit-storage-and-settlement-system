from flask import Flask, render_template
from web3 import Web3
import json

app = Flask(__name__)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

def fetch_audits():
    audits = []
    latest = w3.eth.block_number

    for blk in range(1, latest + 1):
        block = w3.eth.get_block(blk, full_transactions=True)

        for tx in block.transactions:
            raw = tx.input
            if not raw:
                continue

            try:
                decoded = raw.decode("utf-8")
                data = json.loads(decoded)

                audits.append({
                    "block": blk,
                    "tx": tx.hash.hex(),
                    "company": data["metadata"]["company_id"],
                    "credits": data["metadata"]["carbon_credits"],
                    "status": data["metadata"]["credit_status"],
                    "target": data["metadata"]["govt_target"],
                    "achieved": data["metadata"]["achieved_reduction"],
                    "time": data["metadata"]["timestamp"]
                })

            except:
                continue

    return audits

@app.route("/")
def dashboard():
    return render_template("index.html", audits=fetch_audits())

if __name__ == "__main__":
    app.run(debug=True)
