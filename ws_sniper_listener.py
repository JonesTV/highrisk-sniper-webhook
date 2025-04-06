
import websocket
import json

# This is the actual BullX WebSocket URL (replace if different)
WS_URL = "wss://stream4.bullx.io/app/prowess-frail-sensitive?protocol=7&client=js&version=8.4.0-rc2&flash=false"

# This is the Solana token channel we saw in DevTools
CHANNEL_NAME = "new-pairs2-1399811149"

def on_message(ws, message):
    try:
        msg = json.loads(message)
        if msg.get("event") == CHANNEL_NAME:
            print("🔔 New token event received:")
            print(json.dumps(msg["data"], indent=2))
    except Exception as e:
        print("⚠️ Error parsing message:", e)

def on_open(ws):
    print("✅ Connected to BullX WebSocket")

    subscribe_payload = {
        "event": "pusher:subscribe",
        "data": {
            "channel": CHANNEL_NAME
        }
    }

    ws.send(json.dumps(subscribe_payload))
    print(f"📡 Subscribed to channel: {CHANNEL_NAME}")

def on_error(ws, error):
    print("❌ WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 WebSocket Closed:", close_msg)

if __name__ == "__main__":
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
