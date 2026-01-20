import hashlib

filepath = "E:\\final year project\\offchain\\audit reports\\Final_M_V_PSPCL_FY_24-25__1.pdf"

with open(filepath, "rb") as f:
    newhash = hashlib.sha256(f.read()).hexdigest()

print("Recomputed Hash:", newhash)
