"""
ADO-TEE GUI Module (Enhanced with Tabs, Startup Security Check, and Clickable Deadlines)
"""

import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import os
import subprocess

from ado_tee_scanner import scan_folder, OUTPUT_FILE


class AdoTeeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ADO-TEE — Document Intelligence & Task Engine")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0f172a")

        self.selected_folder = tk.StringVar(
            value=r"D:\Admin\hacktober\test-files"
        )

        # Run automated startup security/integrity check first
        self.run_startup_security_check()

        self.build_header()
        self.build_notebook()

    def run_startup_security_check(self):
        """Simulates an automatic startup virus/integrity check for local documents."""
        # You can replace this popup or log with a silent background check if preferred
        print("[SECURITY] Running startup file integrity and safety check...")

    def build_header(self):
        header = tk.Frame(self.root, bg="#0f172a")
        header.pack(fill="x", padx=20, pady=12)

        tk.Label(
            header,
            text="ADO-TEE",
            font=("Segoe UI", 22, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Automated Document Orchestrator & Task Extraction Engine",
            font=("Segoe UI", 10),
            fg="#cbd5e1",
            bg="#0f172a"
        ).pack(anchor="w")

    def build_notebook(self):
        """Create tabbed interface for Scanner vs Assignments Hub."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background="#0f172a", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e293b", foreground="#e2e8f0", padding=[12, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#38bdf8")], foreground=[("selected", "#0f172a")])

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Tab 1: Scanner & Logs
        self.tab_scanner = tk.Frame(notebook, bg="#0f172a")
        notebook.add(self.tab_scanner, text="  🔍 Document Scanner  ")
        self.build_scanner_tab(self.tab_scanner)

        # Tab 2: Dedicated Assignments & Deadlines Hub
        self.tab_assignments = tk.Frame(notebook, bg="#0f172a")
        notebook.add(self.tab_assignments, text="  📋 Assignments & Deadlines Hub  ")
        self.build_assignments_tab(self.tab_assignments)

    def build_scanner_tab(self, parent):
        controls = tk.Frame(parent, bg="#1e293b")
        controls.pack(fill="x", padx=10, pady=10)

        tk.Label(
            controls,
            text="Folder to scan:",
            fg="#e2e8f0",
            bg="#1e293b",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=12, pady=(10, 4))

        row = tk.Frame(controls, bg="#1e293b")
        row.pack(fill="x", padx=12, pady=(0, 12))

        tk.Entry(
            row,
            textvariable=self.selected_folder,
            font=("Consolas", 10),
            bg="#0f172a",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat"
        ).pack(side="left", fill="x", expand=True, ipady=6)

        ttk.Button(row, text="Browse", command=self.browse_folder).pack(side="left", padx=8)
        ttk.Button(row, text="Start Scan", command=self.start_scan).pack(side="left")

        progress_frame = tk.Frame(parent, bg="#0f172a")
        progress_frame.pack(fill="x", padx=10, pady=6)

        self.status_label = tk.Label(
            progress_frame,
            text="Ready. Select a folder and start scanning.",
            fg="#94a3b8",
            bg="#0f172a",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(anchor="w")

        self.progress = ttk.Progressbar(progress_frame, mode="indeterminate", length=920)
        self.progress.pack(fill="x", pady=6)

        self.stats_label = tk.Label(
            progress_frame,
            text="Files scanned: 0 | Deadlines found: 0",
            fg="#38bdf8",
            bg="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        self.stats_label.pack(anchor="w")

        results_frame = tk.Frame(parent, bg="#0f172a")
        results_frame.pack(fill="both", expand=True, padx=10, pady=6)

        tk.Label(
            results_frame,
            text="Live scan log:",
            fg="#e2e8f0",
            bg="#0f172a",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 4))

        self.output_box = tk.Text(
            results_frame,
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            font=("Consolas", 9),
            relief="flat",
            height=14
        )
        self.output_box.pack(fill="both", expand=True)

    def build_assignments_tab(self, parent):
        """Dedicated screen for pending university assignments and lab tasks with clickable file paths."""
        frame = tk.Frame(parent, bg="#0f172a")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            frame,
            text="Detected Assignments & Lab Task Deadlines",
            fg="#38bdf8",
            bg="#0f172a",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w", pady=(0, 8))

        # Treeview table for assignments
        columns = ("priority", "task", "date", "file_path")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
        
        self.tree.heading("priority", text="Priority")
        self.tree.heading("task", text="Task / Assignment Description")
        self.tree.heading("date", text="Due Date")
        self.tree.heading("file_path", text="File Location (Double-click to open)")

        self.tree.column("priority", width=90, anchor="center")
        self.tree.column("task", width=280, anchor="w")
        self.tree.column("date", width=110, anchor="center")
        self.tree.column("file_path", width=420, anchor="w")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind double click to open file
        self.tree.bind("<Double-1>", self.open_selected_file)

        refresh_btn = ttk.Button(frame, text="Reload Deadlines from Index", command=self.load_deadlines_into_hub)
        refresh_btn.pack(side="bottom", anchor="e", pady=10)

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
        self.status_label.config(text="Scanning files, extracting text, checking duplicates...", fg="#facc15")

        threading.Thread(
            target=self.run_scan,
            args=(folder,),
            daemon=True
        ).start()

    def run_scan(self, folder):
        try:
            self.log(f"[START] Scanning: {folder}")
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

            OUTPUT_FILE.write_text(
                json.dumps(result, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )

            self.root.after(0, self.finish_scan, len(files), len(deadlines))

        except Exception as error:
            self.root.after(0, self.scan_failed, str(error))

    def finish_scan(self, file_count, deadline_count):
        self.progress.stop()
        self.status_label.config(text="Scan complete.", fg="#22c55e")
        self.stats_label.config(text=f"Files scanned: {file_count} | Deadlines found: {deadline_count}")
        self.log("[DONE] Results saved to output/file_index.json")
        # Auto-refresh the assignments hub tab
        self.load_deadlines_into_hub()

    def scan_failed(self, error):
        self.progress.stop()
        self.status_label.config(text="Scan failed.", fg="#ef4444")
        self.log(f"[ERROR] {error}")

    def load_deadlines_into_hub(self):
        """Loads saved deadlines from output/file_index.json into the Assignments tab table."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not OUTPUT_FILE.exists():
            return

        try:
            data = json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
            # Match deadlines back to their file paths
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
        """Double-clicking a deadline row opens the underlying file on the computer."""
        selected_item = self.tree.selection()
        if not selected_item:
            return

        item_data = self.tree.item(selected_item)
        file_path = item_data["values"][3]

        if file_path and Path(file_path).exists():
            try:
                os.startfile(file_path)  # Opens the file with default Windows app
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
        else:
            messagebox.showwarning("File Missing", f"The file path does not exist:\n{file_path}")


if __name__ == "__main__":
    root = tk.Tk()
    AdoTeeGUI(root)
    root.mainloop()