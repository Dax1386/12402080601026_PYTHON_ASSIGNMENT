import os
import pickle
import zipfile
import sys
from collections import defaultdict

def build_index(folder_path, output_zip):
    inverted_index = defaultdict(list)
    total_files = 0
    total_lines = 0
    unique_tokens = set()

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.log') or file.endswith('.txt'):
                total_files += 1
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_no, line in enumerate(f, 1):
                        total_lines += 1
                        tokens = line.strip().lower().split()
                        for token in tokens:
                            unique_tokens.add(token)
                            inverted_index[token].append((file, line_no))

    # Pickle saving
    pickle_filename = "index.pkl"
    with open(pickle_filename, 'wb') as pf:
        pickle.dump(inverted_index, pf)

    # Creating ZIP Archive
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(pickle_filename)
        for root, _, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                zipf.write(filepath, os.path.relpath(filepath, folder_path))

    print(f"FILES {total_files}")
    print(f"LINES {total_lines}")
    print(f"TOKENS {len(unique_tokens)}")

def search_index(pickle_path, queries):
    with open(pickle_path, 'rb') as pf:
        index = pickle.load(pf)

    for q in queries:
        matches = index.get(q.lower(), [])
        res = [f"{fname}:{line}" for fname, line in matches]
        print(f"Query '{q}': " + ", ".join(res) if res else f"Query '{q}': No matches")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "BUILD":
        build_index("logs", "archive.zip")