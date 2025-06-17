# My_Program

This repository contains a simple offline search engine implemented in Python.

## search_engine.py

```
usage: python search_engine.py <documents_directory>
```

The script indexes all `.txt` files in the specified directory and allows you to search for documents containing the query terms. Queries are entered interactively; entering a blank line exits the program.

Make sure the directory exists and contains some text files before running the script. For example:

```bash
mkdir docs
echo "hello world" > docs/example.txt
python3 search_engine.py docs
```
