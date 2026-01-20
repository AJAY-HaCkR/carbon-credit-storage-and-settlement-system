from datetime import datetime

auditmeta = {
    "plant": "Plant A",
    "target_emission": 500,
    "achieved_reduction": 120,
    "certificates_earned": 12,
    "audit_year": 2025,
    "timestamp": datetime.utcnow().isoformat()
}

print(auditmeta)

