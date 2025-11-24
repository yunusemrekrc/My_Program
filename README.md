# My_Program

This repository contains a simple offline search engine implemented in Python.

## search_engine.py

```
usage: python search_engine.py [-k LIMIT] directory
```

The script recursively indexes all `.txt` files in the specified directory, builds a TF-IDF index, and lets you search for relevant documents. Queries are entered interactively; enter `:list` to see indexed files, `:quit` or a blank line to exit. Use `-k`/`--limit` to adjust how many results are shown (default 10).

Quick start example:

```bash
mkdir -p docs/notes
echo "hello world" > docs/example.txt
echo "another document about search" > docs/notes/search.txt
python3 search_engine.py docs
```
