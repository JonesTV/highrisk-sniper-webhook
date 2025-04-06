
import re

# ✅ Customize these:
TARGET_FILE = "index-BHlwYjrj.js"  # Replace with your filename
KEYWORDS = [
    "channel",
    "new-pairs2",
    "pusher",
    "subscribe",
    "event",
    "token",
    "lp",
    "mc",
    "websocket",
    "send",
    "receive"
]

def search_file(file_path, keywords):
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                for keyword in keywords:
                    if re.search(re.escape(keyword), line, re.IGNORECASE):
                        results.append((lineno, keyword, line.strip()))
        return results
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return []

if __name__ == "__main__":
    matches = search_file(TARGET_FILE, KEYWORDS)

    if matches:
        print(f"🔍 Found {len(matches)} matching lines in '{TARGET_FILE}':\n")
        for lineno, keyword, line in matches:
            print(f"📌 Line {lineno:5d} | Keyword: '{keyword}' → {line}")
    else:
        print("😶 No matches found.")

        # Save to file
with open("scanner_output.txt", "w", encoding="utf-8") as out:
    for lineno, keyword, line in matches:
        out.write(f"Line {lineno:5d} | Keyword: '{keyword}' → {line}\\n")

print("\\n📝 Saved results to scanner_output.txt")

