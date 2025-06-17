# Simple offline search engine
import os
import sys
import re
from collections import defaultdict, Counter

def tokenize(text):
    # Split on non-word characters
    return re.findall(r"\b\w+\b", text.lower())

def build_index(directory):
    index = defaultdict(Counter)
    documents = {}
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if os.path.isfile(path) and filename.endswith('.txt'):
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            tokens = tokenize(text)
            documents[filename] = tokens
            for token in tokens:
                index[token][filename] += 1
    return index, documents

def search(index, query_tokens):
    if not query_tokens:
        return []
    candidates = None
    for token in query_tokens:
        docs = set(index.get(token, []))
        if candidates is None:
            candidates = docs
        else:
            candidates &= docs
        if not candidates:
            break
    if not candidates:
        return []
    # Rank by sum of token counts
    ranked = []
    for doc in candidates:
        score = sum(index[token][doc] for token in query_tokens)
        ranked.append((score, doc))
    ranked.sort(reverse=True)
    return [doc for score, doc in ranked]

def main():
    if len(sys.argv) != 2:
        print('Usage: python search_engine.py <documents_directory>')
        sys.exit(1)
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: directory '{directory}' does not exist")
        sys.exit(1)
    index, _ = build_index(directory)
    print('Index built. Enter search queries (blank line to exit).')
    while True:
        query = input('> ').strip()
        if not query:
            break
        tokens = tokenize(query)
        results = search(index, tokens)
        if results:
            print('Results:')
            for doc in results:
                print(' -', doc)
        else:
            print('No results found.')

if __name__ == '__main__':
    main()
