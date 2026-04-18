# CNC Controller with OpenGL

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
