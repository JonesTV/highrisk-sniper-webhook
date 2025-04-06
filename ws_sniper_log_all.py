import websocket
import json
import time

# Load emitter keywords from file (generated earlier)
with open("emitter_keywords_output.txt", "r", encoding="utf-8") as f:
    EMITTER_KEYWORDS = [line.strip() for line in f if line.strip()]

# BullX WebSocket setup
BULLX_SOCKET_URL = "wss://socket-neo.bullx.io/socket.io/?EIO=4&transport=websocket"

CHANNELS = [
    "new-pairs2-1399811149",
    "new-pairs2-1399811149-m",
    "new-pairs2-728126428",
    "new-pairs2-728126428-m",
    "walletWiseSwaps"
]

def on_message(ws, message):
    try:
        data = json.loads(message)
        payload = json.dumps(data, indent=2)

        for keyword in EMITTER_KEYWORDS:
            if keyword.lower() in payload.lower():
                print("\n📦 Matched keyword:", keyword)
                print("🧠 EVENT:", data.get("event", "N/A"))
                print("📡 CHANNEL:", data.get("channel", "N/A"))
                print("🔍 DATA:\n", payload)
                print("=" * 40)
                break  # only log first match
    except Exception as e:
        print(f"❌ Failed to parse message: {e}\n{message}")

def on_open(ws):
    print("✅ Connected to BullX WebSocket")
    for channel in CHANNELS:
        subscribe_msg = {
            "event": "pusher:subscribe",
            "data": {"channel": channel}
        }
        ws.send(json.dumps(subscribe_msg))
        print(f"🔔 Subscribed to: {channel}")

def run_ws():
    ws = websocket.WebSocketApp(
        BULLX_SOCKET_URL,
        on_message=on_message,
        on_open=on_open
    )
    try:
        print("📡 Listening for emitter-related messages...\n")
        ws.run_forever()
    except KeyboardInterrupt:
        print("\n👋 Exiting gracefully.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    run_ws()
