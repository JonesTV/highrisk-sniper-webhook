
import re

# ✅ Customize these:
TARGET_FILE = "index-BHlwYjrj.js"  # Replace with your actual dev script filename
KEYWORDS = [
    r"\.subscribe\(",
    r"subscribe\(function",
    r"onmessage",
    r'on\("message"',
    r"channel",
    r"event",
    r"data",
    r"pusher"
]

def search_file(file_path, keywords):
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for lineno, line in enumerate(f, 1):
                for keyword in keywords:
                    if re.search(keyword, line, re.IGNORECASE):
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
        
        with open("refined_scan_output.txt", "w", encoding="utf-8") as out:
            for lineno, keyword, line in matches:
                out.write(f"Line {lineno:5d} | Keyword: '{keyword}' → {line}\n")
        print("\n📝 Saved results to refined_scan_output.txt")
    else:
        print("😶 No matches found.")
