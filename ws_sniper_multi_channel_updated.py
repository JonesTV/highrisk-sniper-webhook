import websocket
import threading
import json
import time

BULLX_SOCKET_URL = "wss://stream4.bullx.io/app/prowess-frail-sensitive?protocol=7&client=js&version=8.4.0"
CHANNELS = [
    "new-pairs2-1399811149",
    "new-pairs2-1399811149-m",
    "new-pairs2-728126428",
    "new-pairs2-728126428-m",
    "walletWiseSwaps"
]

EMITTER_KEYWORDS = [
    "newPairs", "findLatestTokens", "newCreations", "created",
    "tokenWithAddress", "tokenSniper", "token", "txns", "txnsFrom",
    "buy", "sell", "snipers", "snipeBuy", "snipeSell", "alerts",
    "alert", "priceChangeAlert", "setAlert", "walletUpdate", "wallets",
    "walletDiscovery", "walletManager", "walletTracker",
    "trades", "tradingActivity", "activeTokenOrder", "activeTokenOrders"
]

def on_message(ws, message):
    try:
        data = json.loads(message)
        event = data.get("event", "")
        if any(keyword in event.lower() for keyword in EMITTER_KEYWORDS):
            print(f"🚀 Matched Event: {event}")
            print("📦 Payload:", json.dumps(data, indent=2))
    except Exception as e:
        print("⚠️ Failed to parse message:", e)

def on_open(ws):
    print("✅ Connected to BullX WebSocket")
    for channel in CHANNELS:
        payload = {
            "event": "pusher:subscribe",
            "data": {
                "channel": channel
            }
        }
        ws.send(json.dumps(payload))
        print(f"📡 Subscribed to channel: {channel}")

def send_heartbeat(ws):
    while True:
        if ws.sock and ws.sock.connected:
            ws.send(json.dumps({"event": "pusher:ping", "data": {}}))
            print("💗 Sent heartbeat ping")
        else:
            print("🔌 WebSocket closed. Skipping heartbeat.")
            break
        time.sleep(30)

def run_ws():
    ws = websocket.WebSocketApp(
        BULLX_SOCKET_URL,
        on_message=on_message,
        on_open=on_open
    )
    heartbeat = threading.Thread(target=send_heartbeat, args=(ws,))
    heartbeat.daemon = True
    heartbeat.start()
    ws.run_forever()

if __name__ == "__main__":
    run_ws()
