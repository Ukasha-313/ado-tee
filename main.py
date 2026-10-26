import sys
import subprocess
from pathlib import Path

def print_help():
    print("=" * 60)
    print("ADO-TEE: Automated Document Orchestrator & Task Extraction Engine")
    print("=" * 60)
    print("Usage:")
    print("  python main.py gui        - Launch the Desktop GUI")
    print("  python main.py background - Run the AI Background Service & Startup Scan")
    print("  python main.py scan       - Run a one-time folder scan")
    print("=" * 60)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)
        
    command = sys.argv[1].lower()
    
    if command == "gui":
        import tkinter as tk
        from ado_tee_gui import AdoTeeGUI
        root = tk.Tk()
        AdoTeeGUI(root)
        root.mainloop()
    elif command == "background":
        from ado_tee_background import run_startup_ai_scan, start_background_monitoring
        run_startup_ai_scan()
        start_background_monitoring()
    else:
        print(f"[ERROR] Unknown command: {command}")
        print_help()