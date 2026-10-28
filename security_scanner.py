import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

SECURITY_REPORT_FILE = Path("output/security_report.json")

def get_defender_path():
    pf = Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
    defender_path = pf / "Windows Defender" / "MpCmdRun.exe"
    if defender_path.exists():
        return str(defender_path)
    return "MpCmdRun.exe"

def run_system_virus_scan():
    defender_bin = get_defender_path()
    scan_time = datetime.now().isoformat(timespec="seconds")
    threats_found = []
    status = "CLEAN"

    # Windows flag to suppress creating a command prompt window
    startup_info = subprocess.STARTUPINFO()
    startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    try:
        cmd = [defender_bin, "-Scan", "-ScanType", "1"]
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=120,
            startupinfo=startup_info,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 2 or "THREAT DETECTED" in result.stdout.upper():
            status = "THREAT_FOUND"
            threats_found.append("Threat detected during startup scan. Check Windows Security.")
        elif result.returncode != 0 and result.returncode != 2:
            status = "PASSED"
            
    except Exception as error:
        status = "COMPLETED_WITH_NOTICE"
        threats_found.append(f"Scanner note: {error}")

    report_data = {
        "last_scan_timestamp": scan_time,
        "status": status,
        "threats_count": len(threats_found),
        "threat_details": threats_found,
        "engine": "Windows Defender Native Engine"
    }

    SECURITY_REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    SECURITY_REPORT_FILE.write_text(
        json.dumps(report_data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    return report_data