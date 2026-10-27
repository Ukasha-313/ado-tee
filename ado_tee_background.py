"""
ADO-TEE Background AI Document & Security Agent

- Performs an AI-assisted startup scan and Windows virus check
- Automatically discovers safe user folders and available drives
- Monitors folders recursively in real-time
- Runs an automated threat scan on every new or downloaded file
- Classifies documents, summarizes content, and extracts deadlines
- Saves daily reports and a live background index
"""

import json
import time
from datetime import datetime
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ado_tee_scanner import (
    extract_text,
    calculate_hash
)

from ai_engine import AIEngine
from system_scanner import get_scan_roots
from security_scanner import run_system_virus_scan, scan_single_file

# Output locations
REPORT_FOLDER = Path("output/reports")
BACKGROUND_INDEX = Path("output/background_index.json")
LIVE_LOG = Path("output/background_log.txt")

# Files ADO-TEE should ignore
IGNORE_EXTENSIONS = {
    ".tmp", ".temp", ".part", ".crdownload", ".download",
    ".log", ".cache", ".pyc", ".dll", ".exe", ".msi",
    ".sys", ".bin", ".iso"
}

IGNORE_FILE_PREFIXES = (
    "~$", ".~", "._"
)

# Wait after detecting a file so browsers/downloads finish writing it
FILE_SETTLE_DELAY = 2


