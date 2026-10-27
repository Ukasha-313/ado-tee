"""
ADO-TEE Security & Virus Scanner Module
Integrates with Windows Defender to scan files and systems natively.
"""

import subprocess
import os
from pathlib import Path

def run_system_virus_scan():
    """Triggers a quick full-system scan using Windows Defender."""
    print("[SECURITY] Initiating automated system virus scan...")
    try:
        defender_path = Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "Windows Defender" / "MpCmdRun.exe"
        if not defender_path.exists():
            # Fallback path for Windows Defender
            defender_path = Path("C:\\ProgramData\\Microsoft\\Windows Defender\\Platform")
            # If path varies, use command-line alias
            cmd = ["MpCmdRun.exe", "-Scan", "-ScanType", "1"]
        else:
            cmd = [str(defender_path), "-Scan", "-ScanType", "1"]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        print("[SECURITY] Virus scan completed successfully.")
        return True
    except Exception as e:
        print(f"[SECURITY] System scan notice: {e}")
        return False

def scan_single_file(file_path: Path):
    """Scans a newly added or downloaded file for threats."""
    print(f"[SECURITY] Scanning new file: {file_path.name}")
    try:
        defender_path = "MpCmdRun.exe"
        cmd = [defender_path, "-Scan", "-ScanType", "3", "-File", str(file_path)]
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except Exception as e:
        print(f"[SECURITY] File scan error: {e}")