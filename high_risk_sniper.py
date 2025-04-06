import time
import re
import os
from datetime import datetime
import requests
import pusher
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# ENVIRONMENT VARIABLES
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BULLX_AUTH_TOKEN = os.getenv("BULLX_AUTH_TOKEN")
BULLX_CS_TOKEN = os.getenv("BULLX_CS_TOKEN")
BULLX_COOKIES = os.getenv("BULLX_COOKIES")

# Debug: Print raw values of environment variables
print("DEBUG: Raw TELEGRAM_TOKEN:", TELEGRAM_TOKEN)
print("DEBUG: Raw TELEGRAM_CHAT_ID:", TELEGRAM_CHAT_ID)
print("DEBUG: Raw BULLX_AUTH_TOKEN:", BULLX_AUTH_TOKEN)
print("DEBUG: Raw BULLX_CS_TOKEN:", BULLX_CS_TOKEN)
print("DEBUG: Raw BULLX_COOKIES:", BULLX_COOKIES)

# Verify environment variables
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Telegram credentials are not set properly.")
if not BULLX_AUTH_TOKEN or not BULLX_CS_TOKEN:
    raise ValueError("BullX authentication tokens are not set properly.")

print("🔐 Loaded Telegram token:", TELEGRAM_TOKEN[:15])
print("🔐 Loaded BullX Auth Token:", BULLX_AUTH_TOKEN[:15])
print("🔐 Loaded BullX CS Token:", BULLX_CS_TOKEN[:15])
print("🔐 Loaded BullX Cookies:", BULLX_COOKIES)

# Test the REST API to verify the tokens
def test_rest_api():
    url = "https://api-neo.bullx.io/v2/api/getApprovalStatusV3"
    headers = {
    "Authorization": f"Bearer {BULLX_AUTH_TOKEN}",
    "x-cs-token": BULLX_CS_TOKEN,
    "Content-Type": "application/json",
    "Origin": "https://neo.bullx.io",
    "Referer": "https://neo.bullx.io/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Cookie": BULLX_COOKIES  # must include both bullx-cs-token and bullx-session-token
}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print("✅ REST API test successful. Response:", response.json()[:100], "...")
    except requests.exceptions.RequestException as e:
        print(f"❌ REST API test failed: {e.response.text if e.response else str(e)}")

# Helper function to clean and parse numeric values
def clean_numeric(value):
    if value is None:
        return 0
    value_str = str(value)
    match = re.match(r'^-?\d*\.?\d+', value_str)
    if match:
        return float(match.group())
    return 0

# SEND TELEGRAM MESSAGE
def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Telegram message sent")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Telegram error: {e.response.text if e.response else str(e)}")