class AdoTeeAIFileHandler(FileSystemEventHandler):
    """Processes new and modified files in watched folders with automatic security checks."""

    def __init__(self, ai_engine):
        self.ai = ai_engine
        self.recent_events = {}

    def is_valid_file(self, file_path: Path):
        """Filter temporary, hidden, system, and oversized files."""
        try:
            if not file_path.is_file():
                return False

            name = file_path.name.lower()

            if name.startswith(IGNORE_FILE_PREFIXES):
                return False

            if file_path.suffix.lower() in IGNORE_EXTENSIONS:
                return False

            if file_path.stat().st_size > 50 * 1024 * 1024:
                return False

            return True

        except (PermissionError, OSError):
            return False

    def should_process(self, file_path: Path):
        """Avoid processing the same temporary file event repeatedly."""
        key = str(file_path)
        now = time.time()

        if key in self.recent_events and now - self.recent_events[key] < FILE_SETTLE_DELAY:
            return False

        self.recent_events[key] = now
        return True

    def on_created(self, event):
        if event.is_directory:
            return
        self.handle_file(Path(event.src_path), "CREATED")

    def on_modified(self, event):
        if event.is_directory:
            return
        self.handle_file(Path(event.src_path), "MODIFIED")

    def handle_file(self, file_path: Path, event_type: str):
        try:
            if not self.is_valid_file(file_path):
                return

            if not self.should_process(file_path):
                return

            # Give browsers/downloads a moment to finish writing.
            time.sleep(FILE_SETTLE_DELAY)

            if not file_path.exists():
                return

            print(f"[{event_type}] {file_path}")

            # 1. Automatically run virus/threat scan on the newly added or downloaded file
            scan_single_file(file_path)

            # 2. Extract text and perform AI task/deadline extraction
            text = extract_text(file_path)
            analysis = self.ai.analyze_document(file_path.name, text)
            file_hash = calculate_hash(file_path)

            record = {
                "detected_at": datetime.now().isoformat(timespec="seconds"),
                "event_type": event_type,
                "file_name": file_path.name,
                "full_path": str(file_path),
                "sha256": file_hash,
                "text_length": len(text),
                **analysis
            }

            self.save_to_daily_report(record)
            self.save_to_background_index(record)
            self.write_live_log(record)

            print(
                f"[AI SCANNED] {file_path.name} → "
                f"{record['category']} | "
                f"Priority: {record['priority']} | "
                f"Confidence: {record['ai_confidence']}"
            )

            for deadline in record.get("deadlines", []):
                print(
                    f"[DEADLINE] {deadline['task']} | "
                    f"Date: {deadline['detected_date']} | "
                    f"Priority: {deadline['priority']}"
                )

        except Exception as error:
            print(f"[ERROR] Failed to process {file_path}: {error}")

    def save_to_daily_report(self, record):
        """Append the processed file to today's report."""
        REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        report_file = REPORT_FOLDER / f"ado_tee_ai_report_{today}.json"

        if report_file.exists():
            report = json.loads(
                report_file.read_text(encoding="utf-8")
            )
        else:
            report = {
                "report_date": today,
                "total_files": 0,
                "total_deadlines": 0,
                "files": []
            }

        report["files"].append(record)
        report["total_files"] = len(report["files"])
        report["total_deadlines"] = sum(
            len(item.get("deadlines", []))
            for item in report["files"]
        )

        report_file.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def save_to_background_index(self, record):
        """Maintain one continuous index of detected files."""
        BACKGROUND_INDEX.parent.mkdir(parents=True, exist_ok=True)

        if BACKGROUND_INDEX.exists():
            index = json.loads(
                BACKGROUND_INDEX.read_text(encoding="utf-8")
            )
        else:
            index = {
                "project": "ADO-TEE",
                "files": []
            }

        index["files"].append(record)
        index["last_updated"] = datetime.now().isoformat(timespec="seconds")
        index["total_files"] = len(index["files"])

        BACKGROUND_INDEX.write_text(
            json.dumps(index, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    def write_live_log(self, record):
        """Keep a simple human-readable activity log."""
        LIVE_LOG.parent.mkdir(parents=True, exist_ok=True)

        log_line = (
            f"{record['detected_at']} | "
            f"{record['event_type']} | "
            f"{record['file_name']} | "
            f"{record['category']} | "
            f"Priority: {record['priority']}\n"
        )

        with open(LIVE_LOG, "a", encoding="utf-8") as log_file:
            log_file.write(log_line)


def run_startup_ai_scan():
    """Run automated system virus check and scan discovered folders once when the service starts."""
    print("=" * 70)
    print("ADO-TEE BACKGROUND SERVICE & SECURITY AGENT")
    print("=" * 70)
    
    # Run automatic system virus scan on startup / wake
    run_system_virus_scan()

    print("[STARTUP SCAN] Beginning AI-assisted system document scan...")

    ai = AIEngine()
    roots = get_scan_roots()
    all_records = []

    for root in roots:
        print(f"[SCANNING ROOT] {root}")

        try:
            from system_scanner import discover_files

            files = discover_files(root)

            for file_path in files:
                try:
                    text = extract_text(file_path)
                    analysis = ai.analyze_document(file_path.name, text)
                    file_hash = calculate_hash(file_path)

                    record = {
                        "scanned_at": datetime.now().isoformat(timespec="seconds"),
                        "file_name": file_path.name,
                        "full_path": str(file_path),
                        "sha256": file_hash,
                        "text_length": len(text),
                        **analysis
                    }

                    all_records.append(record)

                except Exception as error:
                    print(f"[ERROR] {file_path}: {error}")

        except Exception as error:
            print(f"[ERROR] Could not scan root {root}: {error}")

    REPORT_FOLDER.mkdir(parents=True, exist_ok=True)
    startup_report = REPORT_FOLDER / "startup_ai_report.json"

    startup_report.write_text(
        json.dumps(
            {
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "total_files": len(all_records),
                "total_deadlines": sum(
                    len(item.get("deadlines", []))
                    for item in all_records
                ),
                "files": all_records
            },
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(
        f"[STARTUP COMPLETE] Scanned {len(all_records)} files. "
        f"Report: {startup_report}"
    )


def start_background_monitoring():
    """Monitor all discovered folders continuously for new downloads and file changes."""
    ai = AIEngine()
    handler = AdoTeeAIFileHandler(ai)
    observer = Observer()

    roots = get_scan_roots()

    if not roots:
        print("[WARNING] No folders available to monitor.")
        return

    for folder in roots:
        try:
            observer.schedule(handler, str(folder), recursive=True)
            print(f"[WATCHING] {folder}")
        except Exception as error:
            print(f"[ERROR] Could not watch {folder}: {error}")

    observer.start()

    print("=" * 70)
    print("[ADO-TEE BACKGROUND & SECURITY SERVICE RUNNING]")
    print("New downloads and modified files will be security-scanned and AI-analyzed automatically.")
    print("Press Ctrl+C to stop.")
    print("=" * 70)

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down ADO-TEE background service...")
        observer.stop()

    observer.join()
    print("[STOPPED] ADO-TEE background service stopped.")


if __name__ == "__main__":
    run_startup_ai_scan()
    start_background_monitoring()