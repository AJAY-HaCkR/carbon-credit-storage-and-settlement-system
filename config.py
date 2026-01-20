# config.py
# EDIT THESE VALUES to match your Ganache setup


CERTIFICATE_PRICES = {
    "escert": 250,  
    "rec": 180,      # 1 REC = ₹180
    "carbon": 300,   # 1 Carbon Credit = ₹300
}


GANACHE_RPC = "http://127.0.0.1:7545"   # default Ganache UI RPC

# Master account (must be funded on Ganache). This private key will be used to send ETH.
# WARNING: Do NOT use real private keys. This is for local/testing only.
MASTER_PRIVATE_KEY = "0xb22d7b11311ecb01c10922550e805555b9b04f3b24aa2876cfe8c14493e13665"


COMPANY_ACCOUNTS = {
    0: "0x7D5c104aF544310Bb20720Fa114ddDb79C4cDe9e",
    1: "0x6e8C0a1FE276fB1154cd6e3bf29790b85044253C",
    2: "0x643B0F8F1B5424138511e1a23D3e6eAB300E9409",
    3: "0x3503Cb2a8A3E36d0C9b7fA264860baDf565d92c4"
}


INR_PER_UNIT = 1000.0

import requests

def get_live_eth_inr_rate():
    """Fetch live ETH-INR price from CoinGecko with safe fallback."""
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=inr",
            timeout=5
        )
        data = response.json()
        rate = data["ethereum"]["inr"]
        print(f"Live ETH-INR rate fetched: ₹{rate}")
        return rate
    except Exception as e:
        print(f"Failed to fetch live ETH price: {e}")
        return 300000.0  # fallback if API unavailable

# Use live price
ETH_INR_RATE = get_live_eth_inr_rate()  # e.g., 1 ETH = 200,000 INR
