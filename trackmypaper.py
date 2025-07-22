import csv
import requests
import bibtexparser
from datetime import datetime
import re

# === CONFIGURATION ===
CSV_FILE = "papers.csv"
BIBTEX_FILE = "references.bib"

# === FUNCTIONS ===

def get_bibtex_from_doi(doi):
    """Fetch BibTeX entry using DOI."""
    headers = {"Accept": "application/x-bibtex"}
    url = f"https://doi.org/{doi}"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ Failed to fetch BibTeX for DOI {doi}: {response.status_code}")
            return None
    except Exception as e:
        print("⚠️ Error fetching BibTeX:", e)
        return None

def get_bibtex_from_arxiv(arxiv_id):
    """Fetch BibTeX entry from arXiv ID."""
    url = f"https://export.arxiv.org/bibtex/{arxiv_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            print(f"❌ Failed to fetch BibTeX for arXiv ID {arxiv_id}: {response.status_code}")
            return None
    except Exception as e:
        print("⚠️ Error fetching arXiv BibTeX:", e)
        return None

def extract_doi(link):
    """Try to extract DOI from a link."""
    if "doi.org" in link:
        return link.split("doi.org/")[-1]
    return None

def extract_arxiv_id(link):
    """Try to extract arXiv ID from link or ID string."""
    match = re.search(r'arxiv[:/]?(\d{4}\.\d+)(v\d+)?', link, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def save_bibtex_entry(entry):
    """Append BibTeX entry to references.bib."""
    with open(BIBTEX_FILE, "a", encoding="utf-8") as f:
        f.write(entry.strip() + "\n\n")

def add_to_csv(entry):
    """Append paper info to CSV."""
    file_exists = False
    try:
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["title", "link", "summary", "tags", "bibtex_key", "date_read"])
        writer.writerow(entry)

# === MAIN INTERACTION ===

print("📚 Add a New Paper")
title = input("Title: ").strip()
link = input("Link (DOI, ArXiv, or publisher): ").strip()
summary = input("1-line Summary: ").strip()
tags = input("Tags (comma-separated): ").strip()
date_read = datetime.now().strftime("%Y-%m-%d")

bibtex_entry = None
bibtex_key = ""

# Try DOI
doi = extract_doi(link)
if doi:
    bibtex_entry = get_bibtex_from_doi(doi)

# Try arXiv
if not bibtex_entry:
    arxiv_id = extract_arxiv_id(link)
    if arxiv_id:
        bibtex_entry = get_bibtex_from_arxiv(arxiv_id)

# Extract key and save BibTeX
if bibtex_entry:
    parser = bibtexparser.loads(bibtex_entry)
    if parser.entries:
        bibtex_key = parser.entries[0].get("ID", "")
        save_bibtex_entry(bibtex_entry)
    else:
        print("⚠️ BibTeX found, but couldn't parse entry ID.")

# Save to CSV
add_to_csv([title, link, summary, tags, bibtex_key, date_read])

print("\n✅ Paper saved!")
if bibtex_key:
    print(f"🔖 BibTeX key: {bibtex_key}")
