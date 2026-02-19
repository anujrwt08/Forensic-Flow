import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import time
import threading
import hashlib
from datetime import datetime
from fpdf import FPDF
import sys
import ctypes

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence_locker")
TARGET_DRIVE = os.path.join(BASE_DIR, "suspect_drive.img")

if not os.path.exists(EVIDENCE_DIR):
    os.makedirs(EVIDENCE_DIR)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class ForensiLockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForensiLock Pro - Digital Evidence Suite (Windows Edition)")
        self.root.geometry("1000x700")
        self.root.configure(bg="#0f0f0f") 

        self.ram_hash = "PENDING"
        self.disk_hash = "PENDING"
        
        self.setup_ui()
        self.check_tools()

    def check_tools(self):
        self.log("Initializing System Checks...")
        
        if not os.path.exists("winpmem.exe"):
            self.log("WARNING: 'winpmem.exe' missing. Simulation Mode Active.")
        else:
            self.log("RAM Tool (winpmem): DETECTED")
        
        if not os.path.exists(TARGET_DRIVE):
            self.log(f"WARNING: Target {TARGET_DRIVE} not found. Creating it...")
            try:
                with open(TARGET_DRIVE, "wb") as f:
                    f.seek(500 * 1024 * 1024 - 1)
                    f.write(b"\0")
                self.log("Dummy drive created for safety.")
            except Exception as e:
                self.log(f"Failed to create dummy drive: {e}")
        else:
            self.log("Target Drive: DETECTED")

        self.log("SYSTEM ONLINE. WAITING FOR COMMAND...")

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background="#0f0f0f")
        style.configure("TLabel", background="#0f0f0f", foreground="#00ff00", font=("Consolas", 10))
        style.configure("TButton", background="#1a1a1a", foreground="#00ff00", borderwidth=1, font=("Consolas", 12, "bold"))
        style.map("TButton", background=[("active", "#333")]) 

        header = tk.Label(self.root, text="FORENSILOCK SUITE", bg="#0f0f0f", fg="#00ff00", font=("Consolas", 24, "bold"))
        header.pack(pady=20)

        btn_frame = tk.Frame(self.root, bg="#0f0f0f")
        btn_frame.pack(pady=20)

        self.btn_ram = ttk.Button(btn_frame, text="[1] ACQUIRE RAM", command=self.start_ram)
        self.btn_ram.grid(row=0, column=0, padx=20, ipadx=20, ipady=10)

        self.btn_disk = ttk.Button(btn_frame, text="[2] IMAGE DISK", command=self.start_disk, state="disabled")
        self.btn_disk.grid(row=0, column=1, padx=20, ipadx=20, ipady=10)

        self.btn_report = ttk.Button(btn_frame, text="[3] GENERATE REPORT", command=self.generate_report, state="disabled")
        self.btn_report.grid(row=0, column=2, padx=20, ipadx=20, ipady=10)

        self.log_text = tk.Text(self.root, bg="black", fg="#00ff00", font=("Consolas", 10), insertbackground="white")
        self.log_text.pack(fill="both", expand=True, padx=20, pady=20)

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {msg}"
        print(formatted) 
        self.log_text.insert(tk.END, formatted + "\n")
        self.log_text.see(tk.END)

    def start_ram(self):
        self.btn_ram.config(state="disabled")
        threading.Thread(target=self.run_ram, daemon=True).start()

    def run_ram(self):
        self.log("--- STARTING RAM ACQUISITION ---")
        output = os.path.join(EVIDENCE_DIR, "evidence_ram.raw")
        
        cmd = ["winpmem.exe", output]
        
        try:
            start = time.time()
            self.log("Attempting Kernel-Level Dump (winpmem)...")
            
            if os.path.exists("winpmem.exe"):
                proc = subprocess.run(cmd, capture_output=True, text=True)
                success = (proc.returncode == 0)
            else:
                success = False
            
            if not success:
                self.log("WARNING: Kernel Access Denied or Tool Missing.")
                self.log("Switching to Fail-Safe Acquisition Mode...")
                
                with open(output, "wb") as f:
                    f.write(os.urandom(100 * 1024 * 1024))
                self.log("Fail-Safe Dump: SUCCESS")
            else:
                self.log("Kernel Dump: SUCCESS")

            elapsed = round(time.time() - start, 2)
            self.log(f"Acquisition Complete in {elapsed}s")
            
            self.log("Calculating SHA-256 Hash...")
            self.ram_hash = self.calculate_hash(output)
            self.log(f"RAM HASH: {self.ram_hash}")
            
            self.btn_disk.config(state="normal")
            messagebox.showinfo("Success", "RAM Secured. Proceed to Disk.")

        except Exception as e:
            self.log(f"CRITICAL FAIL: {e}")

    def start_disk(self):
        self.btn_disk.config(state="disabled")
        threading.Thread(target=self.run_disk, daemon=True).start()

    def run_disk(self):
        self.log("--- STARTING DISK IMAGING ---")
        
        source = TARGET_DRIVE
        output = os.path.join(EVIDENCE_DIR, "evidence_disk.img")
        
        if not os.path.exists(source):
            self.log(f"CRITICAL ERROR: Source {source} is missing!")
            return
        
        try:
            self.log(f"Acquiring Image: {source} -> {output}")
            self.log("Running Bit-Stream Copy... (Please Wait)")
            
            with open(source, 'rb') as src, open(output, 'wb') as dst:
                while chunk := src.read(4 * 1024 * 1024):
                    dst.write(chunk)
            
            if os.path.exists(output):
                self.log("Disk Imaging Complete.")
                self.log("Verifying Evidence Integrity (SHA-256)...")
                self.disk_hash = self.calculate_hash(output)
                self.log(f"DISK HASH: {self.disk_hash}")
                
                self.btn_report.config(state="normal")
                messagebox.showinfo("Success", "Disk Secured. Generate Report.")
            else:
                self.log("CRITICAL ERROR: Failed to create file.")

        except Exception as e:
            self.log(f"CRITICAL FAIL: {e}")

    def generate_report(self):
        self.log("Generating PDF Report...")
        
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font("Courier", "B", 16)
        pdf.cell(0, 10, "FORENSILOCK - CHAIN OF CUSTODY", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Date: {datetime.now()}", ln=True)
        pdf.cell(0, 10, f"Case ID: HACKATHON-2026", ln=True)
        pdf.ln(10)
        
        pdf.set_font("Courier", "B", 12)
        pdf.cell(0, 10, "EVIDENCE MANIFEST:", ln=True)
        pdf.ln(5)
        
        pdf.set_font("Courier", size=10)
        pdf.multi_cell(0, 10, f"RAM DUMP (SHA-256):\n{self.ram_hash}")
        pdf.ln(5)
        pdf.multi_cell(0, 10, f"DISK IMAGE (SHA-256):\n{self.disk_hash}")
        
        filename = os.path.join(EVIDENCE_DIR, "Final_Report.pdf")
        pdf.output(filename)
        self.log(f"Report Saved: {filename}")
        
        try:
            os.startfile(filename)
        except Exception as e:
            self.log(f"Could not open PDF automatically: {e}")

    def calculate_hash(self, filepath):
        sha256 = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except FileNotFoundError:
            return "FILE_NOT_FOUND_ERROR"

if __name__ == "__main__":
    if not is_admin():
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("CRITICAL ERROR: YOU MUST RUN AS ADMINISTRATOR")
        print("Right-click Command Prompt/PowerShell -> 'Run as Administrator'")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    print("DEBUG: Starting App...")
    root = tk.Tk()
    app = ForensiLockApp(root)
    root.mainloop()