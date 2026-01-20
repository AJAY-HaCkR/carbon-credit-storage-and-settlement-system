import hashlib

filepath = "E:\\final year project\offchain\\audit reports\\Final_M_V_PSPCL_FY_24-25__1.pdf"

with open(filepath, "rb") as f:
    data = f.read()

pdfhash = hashlib.sha256(data).hexdigest()
print("Audit PDF Hash:", pdfhash)
