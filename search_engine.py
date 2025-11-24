"""Offline TF-IDF search engine for local text files."""
from __future__ import annotations

import argparse
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import re


WORD_RE = re.compile(r"\b\w+\b")


def tokenize(text: str) -> List[str]:
    """Split a string into lowercase word tokens."""
    return WORD_RE.findall(text.lower())


@dataclass
class DocumentRecord:
    """Metadata and cached content for a document."""

    name: str
    path: Path
    preview: str


class SearchEngine:
    """Indexes `.txt` files and performs cosine-similarity search."""

    def __init__(self, directory: Path):
        self.directory = directory
        self.documents: Dict[Path, DocumentRecord] = {}
        self.term_idf: Dict[str, float] = {}
        self.doc_vectors: Dict[Path, Dict[str, float]] = {}
        self.doc_norms: Dict[Path, float] = {}

    def build_index(self) -> None:
        """Index every `.txt` file under ``directory`` recursively."""
        raw_term_counts: Dict[Path, Counter[str]] = {}
        document_frequency: Counter[str] = Counter()

        for path in sorted(self.directory.rglob("*.txt")):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            tokens = tokenize(text)
            if not tokens:
                continue

            counts = Counter(tokens)
            raw_term_counts[path] = counts
            document_frequency.update(counts.keys())
            preview = text.strip().splitlines()[0][:200] if text.strip() else ""
            self.documents[path] = DocumentRecord(name=path.name, path=path, preview=preview)

        num_docs = len(raw_term_counts)
        if num_docs == 0:
            return

        # Calculate IDF with smoothing to avoid division by zero.
        self.term_idf = {
            term: math.log((1 + num_docs) / (1 + freq)) + 1
            for term, freq in document_frequency.items()
        }

        for path, counts in raw_term_counts.items():
            doc_len = sum(counts.values())
            if doc_len == 0:
                continue

            vector: Dict[str, float] = {}
            for term, count in counts.items():
                tf = count / doc_len
                idf = self.term_idf.get(term, 0.0)
                vector[term] = tf * idf

            norm = math.sqrt(sum(weight * weight for weight in vector.values())) or 1e-9
            self.doc_vectors[path] = vector
            self.doc_norms[path] = norm

    def search(self, query: str, limit: int = 10) -> List[Tuple[DocumentRecord, float]]:
        """Search for a query string and return ranked results."""
        tokens = tokenize(query)
        if not tokens:
            return []
        if not self.doc_vectors:
            return []

        query_counts = Counter(tokens)
        query_len = sum(query_counts.values())
        query_vector: Dict[str, float] = {}
        for term, count in query_counts.items():
            idf = self.term_idf.get(term, 0.0)
            query_vector[term] = (count / query_len) * idf

        query_norm = math.sqrt(sum(weight * weight for weight in query_vector.values())) or 1e-9

        scores: List[Tuple[float, Path]] = []
        for path, doc_vector in self.doc_vectors.items():
            numerator = sum(query_vector.get(term, 0.0) * weight for term, weight in doc_vector.items())
            score = numerator / (self.doc_norms[path] * query_norm)
            if score > 0:
                scores.append((score, path))

        scores.sort(reverse=True)
        results = []
        for score, path in scores[:limit]:
            results.append((self.documents[path], score))
        return results

    def list_documents(self) -> List[DocumentRecord]:
        return [self.documents[path] for path in sorted(self.documents)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Offline TF-IDF search engine for text files")
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing .txt documents to index (searched recursively)",
    )
    parser.add_argument(
        "-k",
        "--limit",
        type=int,
        default=10,
        help="Number of results to return for each query",
    )
    return parser.parse_args()


def interactive_loop(engine: SearchEngine, limit: int) -> None:
    print("Index built. Enter search queries (blank line to exit).")
    print("Commands: :list to view indexed files, :quit to exit.")
    while True:
        query = input("> ").strip()
        if not query or query == ":quit":
            break
        if query == ":list":
            docs = engine.list_documents()
            if not docs:
                print("No documents indexed.")
            else:
                for doc in docs:
                    print(f" - {doc.name}")
            continue

        results = engine.search(query, limit=limit)
        if not results:
            print("No results found.")
            continue

        print("Results:")
        for doc, score in results:
            preview = f" — {doc.preview}" if doc.preview else ""
            print(f" - {doc.name} (score: {score:.3f}){preview}")


def main() -> None:
    args = parse_args()
    if not args.directory.exists() or not args.directory.is_dir():
        raise SystemExit(f"Error: directory '{args.directory}' does not exist or is not a directory")

    engine = SearchEngine(args.directory)
    engine.build_index()

    if not engine.documents:
        print("No .txt files found to index. Exiting.")
        return

    interactive_loop(engine, args.limit)


if __name__ == "__main__":
    main()
