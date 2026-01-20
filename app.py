
import json
from decimal import Decimal
from flask import Flask, request, jsonify, send_from_directory
from web3 import Web3
from eth_account import Account
from models import Certificate, create_session
import config
from sqlalchemy import select, and_, update
from datetime import datetime

app = Flask(__name__, static_folder="static", static_url_path="/static")


w3 = Web3(Web3.HTTPProvider(config.GANACHE_RPC))
master_account = Account.from_key(config.MASTER_PRIVATE_KEY)
MASTER_ADDRESS = master_account.address

# DB
db = create_session()

# Helpers
def company_address(company_id):
    if company_id not in config.COMPANY_ACCOUNTS:
        return None
    return Web3.to_checksum_address(config.COMPANY_ACCOUNTS[company_id])

def inr_to_eth(inr_amount: float) -> float:
    
    return float(Decimal(inr_amount) / Decimal(config.ETH_INR_RATE))

# Routes -------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/company")
def company_panel():
    return send_from_directory("static", "company.html")

@app.route("/validator")
def validator_panel():
    return send_from_directory("static", "validator.html")


@app.route("/api/claim", methods=["POST"])
def api_claim():
    """
    JSON body:
    {
      "company_id": 0,
      "cert_type": "escert",
      "units": 3
    }
    """
    data = request.get_json()
    company_id = int(data.get("company_id"))
    cert_type = data.get("cert_type")
    units = int(data.get("units", 0))

    if company_id not in config.COMPANY_ACCOUNTS:
        return jsonify({"error": "Unknown company_id"}), 400
    if units <= 0:
        return jsonify({"error": "units must be > 0"}), 400

    session = db
    
    stmt = select(Certificate).where(
        Certificate.company_id == company_id,
        Certificate.cert_type == cert_type
    )
    existing = session.execute(stmt).scalars().all()
    max_index = -1
    if existing:
        max_index = max([c.unit_index for c in existing])
    
    new_certs = []
    for i in range(1, units + 1):
        new_unit_index = max_index + i
        cert = Certificate(
            company_id=company_id,
            cert_type=cert_type,
            unit_index=new_unit_index,
            status="fresh"
        )
        session.add(cert)
        new_certs.append(cert)
    session.commit()
    created = [{"id": c.id, "unit_index": c.unit_index} for c in new_certs]
    return jsonify({"created": created}), 201

# API: list claims (filter by status optionally)
@app.route("/api/claims", methods=["GET"])
def api_list_claims():
    status = request.args.get("status")  # optional filter
    company_id = request.args.get("company_id")
    session = db
    stmt = select(Certificate)
    if status:
        stmt = stmt.where(Certificate.status == status)
    if company_id:
        stmt = stmt.where(Certificate.company_id == int(company_id))
    items = session.execute(stmt).scalars().all()
    out = []
    for c in items:
        out.append({
            "id": c.id,
            "company_id": c.company_id,
            "cert_type": c.cert_type,
            "unit_index": c.unit_index,
            "status": c.status,
            "eth_rewarded": c.eth_rewarded,
            "validator_id": c.validator_id,
            "timestamp": c.timestamp.isoformat() if c.timestamp else None,
            "burnt_timestamp": c.burnt_timestamp.isoformat() if c.burnt_timestamp else None
        })
    return jsonify(out)

# API: validator approve or reject
@app.route("/api/validate", methods=["POST"])
def api_validate():
    """
    body:
    {
      "validator_id": 23,
      "company_id": 0,
      "cert_type": "escert",
      "unit_indices": [0,1,2],   # list of unit_index or certificate ids? We'll accept ids for precision
      "action": "approve" / "reject"
    }
    """
    data = request.get_json()
    validator_id = int(data.get("validator_id"))
    company_id = int(data.get("company_id"))
    action = data.get("action")
    ids = data.get("ids", [])  # list of certificate row ids to act on

    # Basic validations
    if action not in ("approve", "reject"):
        return jsonify({"error": "action must be approve or reject"}), 400
    # Validator cannot be Ganache company account number (rule) -- here validator_id is numeric and separate
    # To enforce: ensure validator_id not equal to any company_id:
    if validator_id in config.COMPANY_ACCOUNTS:
        return jsonify({"error": "Validator id cannot be a company id (forbidden)"}), 400

    session = db
    # Fetch requested certificates by id and ensure they are fresh and match company
    stmt = select(Certificate).where(Certificate.id.in_(ids), Certificate.company_id == company_id)
    certs = session.execute(stmt).scalars().all()
    if not certs:
        return jsonify({"error": "No certificates found for the given ids/company"}), 404

    # Ensure certificates are fresh (not already approved/burnt/rejected)
    for c in certs:
        if c.status != "fresh":
            return jsonify({"error": f"Certificate id {c.id} is not fresh (status={c.status})"}), 400

    if action == "reject":
        for c in certs:
            c.status = "rejected"
            c.validator_id = validator_id
            c.eth_rewarded = 0.0
        session.commit()
        return jsonify({"rejected_ids": [c.id for c in certs]})

    
    CERTIFICATE_PRICES = {
        "escert": 2500,   
        "rec": 360,      
        "carbon": 300    
    }

# Determine type from first certificate (all are same type in this claim)
    cert_type = certs[0].cert_type if certs else "escert"
    unit_price_inr = CERTIFICATE_PRICES.get(cert_type, config.INR_PER_UNIT)

# Calculate rewards
    units = len(certs)
    reward_inr = units * unit_price_inr
    reward_eth = inr_to_eth(reward_inr)


    # Transfer ETH from master to company Ganache account
    company_addr = company_address(company_id)
    if company_addr is None:
        return jsonify({"error": "Unknown company address"}), 400

    try:
        # transaction
        nonce = w3.eth.get_transaction_count(MASTER_ADDRESS)
        tx = {
            "nonce": nonce,
            "to": company_addr,
            "value": int(w3.to_wei(reward_eth, "ether")),
            "gas": 21000,
            "gasPrice": w3.eth.gas_price,
        }
        # Sign
        signed = w3.eth.account.sign_transaction(tx, private_key=config.MASTER_PRIVATE_KEY)
        # Send
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    except Exception as e:
        return jsonify({"error": "ETH transfer failed", "details": str(e)}), 500

    # Update DB: mark certificates approved
    for c in certs:
        c.status = "approved"
        c.validator_id = validator_id
        c.eth_rewarded = reward_eth / units  # store per-unit ETH (optionally store full)
    session.commit()

    return jsonify({
        "approved_ids": [c.id for c in certs],
        "tx_hash": tx_hash.hex(),
        "total_eth": reward_eth,
        "per_unit_eth": reward_eth / units
    })

# API: burn approved certificates (only status approved -> burnt)
@app.route("/api/burn", methods=["POST"])
def api_burn():
    """
    body:
    {
      "certificate_ids": [1,2,3]
    }
    """
    data = request.get_json()
    ids = data.get("certificate_ids", [])
    session = db
    stmt = select(Certificate).where(Certificate.id.in_(ids))
    certs = session.execute(stmt).scalars().all()
    if not certs:
        return jsonify({"error": "No certificates found"}), 404
    updated = []
    for c in certs:
        if c.status != "approved":
            return jsonify({"error": f"Only approved certificates can be burnt. id {c.id} status {c.status}"}), 400
        c.status = "burnt"
        c.burnt_timestamp = datetime.utcnow()
        updated.append(c.id)
    session.commit()
    return jsonify({"burnt": updated})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
