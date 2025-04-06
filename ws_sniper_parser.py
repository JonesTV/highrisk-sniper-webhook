
import websocket
import json
import threading
import time

WS_URL = "wss://stream4.bullx.io/app/prowess-frail-sensitive?protocol=7&client=js&version=8.4.0-rc2&flash=false"
CHANNEL_NAME = "new-pairs2-1399811149"

def parse_token_event(raw_data):
    try:
        parsed_outer = json.loads(raw_data)
        if isinstance(parsed_outer, list):
            for entry in parsed_outer:
                token_info = entry.get("t", {})
                print("\n🧪 Token Drop Detected!")
                print(f"Name: {token_info.get('n')}")
                print(f"Symbol: {token_info.get('s')}")
                print(f"Token Address: {token_info.get('a')}")
                print(f"DEX: {token_info.get('dx')}")
                print(f"LP: ${token_info.get('lp')} | MC: ${token_info.get('mc')}")
                print(f"Buy Tax: {token_info.get('bt')}% | Sell Tax: {token_info.get('st')}%")
                print(f"Holders: {token_info.get('h')}, Renounced: {token_info.get('renounced')}, Honeypot: {token_info.get('hp')}")
                print(f"🔗 Link: https://dexscreener.com/solana/{token_info.get('a')}")
    except Exception as e:
        print("⚠️ Failed to parse token data:", e)

def on_message(ws, message):
    try:
        msg = json.loads(message)
        if msg.get("event") == CHANNEL_NAME:
            raw_data = msg.get("data", "")
            parse_token_event(raw_data)
    except Exception as e:
        print("⚠️ Error handling message:", e)

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

    def send_heartbeat():
        while True:
            time.sleep(25)
            try:
                ws.send(json.dumps({"event": "pusher:ping", "data": {}}))
                print("💓 Sent heartbeat ping")
            except:
                break

    threading.Thread(target=send_heartbeat, daemon=True).start()

def on_error(ws, error):
    print("❌ WebSocket Error:", error)

def on_close(ws, close_status_code, close_msg):
    print("🔌 WebSocket Closed:", close_msg)

if __name__ == "__main__":
    websocket.enableTrace(False)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Origin": "https://neo.bullx.io"
    }
    ws = websocket.WebSocketApp(
        WS_URL,
        header=[f"{k}: {v}" for k, v in headers.items()],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
