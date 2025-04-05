# 🕵️‍♂️ DorkingAzza0x1a

> Advanced Search Engine Dorking Tool for Reconnaissance, crafted by [@azza0x1a](https://github.com/azza0x1a)

![banner](https://img.shields.io/badge/DorkingAzza0x1a-Active-blueviolet?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge)

---

## Features

1. Flexible Input Options
   - Can take a single domain, a specific dork, or a file containing multiple dorks
   - Automatically combines domain with dorks when both are provided
2. Multiple Search Engine Support
   - Google, Bing, DuckDuckGo, Yahoo, and Yandex
   - Option to search all engines simultaneously with --engine all
   - Bot detection avoidance through rotating user agents and configurable delays
3. Efficient Processing
   - Asynchronous requests with aiohttp for better performance
   - Progress bar to track scanning status
   - Duplicate URL filtering with the --no-duplicate option
4. URL Validation
   - Optional URL validation to ensure only active URLs are saved
   - Status code checking to filter out dead links
5. Flexible Output Options
   - Save results as JSON, CSV, or simple text files
   - JSON output includes full context (dork used, search engine, status code)
   - Ready for piping to other security tools

## Installation Requirements

Before running the tool, install the required dependencies:
pip install -r requirements.txt

## CLI Options:

usage: dorkingAzza0x1a.py [-h] [--domain DOMAIN] [--dork DORK] [--dork-file DORK_FILE]
[--engine {google,bing,duckduckgo,yahoo,yandex,all}]
[--output OUTPUT] [--validate] [--no-duplicate]
[--delay DELAY] [--timeout TIMEOUT]
[--max-pages MAX_PAGES] [--debug]

Options:
-h, --help Show help message and exit

Input Options:
--domain DOMAIN Target domain (e.g., example.com)
--dork DORK Single dork to search
--dork-file DORK_FILE File containing list of dorks

Search Engine Options:
--engine google | bing | duckduckgo | yahoo | yandex | all

Output Options:
--output OUTPUT Output file (.json, .csv, or .txt)
--validate Check if URLs are alive
--no-duplicate Remove duplicates in output

Advanced Options:
--delay DELAY Delay between requests (default: 2s)
--timeout TIMEOUT Request timeout (default: 10s)
--max-pages MAX_PAGES Max pages to fetch (default: 3)
--debug Enable debug logging

## Usage

### Basic usage with a dork file
python3 dorkingPRIB.py --dork-file payloads/SQLi/sqli1.txt --engine google --output results.json
### Target specific domain with dork file
python3 dorkingPRIB.py --domain kominfo.go.id --dork-file payloads/SQLi/sqli1.txt --engine all --output kominfo_sqli.json
### With advanced options
python3 dorkingPRIB.py --domain example.com --dork-file payloads/SQLi/sqli1.txt --engine google --output results.json --no-duplicate --delay 3 --timeout 10 --max-pages 5 --validate

⚠️ Disclaimer
This tool is made for educational and authorized security testing only. Any misuse is not the responsibility of the author.

👑 Author
Azza Tegar Naufal Ataullah
GitHub: @azza0x1a
Tool name: DorkingAzza0x1a
Tagline: Recon Strong. Dork Deep. 🔍

MIT License

```txt
MIT License

Copyright (c) 2025 Azza

Permission is hereby granted, free of charge, to any person obtaining a copy...
(full MIT text bisa auto generate di GitHub ya)
```
