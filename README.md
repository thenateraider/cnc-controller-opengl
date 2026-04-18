# CNC Controller with OpenGL

PyQt5 CNC controller with an OpenGL G-code toolpath viewer.

This project is organized as a small Python package so the code is easier to maintain and ready to publish on GitHub. The original launcher file, `CNCwithOpenGLfix2.py`, is still available and runs the same application.

## Project Structure

```text
CNC/
├── CNCwithOpenGLfix2.py          # Backward-compatible launcher
├── cnc_controller/
│   ├── __init__.py
│   ├── main.py                   # Application entry point
│   ├── main_window.py            # MainWindow wrapper
│   ├── ui.py                     # Main UI, jog buttons, serial, offset controls
│   ├── controller.py             # CNC logic, G-code execution, motion, serial send
│   ├── opengl_widget.py          # OpenGL viewer and toolpath rendering
│   └── info_window.py            # Calculation/info dialog
├── scripts/
│   ├── setup_macos_linux.sh      # Dependency setup for macOS/Linux
│   └── setup_windows.ps1         # Dependency setup for Windows
├── requirements.txt              # pip dependencies
├── pyproject.toml                # Package metadata and console script
├── .gitignore
└── README.md
```

## Requirements

- Python 3.9 or newer
- OpenGL driver from the operating system
- Python packages:
  - PyQt5
  - PyOpenGL
  - pyserial

## Quick Setup

### macOS / Linux

```bash
chmod +x scripts/setup_macos_linux.sh
./scripts/setup_macos_linux.sh
```

### Windows PowerShell

```powershell
.\scripts\setup_windows.ps1
```

## Manual Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run

Run with the original launcher:

```bash
python CNCwithOpenGLfix2.py
```

Or run as a module:

```bash
python -m cnc_controller.main
```

If installed in editable mode:

```bash
python -m pip install -e .
cnc-controller
```

## GitHub Notes

- Do not commit virtual environments such as `cncvenv/` or `.venv/`.
- `.gitignore` already excludes virtual environments, Python cache files, build output, and common system files.
- The main code lives in the `cnc_controller` package, while `CNCwithOpenGLfix2.py` remains as the original run file.

## Syntax Check

```bash
python -m compileall CNCwithOpenGLfix2.py cnc_controller
```

---

## ภาษาไทย

โปรแกรมควบคุม CNC และดูเส้นทาง G-code ด้วย PyQt5 + OpenGL

โค้ดถูกแยกออกเป็นหลายไฟล์เพื่อให้ง่ายต่อการดูแลและพร้อมนำขึ้น GitHub โดยยังคง entry point เดิมไว้ที่ `CNCwithOpenGLfix2.py`

## โครงสร้างโปรเจกต์

```text
CNC/
├── CNCwithOpenGLfix2.py          # ไฟล์รันเดิม ทำหน้าที่เรียก app ใหม่
├── cnc_controller/
│   ├── __init__.py
│   ├── main.py                   # จุดเริ่มโปรแกรม
│   ├── main_window.py            # MainWindow
│   ├── ui.py                     # หน้าจอหลัก ปุ่ม jog, serial, offset
│   ├── controller.py             # Logic CNC, G-code, motion, serial send
│   ├── opengl_widget.py          # OpenGL viewer และ toolpath rendering
│   └── info_window.py            # หน้าต่างข้อมูลการคำนวณ
├── scripts/
│   ├── setup_macos_linux.sh      # ติดตั้ง dependencies บน macOS/Linux
│   └── setup_windows.ps1         # ติดตั้ง dependencies บน Windows
├── requirements.txt              # รายการ dependencies แบบ pip
├── pyproject.toml                # package metadata และ console script
├── .gitignore
└── README.md
```

## Requirements

- Python 3.9 ขึ้นไป
- OpenGL driver จากระบบปฏิบัติการ
- Dependencies:
  - PyQt5
  - PyOpenGL
  - pyserial

## ติดตั้งแบบเร็ว

### macOS / Linux

```bash
chmod +x scripts/setup_macos_linux.sh
./scripts/setup_macos_linux.sh
```

### Windows PowerShell

```powershell
.\scripts\setup_windows.ps1
```

## ติดตั้งด้วยคำสั่งเอง

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

บน Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## การรันโปรแกรม

รันด้วยไฟล์เดิม:

```bash
python CNCwithOpenGLfix2.py
```

หรือรันเป็น module:

```bash
python -m cnc_controller.main
```

ถ้าติดตั้งแบบ editable:

```bash
python -m pip install -e .
cnc-controller
```

## หมายเหตุสำหรับ GitHub

- ไม่ควร commit virtual environment เช่น `cncvenv/` หรือ `.venv/`
- `.gitignore` ตั้งค่าให้ข้าม virtual environment, cache, build output และไฟล์ระบบทั่วไปแล้ว
- โค้ดหลักถูกแยกเป็น package `cnc_controller` แต่ไฟล์ `CNCwithOpenGLfix2.py` ยังใช้รันได้เหมือนเดิม

## ตรวจสอบ syntax

```bash
python -m compileall CNCwithOpenGLfix2.py cnc_controller
```
