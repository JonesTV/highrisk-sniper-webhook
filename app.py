from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/helius_listener', methods=['POST'])
def helius_listener():
    try:
        data = request.get_json(force=True)
        print(f"✅ Received payload: {type(data)}\n{data}")

        # Detect structure
        if isinstance(data, dict) and "transactions" in data:
            transactions = data["transactions"]
        elif isinstance(data, list):
            transactions = data
        else:
            print(f"[x] Unexpected payload format: {type(data)}")
            return jsonify({"error": "Invalid format"}), 400

        # Flatten nested lists if needed
        flattened = []
        for item in transactions:
            if isinstance(item, list):
                flattened.extend(item)
            else:
                flattened.append(item)

        for i, tx in enumerate(flattened):
            print(f"--- TX #{i+1} ---")
            if not isinstance(tx, dict):
                print(f"[x] Skipping non-dict tx: {tx}")
                continue

            events = tx.get("events", {})
            tokens = events.get("token", [])
            if isinstance(tokens, list):
                for t in tokens:
                    mint = t.get("mint")
                    if mint:
                        print(f"✅ Found token mint: {mint}")

        return jsonify({"status": "OK"}), 200

    except Exception as e:
        print(f"[🔥] Crash in webhook: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
