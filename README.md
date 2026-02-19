# ForensiLock 

A Python + Tkinter desktop utility that simulates a **digital evidence acquisition workflow**:
- RAM acquisition (uses `winpmem.exe` if available, otherwise safe simulation mode)
- Disk image copy from a local target image
- SHA-256 integrity hashing
- PDF chain-of-custody style report generation

## Features

- Terminal-style forensic UI built with Tkinter
- Automatic evidence folder creation (`evidence_locker`)
- Fallback-safe RAM dump simulation when privileged tooling is unavailable
- Bit-stream style disk image copy from `suspect_drive.img`
- SHA-256 hashes for both RAM and disk artifacts
- One-click PDF report export (`Final_Report.pdf`)

## Project Structure

- `main.py` – Main GUI application
- `evidence_locker/` – Generated output folder (created at runtime)
- `suspect_drive.img` – Target image file (auto-created if missing)
- `winpmem.exe` – Optional external RAM acquisition tool (place beside `main.py`)

## Requirements

- Windows
- Python 3.10+
- Administrator privileges (required by app startup check)

Python package dependency:
- `fpdf`

Install dependency:

```powershell
pip install fpdf
```

## Run

From the project folder:

```powershell
python main.py
```

> Run the terminal as **Administrator** before launching, or the app exits immediately.

## Usage Flow

1. Click **[1] ACQUIRE RAM**
2. After success, click **[2] IMAGE DISK**
3. After success, click **[3] GENERATE REPORT**

Generated artifacts are stored in `evidence_locker`:
- `evidence_ram.raw`
- `evidence_disk.img`
- `Final_Report.pdf`

## Demo Video

- Play in browser (raw file):
	https://raw.githubusercontent.com/anujrwt08/Forensic-Flow/main/project%20demo%20video/project%20demo.mp4
- Repository file page (may show size warning for large files):
	https://github.com/anujrwt08/Forensic-Flow/blob/main/project%20demo%20video/project%20demo.mp4

## Notes

- If `winpmem.exe` is missing, RAM acquisition runs in simulation mode using random bytes.
- This project is suitable for demos, prototyping, and hackathon workflows.
- For real investigations, use validated forensic tooling, proper legal authorization, and strict chain-of-custody procedures.
