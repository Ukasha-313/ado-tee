import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from ado_tee_scanner import scan_folder, OUTPUT_FILE


class AdoTeeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ADO-TEE — Document Intelligence Scanner")
        self.root.geometry("900x620")
        self.root.configure(bg="#0f172a")

        self.selected_folder = tk.StringVar(
            value=r"D:\Admin\hacktober\test-files"
        )

        self.build_header()
        self.build_controls()
        self.build_progress()
        self.build_results()

    def build_header(self):
        header = tk.Frame(self.root, bg="#0f172a")
        header.pack(fill="x", padx=20, pady=18)

        tk.Label(
            header,
            text="ADO-TEE",
            font=("Segoe UI", 24, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Automated Document Orchestrator & Task Extraction Engine",
            font=("Segoe UI", 11),
            fg="#cbd5e1",
            bg="#0f172a"
        ).pack(anchor="w")

    def build_controls(self):
        controls = tk.Frame(self.root, bg="#1e293b")
        controls.pack(fill="x", padx=20, pady=10)

        tk.Label(
            controls,
            text="Folder to scan:",
            fg="#e2e8f0",
            bg="#1e293b",
            font=("Segoe UI", 10)
        ).pack(anchor="w", padx=12, pady=(12, 4))

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
        ).pack(side="left", fill="x", expand=True, ipady=7)

        ttk.Button(
            row,
            text="Browse",
            command=self.browse_folder
        ).pack(side="left", padx=8)

        ttk.Button(
            row,
            text="Start Scan",
            command=self.start_scan
        ).pack(side="left")

    def build_progress(self):
        progress_frame = tk.Frame(self.root, bg="#0f172a")
        progress_frame.pack(fill="x", padx=20, pady=10)

        self.status_label = tk.Label(
            progress_frame,
            text="Ready. Select a folder and start scanning.",
            fg="#94a3b8",
            bg="#0f172a",
            font=("Segoe UI", 10)
        )
        self.status_label.pack(anchor="w")

        self.progress = ttk.Progressbar(
            progress_frame,
            mode="indeterminate",
            length=860
        )
        self.progress.pack(fill="x", pady=8)

        self.stats_label = tk.Label(
            progress_frame,
            text="Files scanned: 0 | Deadlines found: 0",
            fg="#38bdf8",
            bg="#0f172a",
            font=("Segoe UI", 10, "bold")
        )
        self.stats_label.pack(anchor="w")

    def build_results(self):
        results_frame = tk.Frame(self.root, bg="#0f172a")
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(
            results_frame,
            text="Live scan log and detected deadlines",
            fg="#e2e8f0",
            bg="#0f172a",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=(0, 6))

        self.output_box = tk.Text(
            results_frame,
            bg="#020617",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            font=("Consolas", 10),
            relief="flat",
            height=18
        )
        self.output_box.pack(fill="both", expand=True)

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
            messagebox.showerror(
                "Folder not found",
                f"This folder does not exist:\n{folder}"
            )
            return

        self.output_box.delete("1.0", "end")
        self.progress.start(20)
        self.status_label.config(
            text="Scanning files, extracting text, checking duplicates...",
            fg="#facc15"
        )

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

                self.log(
                    f"[{status}] {file_record['file_name']} "
                    f"→ {file_record['category']}"
                )

            for deadline in deadlines:
                self.log(
                    f"[DEADLINE] {deadline['task']} "
                    f"| Priority: {deadline['priority']}"
                )

            OUTPUT_FILE.parent.mkdir(exist_ok=True)

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

            self.root.after(
                0,
                self.finish_scan,
                len(files),
                len(deadlines)
            )

        except Exception as error:
            self.root.after(
                0,
                self.scan_failed,
                str(error)
            )

    def finish_scan(self, file_count, deadline_count):
        self.progress.stop()
        self.status_label.config(
            text="Scan complete.",
            fg="#22c55e"
        )
        self.stats_label.config(
            text=f"Files scanned: {file_count} | Deadlines found: {deadline_count}"
        )
        self.log("[DONE] Results saved to output/file_index.json")

    def scan_failed(self, error):
        self.progress.stop()
        self.status_label.config(
            text="Scan failed.",
            fg="#ef4444"
        )
        self.log(f"[ERROR] {error}")


if __name__ == "__main__":
    root = tk.Tk()
    AdoTeeGUI(root)
    root.mainloop()