# Function to fetch Pusher authentication token
def get_pusher_auth_token(channel_name, socket_id):
    url = "https://api-neo.bullx.io/pusher/auth"  # Updated based on the JavaScript code
    headers = {
        "Authorization": f"Bearer {BULLX_AUTH_TOKEN}",
        "x-cs-token": BULLX_CS_TOKEN,
        "Cookie": BULLX_COOKIES
    }
    data = {
        "socket_id": socket_id,
        "channel_name": channel_name
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        auth_data = response.json()
        print("✅ Pusher auth token fetched:", auth_data)
        return auth_data["auth"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to fetch Pusher auth token: {e.response.text if e.response else str(e)}")
        return None

# Subscribe to new token creations using Pusher
def subscribe_to_new_tokens():
    # Pusher configuration
    pusher_app_key = "prowess-frank-sensitive-protocol-78c1ent-js"  # From the WebSocket URL
    pusher_host = "stream.bullx.io"  # Custom host from the WebSocket URL
    pusher_port = 443  # From the JavaScript code (wssPort)
    pusher_cluster = None  # No cluster specified; using custom host

    # Initialize Pusher client
    try:
        pusher_client = pusher.Pusher(
            app_id="",
            key=pusher_app_key,
            secret="",  # Not needed for client-side
            cluster=pusher_cluster,
            host=pusher_host,
            ssl=True,
            port=pusher_port
        )
        print("✅ Pusher client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Pusher client: {str(e)}")
        return

    # Bind authentication handler for private channels
    def auth_handler(channel_name, socket_id):
        auth_token = get_pusher_auth_token(channel_name, socket_id)
        return auth_token

    pusher_client.connection.bind("pusher:connection_established", lambda data: print("✅ Pusher connection established:", data))
    pusher_client.connection.bind("pusher:error", lambda data: print("❌ Pusher error:", data))

    # Subscribe to a channel (we need to determine the channel name)
    channel_name = "private-solana-token-supply-updates"  # Placeholder; update based on browser messages
    channel = pusher_client.subscribe(channel_name, auth=auth_handler)

    # Bind to the event (we need to determine the event name)
    def on_token_update(data):
        print("📩 Received message:", data)
        # Process the new token (similar to the previous script)
        block_time = data.get("Block", {}).get("Time")  # Adjust based on actual message structure
        creator = data.get("Transaction", {}).get("Signer")
        token_data = data.get("TokenSupplyUpdate", {}).get("Currency", {})
        symbol = token_data.get("Symbol") or "???"
        name = token_data.get("Name") or "???"
        token_address = token_data.get("MintAddress") or "???"

        # Calculate age in minutes
        if block_time:
            block_datetime = datetime.fromisoformat(block_time.replace("Z", "+00:00"))
            current_time = datetime.utcnow()
            age_seconds = (current_time - block_datetime).total_seconds()
            age = age_seconds / 60  # Convert to minutes
        else:
            age = 0

        # Placeholder values for missing fields
        lp = 0
        mc = 0
        buy_vol = 0
        sell_vol = 0
        vol = buy_vol + sell_vol
        dev_hold = 0
        top_holder = 0
        holders = 0
        snipers = 0

        print(f"🔍 New Token Detected - Symbol: {symbol}, Age: {age} mins, Creator: {creator}")

        # Log why the token fails filters
        filter_reasons = []
        if age < 2:
            filter_reasons.append(f"age ({age} < 2)")
        if age > 3:
            filter_reasons.append(f"age ({age} > 3)")
        if lp < 0.1:
            filter_reasons.append(f"lp ({lp} < 0.1)")
        if mc < 2000 or mc > 500000:
            filter_reasons.append(f"mc ({mc} not in 2000-500000)")
        if dev_hold > 50:
            filter_reasons.append(f"dev_hold ({dev_hold} > 50)")
        if top_holder > 50:
            filter_reasons.append(f"top_holder ({top_holder} > 50)")
        if holders < 1:
            filter_reasons.append(f"holders ({holders} < 1)")

        # Apply filters
        if (
            age < 2 or
            age > 3 or
            lp < 0.1 or
            mc < 2000 or mc > 500000 or
            dev_hold > 50 or
            top_holder > 50 or
            holders < 1
        ):
            print(f"❌ Skipping {symbol} (didn't pass filters: {', '.join(filter_reasons)})")
            return

        nova_cmd = f"/snipe {token_address} 0.3 slippage=6% maxwallet=3%"

        msg = (
            f"🚨 <b>High Risk Token Detected</b>: <code>{symbol}</code> ({name})\n"
            f"👤 Creator: <code>{creator[:10]}...</code>\n"
            f"💧 LP: <b>{lp:.2f}</b> SOL  |  💸 MC: <b>${mc:,.0f}</b>  |  📊 Vol: <b>${vol:,.0f}</b>\n"
            f"🤛‍♂️ Holders: <b>{holders}</b>  |  🤖 Snipers: <b>{snipers}</b>  |  🔐 Dev: <b>{dev_hold:.1f}%</b>\n"
            f"⏱ Age: <b>{int(age)}</b> mins\n"
            f"<code>{nova_cmd}</code>\n"
        )

        if token_address != "???" and token_address:
            msg += f"<a href=\"https://neo.bulix.io/token/{token_address}\">View on Bulix</a>"

        print(f"📬 Sending alert for {symbol}")
        send_telegram_message(msg)

    # Bind to the event (update event name based on browser messages)
    channel.bind("token-supply-update", on_token_update)

    # Connect to Pusher
    try:
        pusher_client.connect()
        print("📡 Subscribing to new Pump Fun token creations...")
        # Keep the script running
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"❌ Error in subscription: {str(e)}")
    finally:
        pusher_client.disconnect()

# Basic snipe decision logic placeholder
def should_snipe(token_address):
    print(f"[🧠] Evaluating token: {token_address}")
    return True  # TODO: Replace with real LP, age, risk logic
