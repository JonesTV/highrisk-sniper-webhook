import re

# File to scan
TARGET_FILE = "translation-CeOFwFqV.js"

# Keywords that hint at emitter/event relevance
KEYWORDS = [
    "event", "channel", "emit", "sniper", "wallet", "swap",
    "token", "buy", "sell", "created", "alert", "tx"
]

def extract_emitter_keywords(file_path, keywords):
    found = set()
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                matches = re.findall(r"['\"]([^'\"]+)['\"]", line)  # ✅ fixed regex
                for match in matches:
                    for keyword in keywords:
                        if keyword.lower() in match.lower():
                            found.add(match.strip())
        return sorted(found)
    except FileNotFoundError:
        print("❌ File not found:", file_path)
        return []

if __name__ == "__main__":
    results = extract_emitter_keywords(TARGET_FILE, KEYWORDS)

    if results:
        with open("emitter_keywords_output.txt", "w", encoding="utf-8") as out:
            for item in results:
                out.write(item + "\n")
        print(f"✅ Extracted {len(results)} keywords to emitter_keywords_output.txt")
    else:
        print("😶 No matching keywords found.")
