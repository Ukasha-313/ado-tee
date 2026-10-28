"""
ADO-TEE GUI Module — Next-Gen Cyber-Dark Dashboard
"""

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from ado_tee_scanner import OUTPUT_FILE, scan_folder
from security_scanner import SECURITY_REPORT_FILE, run_system_virus_scan


class AdoTeeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ADO-TEE — Document Intelligence & Threat Engine")
        self.root.geometry("1120x740")
        self.root.configure(bg="#0b132b")

        self.selected_folder = tk.StringVar(value=r"D:\Admin\hacktober\test-files")
        self.security_status_var = tk.StringVar(value="SYSTEM HEALTH: OPTIMAL")

        self.build_header()
        self.build_notebook()

        # Run automated startup virus check asynchronously
        threading.Thread(target=self.perform_startup_security_check, daemon=True).start()

    def build_header(self):
        header = tk.Frame(self.root, bg="#0b132b")
        header.pack(fill="x", padx=24, pady=(16, 8))

        # Brand Container
        brand_frame = tk.Frame(header, bg="#0b132b")
        brand_frame.pack(side="left", anchor="w")

        # Custom Logo Emblem
        logo_canvas = tk.Canvas(brand_frame, width=48, height=48, bg="#0b132b", highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 14))
        logo_canvas.create_oval(2, 2, 46, 46, outline="#38bdf8", width=2)
        logo_canvas.create_oval(10, 10, 38, 38, outline="#1d4ed8", width=1.5)
        logo_canvas.create_text(24, 24, text="A", fill="#38bdf8", font=("Segoe UI", 18, "bold"))

        text_frame = tk.Frame(brand_frame, bg="#0b132b")
        text_frame.pack(side="left", anchor="w")

        tk.Label(
            text_frame,
            text="ADO-TEE",
            font=("Segoe UI", 20, "bold"),
            fg="#38bdf8",
            bg="#0b132b"
        ).pack(anchor="w")

        tk.Label(
            text_frame,
            text="AUTOMATED DOCUMENT ORCHESTRATOR & TASK EXTRACTION ENGINE",
            font=("Segoe UI", 8, "bold"),
            fg="#64748b",
            bg="#0b132b"
        ).pack(anchor="w")

        # Security Status Indicator Card
        self.status_card = tk.Frame(header, bg="#1c2541", relief="flat")
        self.status_card.pack(side="right", anchor="e", ipadx=14, ipady=6)

        self.health_lbl = tk.Label(
            self.status_card,
            textvariable=self.security_status_var,
            font=("Segoe UI", 9, "bold"),
            fg="#22c55e",
            bg="#1c2541"
        )
        self.health_lbl.pack()

    def build_notebook(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#0b132b", borderwidth=0)
        style.configure(
            "TNotebook.Tab",
            background="#1c2541",
            foreground="#94a3b8",
            padding=[16, 8],
            font=("Segoe UI", 10, "bold"),
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#1e3a8a")],
            foreground=[("selected", "#38bdf8")]
        )

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=24, pady=(0, 16))

        # Tab 1: Live Scanner
        self.tab_scanner = tk.Frame(notebook, bg="#0b132b")
        notebook.add(self.tab_scanner, text="  🔍 Live Scanner  ")
        self.build_scanner_tab(self.tab_scanner)

        # Tab 2: Assignments & Deadlines Hub
        self.tab_assignments = tk.Frame(notebook, bg="#0b132b")
        notebook.add(self.tab_assignments, text="  📋 Assignments & Deadlines Hub  ")
        self.build_assignments_tab(self.tab_assignments)

        # Tab 3: Security & Virus Report
        self.tab_security = tk.Frame(notebook, bg="#0b132b")
        notebook.add(self.tab_security, text="  🛡️ Security & Threat Report  ")
        self.build_security_tab(self.tab_security)

    def build_scanner_tab(self, parent):
        controls = tk.Frame(parent, bg="#1c2541")
        controls.pack(fill="x", padx=4, pady=10, ipady=4)

        tk.Label(
            controls,
            text="TARGET DIRECTORY TO MONITOR & SCAN:",
            fg="#94a3b8",
            bg="#1c2541",
            font=("Segoe UI", 8, "bold")
        ).pack(anchor="w", padx=16, pady=(10, 4))

        row = tk.Frame(controls, bg="#1c2541")
        row.pack(fill="x", padx=16, pady=(0, 10))

        tk.Entry(
            row,
            textvariable=self.selected_folder,
            font=("Consolas", 10),
            bg="#0b132b",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat"
        ).pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 10))

        tk.Button(
            row, text="Browse", command=self.browse_folder,
            bg="#334155", fg="#ffffff", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=14, pady=4, cursor="hand2"
        ).pack(side="left", padx=4)

        tk.Button(
            row, text="Start Scan", command=self.start_scan,
            bg="#2563eb", fg="#ffffff", font=("Segoe UI", 9, "bold"),
            relief="flat", padx=16, pady=4, cursor="hand2"
        ).pack(side="left", padx=4)

        progress_frame = tk.Frame(parent, bg="#0b132b")
        progress_frame.pack(fill="x", padx=4, pady=4)

        self.status_label = tk.Label(
            progress_frame,
            text="Ready. Select target folder and initiate extraction.",
            fg="#94a3b8",
            bg="#0b132b",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(anchor="w")

        self.progress = ttk.Progressbar(progress_frame, mode="indeterminate", length=1000)
        self.progress.pack(fill="x", pady=6)

        self.stats_label = tk.Label(
            progress_frame,
            text="Files Scanned: 0 | Deadlines Extracted: 0",
            fg="#38bdf8",
            bg="#0b132b",
            font=("Segoe UI", 10, "bold")
        )
        self.stats_label.pack(anchor="w")

        results_frame = tk.Frame(parent, bg="#1c2541")
        results_frame.pack(fill="both", expand=True, padx=4, pady=10)

        tk.Label(
            results_frame,
            text="LIVE EXTRACTION LOG",
            fg="#e2e8f0",
            bg="#1c2541",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=16, pady=(10, 4))

        self.output_box = tk.Text(
            results_frame,
            bg="#0b132b",
            fg="#38bdf8",
            insertbackground="#e2e8f0",
            font=("Consolas", 9),
            relief="flat"
        )
        self.output_box.pack(fill="both", expand=True, padx=16, pady=(0, 14))

    def build_assignments_tab(self, parent):
        frame = tk.Frame(parent, bg="#1c2541")
        frame.pack(fill="both", expand=True, padx=4, pady=10)

        top_bar = tk.Frame(frame, bg="#1c2541")
        top_bar.pack(fill="x", padx=16, pady=12)

        tk.Label(
            top_bar,
            text="DETECTED LAB TASKS & ASSIGNMENT DEADLINES",
            fg="#38bdf8",
            bg="#1c2541",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", anchor="w")

        tk.Button(
            top_bar, text="🔄 Reload Index", command=self.load_deadlines_into_hub,
            bg="#334155", fg="#ffffff", font=("Segoe UI", 8, "bold"),
            relief="flat", padx=12, pady=4, cursor="hand2"
        ).pack(side="right", anchor="e")

        table_frame = tk.Frame(frame, bg="#0b132b")
        table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        columns = ("priority", "task", "date", "file_path")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=16)

        self.tree.heading("priority", text="PRIORITY")
        self.tree.heading("task", text="ASSIGNMENT / TASK DESCRIPTION")
        self.tree.heading("date", text="DUE DATE")
        self.tree.heading("file_path", text="FILE LOCATION (DOUBLE-CLICK TO OPEN)")

        self.tree.column("priority", width=110, anchor="center")
        self.tree.column("task", width=320, anchor="w")
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("file_path", width=460, anchor="w")

        style = ttk.Style()
        style.configure("Treeview", background="#0b132b", foreground="#e2e8f0", fieldbackground="#0b132b", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", background="#1c2541", foreground="#38bdf8", font=("Segoe UI", 9, "bold"))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.open_selected_file)
        self.load_deadlines_into_hub()

    def build_security_tab(self, parent):
        frame = tk.Frame(parent, bg="#1c2541")
        frame.pack(fill="both", expand=True, padx=4, pady=10)

        top_bar = tk.Frame(frame, bg="#1c2541")
        top_bar.pack(fill="x", padx=16, pady=12)

        tk.Label(
            top_bar,
            text="SYSTEM VIRUS & THREAT SCAN REPORT",
            fg="#38bdf8",
            bg="#1c2541",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", anchor="w")

        tk.Button(
            top_bar, text="⚡ Run Virus Scan Now", command=self.trigger_manual_virus_scan,
            bg="#2563eb", fg="#ffffff", font=("Segoe UI", 8, "bold"),
            relief="flat", padx=12, pady=4, cursor="hand2"
        ).pack(side="right", anchor="e")

        self.security_box = tk.Text(
            frame,
            bg="#0b132b",
            fg="#22c55e",
            insertbackground="#e2e8f0",
            font=("Consolas", 10),
            relief="flat"
        )
        self.security_box.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    def perform_startup_security_check(self):
        self.security_status_var.set("🛡️ RUNNING VIRUS SCAN...")
        report = run_system_virus_scan()
        self.root.after(0, self.update_security_ui, report)

    def trigger_manual_virus_scan(self):
        self.security_status_var.set("🛡️ SCANNING SYSTEM...")
        self.security_box.delete("1.0", "end")
        self.security_box.insert("end", "[SECURITY] Initiating manual threat scan via Windows Defender...\n")

        def task():
            report = run_system_virus_scan()
            self.root.after(0, self.update_security_ui, report)

        threading.Thread(target=task, daemon=True).start()

    def update_security_ui(self, report):
        status = report.get("status", "CLEAN")
        if status == "THREAT_FOUND":
            self.security_status_var.set("⚠️ THREAT DETECTED")
            self.health_lbl.config(fg="#ef4444")
        else:
            self.security_status_var.set("🛡️ SYSTEM HEALTH: OPTIMAL")
            self.health_lbl.config(fg="#22c55e")

        self.security_box.delete("1.0", "end")
        self.security_box.insert("end", f"LAST SCAN TIMESTAMP: {report.get('last_scan_timestamp', 'N/A')}\n")
        self.security_box.insert("end", f"SCAN ENGINE:         {report.get('engine', 'Native Defender')}\n")
        self.security_box.insert("end", f"OVERALL STATUS:      {status}\n")
        self.security_box.insert("end", f"THREATS FOUND:       {report.get('threats_count', 0)}\n")
        self.security_box.insert("end", "-" * 60 + "\n")

        if report.get("threat_details"):
            for threat in report["threat_details"]:
                self.security_box.insert("end", f"[WARNING] {threat}\n")
        else:
            self.security_box.insert("end", "[SUCCESS] Zero malicious threats or viruses detected on system.\n")

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder.set(folder)

    def log(self, message):
        self.output_box.insert("end", message + "\n")
        self.output_box.see("end")

    def start_scan(self):
        folder = Path(self.selected_folder.get())

        if not folder.exists():
            messagebox.showerror("Folder not found", f"This folder does not exist:\n{folder}")
            return

        self.output_box.delete("1.0", "end")
        self.progress.start(20)
        self.status_label.config(text="Scanning target files, parsing documents...", fg="#facc15")

        threading.Thread(target=self.run_scan, args=(folder,), daemon=True).start()

    def run_scan(self, folder):
        try:
            self.log(f"[START] Scanning target: {folder}")
            files, deadlines = scan_folder(folder)

            for file_record in files:
                status = "DUPLICATE" if file_record["duplicate"] else "SCANNED"
                self.log(f"[{status}] {file_record['file_name']} → {file_record['category']}")

            for deadline in deadlines:
                self.log(f"[DEADLINE] {deadline['task']} | Priority: {deadline['priority']}")

            OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
            result = {
                "project": "ADO-TEE",
                "scanned_folder": str(folder),
                "total_files": len(files),
                "total_deadlines_found": len(deadlines),
                "files": files,
                "deadlines": deadlines
            }

            OUTPUT_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            self.root.after(0, self.finish_scan, len(files), len(deadlines))

        except Exception as error:
            self.root.after(0, self.scan_failed, str(error))

    def finish_scan(self, file_count, deadline_count):
        self.progress.stop()
        self.status_label.config(text="Scan sequence completed.", fg="#22c55e")
        self.stats_label.config(text=f"Files Scanned: {file_count} | Deadlines Extracted: {deadline_count}")
        self.log("[DONE] Index saved to output/file_index.json")
        self.load_deadlines_into_hub()

    def scan_failed(self, error):
        self.progress.stop()
        self.status_label.config(text="Scan sequence failed.", fg="#ef4444")
        self.log(f"[ERROR] {error}")

    def load_deadlines_into_hub(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not OUTPUT_FILE.exists():
            return

        try:
            data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            file_path_map = {f["file_name"]: f["full_path"] for f in data.get("files", [])}

            for deadline in data.get("deadlines", []):
                file_name = deadline.get("file", "")
                full_path = file_path_map.get(file_name, "Path not found")

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        deadline.get("priority", "Medium"),
                        deadline.get("task", "Unknown Task"),
                        deadline.get("detected_date", "No Date"),
                        full_path
                    )
                )
        except Exception as e:
            print(f"[ERROR loading hub]: {e}")

    def open_selected_file(self, event):
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item_data = self.tree.item(selected_item)
        file_path = item_data["values"][3]

        if file_path and Path(file_path).exists():
            try:
                os.startfile(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
        else:
            messagebox.showwarning("File Missing", f"The file path does not exist:\n{file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    AdoTeeGUI(root)
    root.mainloop()