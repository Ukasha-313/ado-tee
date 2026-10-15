"""
ADO-TEE: Automated Document Orchestrator & Task Extraction Engine
Scans a folder, extracts text, classifies files, detects duplicates,
and finds likely deadlines.
"""

import hashlib
import json
import mimetypes
import re
from datetime import datetime
from pathlib import Path

# Folder to scan. Change this if needed.
WATCH_ROOT = Path(r"D:\Admin\hacktober\test-files")

# Where the results will be saved.
OUTPUT_FILE = Path("output/file_index.json")

TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".py", ".js",
    ".html", ".css", ".log"
}

CATEGORY_RULES = {
    "Academic_Lecture_Notes": [
        "lecture", "course", "slides", "notes", "quiz",
        "assignment", "syllabus", "midterm", "exam"
    ],
    "Administrative_Challan": [
        "challan", "invoice", "receipt", "fee", "bill", "form"
    ],
    "Project_Code_Base": [
        ".py", ".js", ".java", ".cpp", ".ipynb",
        "requirements.txt", "package.json"
    ],
    "Personal_Financial": [
        "bank", "statement", "salary", "tax", "budget", "insurance"
    ]
}

DEADLINE_PATTERNS = [
    r"(?:due\s*(?:date|by)|deadline|submission\s*(?:date|deadline)|last\s*date)\s*[:\-]?\s*([^\n\r]{3,150})",
    r"(quiz\s*\d+|assignment\s*#?\s*\d+|lab\s*task\s*\d+|midterm|final\s*exam)[^\n\r]{0,180}"
]


def calculate_hash(file_path):
    """Create a SHA-256 hash to identify duplicate files."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def extract_text(file_path):
    """Extract readable text from supported files."""
    extension = file_path.suffix.lower()

    if extension in TEXT_EXTENSIONS:
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    if extension == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(file_path))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            return ""

    if extension == ".docx":
        try:
            from docx import Document
            document = Document(str(file_path))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        except Exception:
            return ""

    return ""


def classify_file(file_path, text):
    """Assign a simple category using filename and content keywords."""
    searchable_text = (
        str(file_path).lower() + " " + text[:5000].lower()
    )

    scores = {}

    for category, keywords in CATEGORY_RULES.items():
        score = 0
        for keyword in keywords:
            score += searchable_text.count(keyword.lower())
        scores[category] = score

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Uncategorized"

    return best_category


def extract_deadlines(text, file_path):
    """Find likely deadlines, quizzes, assignments, and exams."""
    deadlines = []

    for pattern in DEADLINE_PATTERNS:
        matches = re.finditer(pattern, text, re.IGNORECASE)

        for match in matches:
            snippet = " ".join(match.group(0).split())[:250]

            priority = "Medium"
            if re.search(r"today|tomorrow|due", snippet, re.IGNORECASE):
                priority = "High"

            deadlines.append({
                "task": snippet,
                "source_file": str(file_path),
                "priority": priority,
                "detected_at": datetime.now().isoformat(timespec="seconds")
            })

    return deadlines


def scan_folder(root_folder):
    """Scan every file in the selected folder."""
    files_index = []
    deadlines_index = []
    seen_hashes = {}

    if not root_folder.exists():
        print(f"Folder does not exist: {root_folder}")
        return files_index, deadlines_index

    for file_path in root_folder.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.name.startswith("."):
            continue

        try:
            file_hash = calculate_hash(file_path)
        except Exception:
            continue

        text = extract_text(file_path)
        category = classify_file(file_path, text)
        file_stat = file_path.stat()

        is_duplicate = file_hash in seen_hashes

        file_record = {
            "file_name": file_path.name,
            "full_path": str(file_path),
            "extension": file_path.suffix.lower(),
            "mime_type": mimetypes.guess_type(file_path.name)[0],
            "size_bytes": file_stat.st_size,
            "last_modified": datetime.fromtimestamp(
                file_stat.st_mtime
            ).isoformat(timespec="seconds"),
            "sha256": file_hash,
            "category": category,
            "suggested_folder": str(root_folder / category),
            "duplicate": is_duplicate,
            "duplicate_of": seen_hashes.get(file_hash),
            "extracted_text_length": len(text)
        }

        if not is_duplicate:
            seen_hashes[file_hash] = str(file_path)

        files_index.append(file_record)
        deadlines_index.extend(extract_deadlines(text, file_path))

    return files_index, deadlines_index


def save_results(files_index, deadlines_index):
    """Save the scan results into a JSON index."""
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    results = {
        "project": "ADO-TEE",
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "scanned_folder": str(WATCH_ROOT),
        "total_files": len(files_index),
        "total_deadlines_found": len(deadlines_index),
        "files": files_index,
        "deadlines": deadlines_index
    }

    OUTPUT_FILE.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def main():
    print("=" * 60)
    print("ADO-TEE: Document Intelligence Scanner")
    print("=" * 60)
    print(f"Scanning folder: {WATCH_ROOT}")

    files, deadlines = scan_folder(WATCH_ROOT)
    save_results(files, deadlines)

    print("-" * 60)
    print(f"Files indexed: {len(files)}")
    print(f"Potential deadlines found: {len(deadlines)}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()