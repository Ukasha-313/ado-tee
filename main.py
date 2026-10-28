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

def launch_gui():
    import tkinter as tk
    from ado_tee_gui import AdoTeeGUI
    root = tk.Tk()
    AdoTeeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    # If launched with no arguments (e.g. double-clicked .exe), default to GUI
    if len(sys.argv) < 2:
        launch_gui()
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "gui":
        launch_gui()
    elif command == "background":
        from ado_tee_background import run_startup_ai_scan, start_background_monitoring
        run_startup_ai_scan()
        start_background_monitoring()
    elif command == "help" or command == "-h" or command == "--help":
        print_help()
    else:
        # Fallback to GUI if an unknown argument or launcher flag is passed
        launch_gui()