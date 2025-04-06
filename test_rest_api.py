# test_rest_api.py

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read BullX credentials from .env
BULLX_AUTH_TOKEN = os.getenv("BULLX_AUTH_TOKEN")
BULLX_CS_TOKEN = os.getenv("BULLX_CS_TOKEN")
BULLX_COOKIES = os.getenv("BULLX_COOKIES")

def test_rest_api():
    print("🔐 Loaded BullX Auth Token:", BULLX_AUTH_TOKEN[:15])
    print("🔐 Loaded BullX CS Token:", BULLX_CS_TOKEN[:15])
    print("🍪 Loaded BullX Cookies:", BULLX_COOKIES[:80], "...")

    url = "https://api-neo.bullx.io/v2/api/getApprovalStatusV3"
    
    headers = {
        "Authorization": f"Bearer {BULLX_AUTH_TOKEN}",
        "x-cs-token": BULLX_CS_TOKEN,
        "Content-Type": "application/json",
        "Origin": "https://api-neo.bullx.io",
        "Referer": "https://api-neo.bullx.io",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Cookie": BULLX_COOKIES  # ✅ THIS WAS MISSING!
    }

    payload = {
        "name": "getApprovalStatusV3",
        "chainId": 1399811149,
        "tokenAddress": "D7QAmjFjevofTV653qxplLmmuxzVP48mJz4jnXzY5SH",
        "protocol": None,
        "walletAddresses": [
            "HsDrL5RtGUsrnbCp08ULHSZfKM8egEMNyvHrL3U2rR",
            "GL06fGRaopCnsk2VacpjxNTGTprncctjM3Erui6qK"
        ]
    }

    try:
        print("📦 Testing API call...")
        response = requests.post(url, headers=headers, json=payload)
        print("📨 Raw Response:", response.status_code, response.text[:200])
        response.raise_for_status()
        print("✅ SUCCESS: REST API works!")
    except Exception as e:
        print(f"❌ REST API test failed: {e}")

if __name__ == "__main__":
    test_rest_api()
