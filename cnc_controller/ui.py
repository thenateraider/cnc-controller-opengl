from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
import serial
import re
import time

from .controller import CNCApp
from .info_window import InfoWindow
from .opengl_widget import MyOpenGLWidget


class Ui_Widget(object):

    def __init__(self):

        self.cnc_app = None
        self.last_jog_axis = None
        self.jog_accum = 0.0
        self.last_jog_button = None
        self.jog_total = 0.0
    def jog_status(self, button, distance):

        self.set_state(
            "JOG",
            f"Jog {button} {distance}"
        )
    def add_jog_queue(self, text):

        self.queueList.addItem(text)

        # อัปเดตสี
        self.update_queue_display()
    def set_state(self, state, message=None):
        self.cnc_app.set_state(state, message)
        self.adjust_status_font()
    def adjust_status_font(self):
        from PyQt5.QtGui import QFontMetrics
        text = self.statusLabel.text()
        label_width = self.statusLabel.width()

        font = self.statusLabel.font()
        font_size = 20  # เริ่มต้น

        while font_size > 8:
            font.setPointSize(font_size)
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(text)

            if text_width <= label_width - 20:  # เผื่อ padding
                break

            font_size -= 1

        self.statusLabel.setFont(font)
    def view_top(self):

        self.openGLWidget.rotation_x = 0
        self.openGLWidget.rotation_y = 0
        self.openGLWidget.update()


    def view_front(self):

        self.openGLWidget.rotation_x = 90
        self.openGLWidget.rotation_y = 180
        self.openGLWidget.update()


    def view_side(self):

        self.openGLWidget.rotation_x = 0
        self.openGLWidget.rotation_y = 90
        self.openGLWidget.update()
    def setupUi(self, Widget):
        Widget.setObjectName("Widget")
        Widget.resize(1010, 634)
        mainLayout = QtWidgets.QHBoxLayout(Widget)
        mainLayout.setContentsMargins(5, 5, 5, 5)
        mainLayout.setSpacing(5)
        leftLayout = QtWidgets.QVBoxLayout()
        rightLayout = QtWidgets.QVBoxLayout()

        mainLayout.addLayout(leftLayout, 1)
        mainLayout.addLayout(rightLayout, 2)

        self.textEdit = QtWidgets.QTextEdit(Widget)
        self.textEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.textEdit.customContextMenuRequested.connect(self.show_textedit_menu)
        leftLayout.addWidget(self.textEdit, 1)
        self.textEdit.setStyleSheet("background-color: rgb(85, 255, 255);")
        self.textEdit.setObjectName("textEdit")

        self.openGLWidget = MyOpenGLWidget(Widget)
        rightLayout.addWidget(self.openGLWidget)
        self.openGLWidget.setObjectName("openGLWidget")

        self.widget = QtWidgets.QWidget(Widget)
        leftLayout.addWidget(self.widget, 1)
        self.widget.setStyleSheet("background-color: rgb(147, 147, 147);")
        self.widget.setObjectName("widget")

        self.X_RIGHT = QtWidgets.QPushButton(self.widget)
        self.X_RIGHT.setGeometry(QtCore.QRect(180, 100, 81, 60))
        self.X_RIGHT.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.X_RIGHT.setObjectName("X_RIGHT")
        
        self.X_LEFT = QtWidgets.QPushButton(self.widget)
        self.X_LEFT.setGeometry(QtCore.QRect(20, 100, 81, 60))
        self.X_LEFT.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.X_LEFT.setObjectName("X_LEFT")

        self.Y_UP = QtWidgets.QPushButton(self.widget)
        self.Y_UP.setGeometry(QtCore.QRect(100, 30, 81, 71))
        self.Y_UP.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.Y_UP.setObjectName("Y_UP")
        
        self.Y_DOWN = QtWidgets.QPushButton(self.widget)
        self.Y_DOWN.setGeometry(QtCore.QRect(100, 160, 81, 71))
        self.Y_DOWN.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.Y_DOWN.setObjectName("Y_DOWN")

        self.Z_UP = QtWidgets.QPushButton(self.widget)
        self.Z_UP.setGeometry(QtCore.QRect(320, 30, 81, 71))
        self.Z_UP.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.Z_UP.setObjectName("Z_UP")
        
        self.Z_DOWN = QtWidgets.QPushButton(self.widget)
        self.Z_DOWN.setGeometry(QtCore.QRect(320, 160, 81, 71))
        self.Z_DOWN.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.Z_DOWN.setObjectName("Z_DOWN")

        # ------------------------
        # JOG MULTIPLIER CONTROL
        # ------------------------

        self.jogMinus = QtWidgets.QPushButton("-", self.widget)
        self.jogMinus.setGeometry(QtCore.QRect(130, 250, 40, 40))
        self.jogMinus.setStyleSheet("font: bold 18pt 'Segoe UI';")

        self.jogValue = QtWidgets.QLineEdit(self.widget)
        self.jogValue.setGeometry(QtCore.QRect(170, 250, 100, 40))
        self.jogValue.setAlignment(Qt.AlignCenter)
        self.jogValue.setText("1")
        self.jogValue.setStyleSheet("""
        background-color:white;
        font: bold 12pt 'Segoe UI';
        border:2px solid #444;
        border-radius:5px;
        """)

        self.jogPlus = QtWidgets.QPushButton("+", self.widget)
        self.jogPlus.setGeometry(QtCore.QRect(270, 250, 40, 40))
        self.jogPlus.setStyleSheet("font: bold 18pt 'Segoe UI';")
        self.statusLabel = QtWidgets.QLabel(self.widget)
        self.jogPlus.clicked.connect(self.increase_jog)
        self.jogMinus.clicked.connect(self.decrease_jog)
        self.statusLabel.setGeometry(QtCore.QRect(160, 305, 291, 51))
        self.statusLabel.setAlignment(Qt.AlignCenter)
        self.statusLabel.setText("IDLE")
        
        self.statusLabel.setStyleSheet("""
            background-color: #3B1E54;
            color: white;
            font: 16pt 'Segoe UI';
            border-radius: 8px;
        """)
        
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setGeometry(QtCore.QRect(20, 315, 131, 31))
        self.label_5.setStyleSheet("font: 700 22pt \"Segoe UI\";")
        self.label_5.setObjectName("label_5")


        
        self.frame = QtWidgets.QFrame(Widget)
        
        self.viewTop = QtWidgets.QPushButton("TOP", self.frame)
        self.viewTop.setGeometry(QtCore.QRect(600, 340, 60, 35))

        self.viewFront = QtWidgets.QPushButton("FRONT", self.frame)
        self.viewFront.setGeometry(QtCore.QRect(690, 340, 60, 35))

        self.viewSide = QtWidgets.QPushButton("SIDE", self.frame)
        self.viewSide.setGeometry(QtCore.QRect(780, 340, 60, 35))
        self.viewTop.clicked.connect(self.view_top)
        self.viewFront.clicked.connect(self.view_front)
        self.viewSide.clicked.connect(self.view_side)

        # ===== Jog Queue Panel =====
        self.queueFrame = QtWidgets.QFrame(self.frame)
        self.queueFrame.setGeometry(QtCore.QRect(600, 10, 250, 320))

        self.queueFrame.setStyleSheet("""
        QFrame{
            background-color:#222;
            border:3px solid #444;
            border-radius:8px;
        }
        """)

        self.queueLayout = QtWidgets.QVBoxLayout(self.queueFrame)

        self.queueTitle = QtWidgets.QLabel("JOG QUEUE (Manual)")
        self.queueTitle.setStyleSheet("""
        color:white;
        font: bold 14pt 'Segoe UI';
        """)

        self.queueLayout.addWidget(self.queueTitle)
        self.runningLabel = QtWidgets.QLabel("RUNNING : -")
        self.runningLabel.setStyleSheet("""
        color:#ffaa00;
        font:bold 12pt 'Segoe UI';
        """)

        self.queueLayout.addWidget(self.runningLabel)
        self.queueList = QtWidgets.QListWidget()

        self.queueList.setStyleSheet("""
        QListWidget{
        background:#111;
        color:#00ffaa;
        font:13pt 'Consolas';
        border:none;
        padding:5px;
        }

        QListWidget::item{
        padding:6px;
        }
        """)
        self.queueLayout.addWidget(self.queueList)
        rightLayout.addWidget(self.frame)
        self.frame.setStyleSheet("background-color: rgb(147, 147, 147);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")


        self.lcdNumber = QtWidgets.QLCDNumber(self.frame)
        self.lcdNumber.setGeometry(QtCore.QRect(400, 10, 171, 41))
        self.lcdNumber.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.lcdNumber.setObjectName("lcdNumber")

        self.lcdNumber_2 = QtWidgets.QLCDNumber(self.frame)
        self.lcdNumber_2.setGeometry(QtCore.QRect(400, 70, 171, 41))
        self.lcdNumber_2.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.lcdNumber_2.setObjectName("lcdNumber_2")

        self.lcdNumber_3 = QtWidgets.QLCDNumber(self.frame)
        self.lcdNumber_3.setGeometry(QtCore.QRect(400, 130, 171, 41))
        self.lcdNumber_3.setStyleSheet("background-color: rgb(0, 255, 127);")
        self.lcdNumber_3.setObjectName("lcdNumber_3")

        self.label = QtWidgets.QLabel(self.frame)
        self.label.setGeometry(QtCore.QRect(360, 10, 31, 41))
        self.label.setStyleSheet("font: 700 18pt \"Segoe UI\";")
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setGeometry(QtCore.QRect(370, 70, 21, 41))
        self.label_2.setStyleSheet("font: 700 18pt \"Segoe UI\";")
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setGeometry(QtCore.QRect(370, 130, 21, 41))
        self.label_3.setStyleSheet("font: 700 18pt \"Segoe UI\";")
        self.label_3.setObjectName("label_3")


        self.START = QtWidgets.QPushButton(self.frame)
        self.START.setGeometry(QtCore.QRect(20, 10, 101, 51))
        self.START.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0.989, y1:0, x2:1, y2:0, stop:0 rgba(102, 255, 104, 255), stop:0.55 rgba(235, 148, 61, 255), stop:0.98 rgba(0, 0, 0, 255), stop:1 rgba(0, 0, 0, 0));\nfont: 24pt \"Segoe UI\";")
        self.START.setObjectName("START")

        self.STOP = QtWidgets.QPushButton(self.frame)
        self.STOP.setGeometry(QtCore.QRect(20, 80, 101, 51))
        self.STOP.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 0, 0, 255), stop:1 rgba(255, 0, 0, 255));\nfont: 24pt \"Segoe UI\";")
        self.STOP.setObjectName("STOP")

        self.RESET = QtWidgets.QPushButton(self.frame)
        self.RESET.setGeometry(QtCore.QRect(20, 140, 101, 51))
        self.RESET.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 0, 255), stop:0.852273 rgba(255, 255, 0, 255));\nfont: 24pt \"Segoe UI\";")
        self.RESET.setObjectName("RESET")

        self.INFO = QtWidgets.QPushButton(self.frame)
        self.INFO.setGeometry(QtCore.QRect(20,200,101,51))
        self.INFO.setStyleSheet("""
        QPushButton{
            background-color: qlineargradient(
                spread:pad,
                x1:0, y1:0,
                x2:0, y2:1,
                stop:0 rgba(255,255,0,255),
                stop:0.85 rgba(255,125,0,255)
            );
            font: 24pt "Segoe UI";
            color: black;
        }
        """)
        self.INFO.setText("INFO")

        self.ZERO_X = QtWidgets.QPushButton(self.frame)
        self.ZERO_X.setGeometry(QtCore.QRect(270, 10, 91, 51))
        self.ZERO_X.setStyleSheet("font: 14pt \"Segoe UI\";")
        self.ZERO_X.setObjectName("ZERO_X")

        self.ZERO_Y = QtWidgets.QPushButton(self.frame)
        self.ZERO_Y.setGeometry(QtCore.QRect(270, 70, 91, 51))
        self.ZERO_Y.setStyleSheet("font: 14pt \"Segoe UI\";")
        self.ZERO_Y.setObjectName("ZERO_Y")

        self.ZERO_Z = QtWidgets.QPushButton(self.frame)
        self.ZERO_Z.setGeometry(QtCore.QRect(270, 130, 91, 51))
        self.ZERO_Z.setStyleSheet("font: 14pt \"Segoe UI\";")
        self.ZERO_Z.setObjectName("ZERO_Z")

        self.SET_ZERO = QtWidgets.QPushButton(self.frame)
        self.SET_ZERO.setGeometry(QtCore.QRect(130, 10, 131, 61))
        self.SET_ZERO.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.SET_ZERO.setObjectName("SET_ZERO")

        self.SET_HOME = QtWidgets.QPushButton(self.frame)
        self.SET_HOME.setGeometry(QtCore.QRect(130, 80, 131, 61))
        self.SET_HOME.setStyleSheet("font: 20pt \"Segoe UI\";")
        self.SET_HOME.setObjectName("SET_HOME")
        # =========================
        # MANUAL OFFSET SECTION
        # =========================

        self.manualOffsetFrame = QtWidgets.QFrame(self.frame)
        self.manualOffsetFrame.setGeometry(QtCore.QRect(270, 185, 300, 140))

        self.manualOffsetFrame.setStyleSheet("""
        QFrame{
        background:#222;
        border:2px solid #555;
        border-radius:6px;
        }
        """)

        layout = QtWidgets.QGridLayout(self.manualOffsetFrame)
        # Checkbox enable
        self.manualOffsetEnable = QtWidgets.QCheckBox("Manual Offset")
        self.manualOffsetEnable.setStyleSheet("color:white;font:12pt 'Segoe UI';background:#222")
        layout.addWidget(self.manualOffsetEnable,0,0)
        self.setCenterBtn = QtWidgets.QPushButton("SET CENTER")
        self.setCenterBtn.setStyleSheet("""
        QPushButton{
        background:#ffaa00;
        font:9pt 'Segoe UI';
        border-radius:4px;
        }
        """)

        layout.addWidget(self.setCenterBtn,0,1)
        # ---------- X Offset ----------
        labelX = QtWidgets.QLabel("X Offset")
        labelX.setStyleSheet("color:white;font:11pt 'Segoe UI'")
        layout.addWidget(labelX,1,0)

        self.offsetX = QtWidgets.QLineEdit("0")
        self.offsetX.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.offsetX,1,1)

        # ---------- Y Offset ----------
        labelY = QtWidgets.QLabel("Y Offset")
        labelY.setStyleSheet("color:white;font:11pt 'Segoe UI'")
        layout.addWidget(labelY,2,0)

        self.offsetY = QtWidgets.QLineEdit("0")
        self.offsetY.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.offsetY,2,1)

        # ---------- Z Offset ----------
        labelZ = QtWidgets.QLabel("Z Offset")
        labelZ.setStyleSheet("color:white;font:11pt 'Segoe UI'")
        layout.addWidget(labelZ,3,0)

        self.offsetZ = QtWidgets.QLineEdit("0")
        self.offsetZ.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.offsetZ,3,1)

        # ---------- Send Button ----------
        self.offsetSend = QtWidgets.QPushButton("SEND OFFSET")
        self.offsetSend.setStyleSheet("color:white;font:9pt 'Segoe UI'")
        layout.addWidget(self.offsetSend,4,0,1,2)


        self.setCenterBtn.setVisible(False)
        # เริ่มต้น disable
        self.offsetX.setEnabled(False)
        self.offsetY.setEnabled(False)
        self.offsetZ.setEnabled(False)
        self.offsetSend.setEnabled(False)
        self.setCenterBtn.setVisible(False)

        # สีปุ่ม
        self.offsetSend.setStyleSheet("""
        QPushButton{
        background-color:qlineargradient(
        spread:pad,x1:0,y1:0,x2:1,y2:1,
        stop:1 rgba(82,168,255,255));
        font:16pt "Segoe UI";
        border-radius:5px;
        }

        QPushButton:disabled{
        background-color:rgb(120,120,120);
        color:rgb(200,200,200);
        }
        """)

        # Toggle enable
        self.manualOffsetEnable.toggled.connect(self.toggle_manual_offset)

        self.forceFinish = QtWidgets.QPushButton("FORCE\nFINISH", self.frame)
        self.forceFinish.setGeometry(QtCore.QRect(145,200,100,100))
        self.forceFinish.setStyleSheet("""
        background-color:#ffaa00;
        font:20pt 'Segoe UI';
        """)
        self.forceFinish.clicked.connect(self.force_finish)
        # =========================
        # CONNECTION SECTION
        # =========================

        # Layout container ใต้ INPUT
        self.connectionFrame = QtWidgets.QFrame(self.frame)
        self.connectionFrame.setGeometry(QtCore.QRect(20, 330, 560, 50))
        self.connectionFrame.setStyleSheet("""
        QFrame {
            background-color: #6f6f6f;
            border: 2px solid #555;
            border-radius: 8px;
        }
        """)
        # Layout สำหรับ connectionFrame
        self.connectionLayout = QtWidgets.QHBoxLayout(self.connectionFrame)
        self.connectionLayout.setContentsMargins(5, 5, 5, 5)
        self.connectionLayout.setSpacing(10)


        # Toggle SIM
        self.simToggle = QtWidgets.QPushButton("SIMULATION", self.connectionFrame)
        self.connectionLayout.addWidget(self.simToggle)
        self.simToggle.setFixedSize(130, 35)
        self.simToggle.setCheckable(True)
        self.simToggle.setChecked(True)
        self.simToggle.setStyleSheet("""
        QPushButton {
            background-color:#999;
            color:white;
            border-radius:5px;
            
        }
        QPushButton:checked {
            background-color:#2E8B57;
            font-weight: bold;
        }
        """)

        # Toggle Arduino
        self.arduinoToggle = QtWidgets.QPushButton("ARDUINO", self.connectionFrame)
        self.connectionLayout.addWidget(self.arduinoToggle)
        self.arduinoToggle.setFixedSize(130, 35)
        self.arduinoToggle.setCheckable(True)
        self.arduinoToggle.setStyleSheet("""
        QPushButton {
            background-color:#999;
            color:white;
            border-radius:5px;
        }
        QPushButton:checked {
            background-color:#E67E22;
            font-weight: bold;
        }
        """)

        # Port Dropdown (ซ่อนตอนแรก)
        self.portCombo = QtWidgets.QComboBox(self.connectionFrame)
        self.connectionLayout.addWidget(self.portCombo)
        self.portCombo.setFixedSize(130, 35)
        self.portCombo.setVisible(False)

        # Connect Button (ซ่อนตอนแรก)
        self.CONNECT = QtWidgets.QPushButton("CONNECT", self.connectionFrame)
        self.connectionLayout.addWidget(self.CONNECT)
        self.CONNECT.setFixedSize(85, 35)
        self.CONNECT.setVisible(False)
        self.retranslateUi(Widget)
        QtCore.QMetaObject.connectSlotsByName(Widget)
        self.simToggle.clicked.connect(self.activate_simulation)
        self.arduinoToggle.clicked.connect(self.activate_arduino)
        self.CONNECT.clicked.connect(self.connect_serial)
        self.CONNECT.setStyleSheet("""
        QPushButton {
            background-color:#444;
            color:white;
            border-radius:5px;
            font: 10pt "Segoe UI";
            font-weight: bold;
        }
        QPushButton:hover {
            background-color:#777;
            font-weight: bold;
        }
        QPushButton:pressed {
            background-color:#FF7F00;
            font-weight: bold;
        }
        """)
        # Refresh Button
        self.refreshBtn = QtWidgets.QPushButton("⟳", self.connectionFrame)
        self.connectionLayout.addWidget(self.refreshBtn)
        self.refreshBtn.setFixedSize(40, 35)
        self.refreshBtn.setVisible(False)
        self.connectionLayout.addStretch()
        self.refreshBtn.setStyleSheet("""
        QPushButton {
            background-color:#444;
            color:white;
            
            border-radius:5px;
            font: 14pt "Segoe UI";
            font-weight: bold;
        }
        QPushButton:hover {
            background-color:#777;
            font-weight: bold;
        }
        QPushButton:pressed {
            background-color:#FF7F00;
            font-weight: bold;
        }
        """)

        self.global_gcode = ""
        # default เป็น simulation
        self.arduino = None
        # สร้าง CNCApp instance (แก้ไขตรงนี้!)
        self.cnc_app = CNCApp(self.textEdit, self.arduino, self.START, self.statusLabel, self)
        self.infoWindow = InfoWindow(self.frame)
        self.openGLWidget.cnc = self.cnc_app
        # Connect signals to slots
        
        self.offsetSend.clicked.connect(self.set_manual_offset)
        # ไม่ต้อง connect START อีก เพราะ CNCApp จัดการแล้ว
        self.STOP.clicked.connect(self.stop_cnc)

        self.RESET.clicked.connect(self.reset_CNC)
        self.SET_ZERO.clicked.connect(self.set_zero)
        self.SET_HOME.clicked.connect(self.set_home)
        self.ZERO_X.clicked.connect(self.zero_x)
        self.ZERO_Y.clicked.connect(self.zero_y)
        self.ZERO_Z.clicked.connect(self.zero_z)
        self.X_RIGHT.clicked.connect(self.move_x_right)
        self.X_LEFT.clicked.connect(self.move_x_left)
        self.Y_UP.clicked.connect(self.move_y_up)
        self.Y_DOWN.clicked.connect(self.move_y_down)
        self.Z_UP.clicked.connect(self.move_z_up)
        self.Z_DOWN.clicked.connect(self.move_z_down)
        self.setCenterBtn.clicked.connect(self.set_center_offset)
        self.lcdNumber.display(0)
        self.lcdNumber_2.display(0)
        self.lcdNumber_3.display(0)
        # Connect refresh button
        self.refreshBtn.clicked.connect(self.refresh_ports)
        self.INFO.clicked.connect(self.show_info)

    def show_info(self):
        if self.infoWindow:
            self.infoWindow.show()

    def set_center_offset(self):

        # คำนวณกลางโต๊ะ
        cx = self.openGLWidget.bed_width / 2
        cy = self.openGLWidget.bed_depth / 2
        cz = 0

        # ใส่ค่าในช่อง offset
        self.offsetX.setText(str(round(cx,2)))
        self.offsetY.setText(str(round(cy,2)))
        self.offsetZ.setText(str(round(cz,2)))

        # ส่ง offset อัตโนมัติ
        self.set_manual_offset()

        self.set_state("IDLE","Offset preset → CENTER")
    
    def force_finish(self):

        if self.cnc_app.timer:
            self.cnc_app.timer.stop()
        # โหลด gcode เข้า viewer ก่อน
        self.openGLWidget.load_gcode(self.textEdit.toPlainText())

        self.openGLWidget.arcs.clear()
        self.openGLWidget.segments.clear()
        self.openGLWidget.last_pos = (0,0,0)

        self.cnc_app.machine_x = 0
        self.cnc_app.machine_y = 0
        self.cnc_app.machine_z = 0

        self.cnc_app.absolute_mode = True

        lines = self.textEdit.toPlainText().splitlines()

        for line in lines:

            line = line.strip().upper()

            if not line or line.startswith(";"):
                continue

            tx, ty, tz = self.cnc_app.parse_motion(line)

            print("LINE:", line)
            print("TARGET:", tx, ty, tz)
            print("MACHINE BEFORE:", 
                self.cnc_app.machine_x,
                self.cnc_app.machine_y,
                self.cnc_app.machine_z)

            if line.startswith(("G0","G1","G00","G01")):

                start = (
                    self.cnc_app.machine_x,
                    self.cnc_app.machine_y,
                    self.cnc_app.machine_z
                )

                end = (tx, ty, tz)

                print("SEGMENT:", start, "→", end)

                self.openGLWidget.segments.append((start, end, "XYZ"))

                self.cnc_app.machine_x = tx
                self.cnc_app.machine_y = ty
                self.cnc_app.machine_z = tz

                print("MACHINE AFTER:",
                    self.cnc_app.machine_x,
                    self.cnc_app.machine_y,
                    self.cnc_app.machine_z)

                print("--------------")
            elif line.startswith(("G2","G3","G02","G03")):

                coords = re.findall(r'[XYIJ]-?\d*\.?\d+', line)

                tx = self.cnc_app.machine_x
                ty = self.cnc_app.machine_y
                i = 0
                j = 0

                for c in coords:
                    if c.startswith("X"):
                        tx = float(c[1:])
                    elif c.startswith("Y"):
                        ty = float(c[1:])
                    elif c.startswith("I"):
                        i = float(c[1:])
                    elif c.startswith("J"):
                        j = float(c[1:])

                start = (
                    self.cnc_app.machine_x,
                    self.cnc_app.machine_y,
                    self.cnc_app.machine_z
                )

                end = (tx, ty, self.cnc_app.machine_z)

                print("ARC LINE:", line)
                print("ARC START:", start)
                print("ARC END:", end)
                print("ARC CENTER:", start[0]+i, start[1]+j)

                self.openGLWidget.arcs.append(
                    (start, end, i, j, line.startswith(("G2","G02")))
                )
                # อัปเดตตำแหน่งเครื่อง
                self.cnc_app.machine_x = tx
                self.cnc_app.machine_y = ty

                print("MACHINE AFTER:",
                    self.cnc_app.machine_x,
                    self.cnc_app.machine_y,
                    self.cnc_app.machine_z)

                print("--------------")
        self.openGLWidget.update()

        wx = self.cnc_app.machine_x + self.cnc_app.work_offset_x
        wy = self.cnc_app.machine_y + self.cnc_app.work_offset_y
        wz = self.cnc_app.machine_z + self.cnc_app.work_offset_z

        self.lcdNumber.display(round(wx,2))
        self.lcdNumber_2.display(round(wy,2))
        self.lcdNumber_3.display(round(wz,2))

        self.set_state("IDLE","Force Finish")
    def toggle_manual_offset(self, checked):

        self.offsetX.setEnabled(checked)
        self.offsetY.setEnabled(checked)
        self.offsetZ.setEnabled(checked)
        self.offsetSend.setEnabled(checked)
        self.setCenterBtn.setVisible(checked)
        if checked:

            self.set_state("IDLE","Manual Offset Enabled")

        else:

            # reset offset
            self.cnc_app.work_offset_x = 0
            self.cnc_app.work_offset_y = 0
            self.cnc_app.work_offset_z = 0

            # อัปเดต LCD เป็น machine position
            wx = self.cnc_app.machine_x
            wy = self.cnc_app.machine_y
            wz = self.cnc_app.machine_z

            self.lcdNumber.display(round(wx,2))
            self.lcdNumber_2.display(round(wy,2))
            self.lcdNumber_3.display(round(wz,2))
            self.offsetX.setText("0")
            self.offsetY.setText("0")
            self.offsetZ.setText("0")
            # refresh viewer
            self.openGLWidget.update()

            self.set_state("IDLE","Manual Offset Disabled")
    def retranslateUi(self, Widget):
        _translate = QtCore.QCoreApplication.translate
        Widget.setWindowTitle(_translate("Widget", "CNC Controller"))
        self.X_RIGHT.setText(_translate("Widget", "X+"))
        self.X_LEFT.setText(_translate("Widget", "X-"))
        self.Y_UP.setText(_translate("Widget", "Y+"))
        self.Y_DOWN.setText(_translate("Widget", "Y-"))
        self.Z_UP.setText(_translate("Widget", "Z+"))
        self.Z_DOWN.setText(_translate("Widget", "Z-"))
        self.label_5.setText(_translate("Widget", "STATUS:"))
        self.label.setText(_translate("Widget", " X"))
        self.label_2.setText(_translate("Widget", "Y"))
        self.label_3.setText(_translate("Widget", "Z"))
        self.START.setText(_translate("Widget", "START"))
        self.STOP.setText(_translate("Widget", "STOP"))
        self.RESET.setText(_translate("Widget", "RESET"))
        self.ZERO_X.setText(_translate("Widget", "ZERO X"))
        self.ZERO_Y.setText(_translate("Widget", "ZERO Y"))
        self.ZERO_Z.setText(_translate("Widget", "ZERO Z"))
        self.SET_ZERO.setText(_translate("Widget", "SET ZERO"))
        self.SET_HOME.setText(_translate("Widget", "SET HOME"))
        
    def activate_simulation(self):
        self.arduinoToggle.setChecked(False)
        self.simToggle.setChecked(True)

        self.portCombo.setVisible(False)
        self.CONNECT.setVisible(False)
        self.refreshBtn.setVisible(False)
        self.arduino = None
        self.cnc_app.serial = None

        self.set_state("IDLE", "Simulation Mode")
    def activate_arduino(self):
        self.simToggle.setChecked(False)
        self.arduinoToggle.setChecked(True)

        self.portCombo.setVisible(True)
        self.CONNECT.setVisible(True)
        self.refreshBtn.setVisible(True)
        self.refresh_ports()
    def refresh_ports(self):
        import serial.tools.list_ports
        self.portCombo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.portCombo.addItem(port.device)
    def connect_serial(self):

        port_name = self.portCombo.currentText()

        if not port_name:
            self.set_state("STOP", "No COM Port Found")
            return

        try:
            # ถ้ามี port เดิมเปิดอยู่ ให้ปิดก่อน
            if self.arduino and self.arduino.is_open:
                self.arduino.close()

            # เปิด serial
            self.arduino = serial.Serial(
                port=port_name,
                baudrate=9600,
                timeout=1
            )
            time.sleep(2)
            # ตรวจสอบว่าเปิดสำเร็จจริงไหม
            if self.arduino.is_open:
                self.cnc_app.serial = self.arduino
                self.set_state("IDLE", f"Connected: {port_name}")
            else:
                self.set_state("STOP", "Serial open failed")

        except PermissionError:
            self.set_state("STOP", "Port is already in use")

        except Exception as e:
            self.set_state("STOP", str(e))
    def set_manual_offset(self):

        try:

            ox = float(self.offsetX.text())
            oy = float(self.offsetY.text())
            oz = float(self.offsetZ.text())

            # -------------------------
            # SET WORK OFFSET
            # -------------------------

            self.cnc_app.work_offset_x = ox
            self.cnc_app.work_offset_y = oy
            self.cnc_app.work_offset_z = oz

            # -------------------------
            # MOVE TOOL TO W0
            # -------------------------

            # Machine position = offset
            self.cnc_app.machine_x = ox
            self.cnc_app.machine_y = oy
            self.cnc_app.machine_z = oz

            # sync planner
            self.cnc_app.planner_x = self.cnc_app.machine_x
            self.cnc_app.planner_y = self.cnc_app.machine_y
            self.cnc_app.planner_z = self.cnc_app.machine_z

            # -------------------------
            # UPDATE VIEWER
            # -------------------------

            self.openGLWidget.current_x = self.cnc_app.machine_x
            self.openGLWidget.current_y = self.cnc_app.machine_y
            self.openGLWidget.current_z = self.cnc_app.machine_z

            self.openGLWidget.last_pos = (
                self.cnc_app.machine_x,
                self.cnc_app.machine_y,
                self.cnc_app.machine_z
            )

            # -------------------------
            # WORK COORDINATE = 0
            # -------------------------

            self.lcdNumber.display(0)
            self.lcdNumber_2.display(0)
            self.lcdNumber_3.display(0)

            # refresh viewer
            self.openGLWidget.update()

            self.set_state(
                "IDLE",
                f"Offset → X{ox} Y{oy} Z{oz}"
            )

        except:
            self.set_state("STOP","Offset format error")
    def increase_jog(self):
        try:
            value = int(float(self.jogValue.text()))
        except:
            value = 1

        value *= 10
        self.jogValue.setText(str(value))

    def decrease_jog(self):
        try:
            value = int(float(self.jogValue.text()))
        except:
            value = 1

        value //= 10

        if value < 1:
            value = 1

        self.jogValue.setText(str(value)) 
    def show_textedit_menu(self, position):
        menu = QtWidgets.QMenu()

        undo = menu.addAction("Undo")
        redo = menu.addAction("Redo")
        menu.addSeparator()
        cut = menu.addAction("Cut")
        copy = menu.addAction("Copy")
        paste = menu.addAction("Paste")
        delete = menu.addAction("Delete")
        menu.addSeparator()
        select_all = menu.addAction("Select All")

        # 🎨 แก้สี hover ตรงนี้
        menu.setStyleSheet("""
        QMenu {
            background-color: rgb(85, 255, 255);
            color: black;
            font: 12pt "Segoe UI";
        }
        QMenu::item {
            padding: 6px 25px 6px 20px;
        }
        QMenu::item:selected {
            background-color: rgb(0,120,215);
            color: white;
        }
        """)

        action = menu.exec_(self.textEdit.mapToGlobal(position))

        if action == undo:
            self.textEdit.undo()
        elif action == redo:
            self.textEdit.redo()
        elif action == cut:
            self.textEdit.cut()
        elif action == copy:
            self.textEdit.copy()
        elif action == paste:
            self.textEdit.paste()
        elif action == delete:
            self.textEdit.textCursor().removeSelectedText()
        elif action == select_all:
            self.textEdit.selectAll()
    def show_plaintext_menu(self, position):
        menu = QtWidgets.QMenu()

        undo = menu.addAction("Undo")
        redo = menu.addAction("Redo")
        menu.addSeparator()
        cut = menu.addAction("Cut")
        copy = menu.addAction("Copy")
        paste = menu.addAction("Paste")
        delete = menu.addAction("Delete")
        menu.addSeparator()
        select_all = menu.addAction("Select All")

        # 🎨 แก้สี hover ตรงนี้
        menu.setStyleSheet("""
        QMenu {
            background-color: white;
            color: black;
            font: 12pt "Segoe UI";
            border: 1px solid #aaa;
        }
        QMenu::item {
            padding: 6px 25px 6px 20px;
        }
        QMenu::item:selected {
            background-color: #2E8B57;
            color: white;
        }
        """)

        action = menu.exec_(self.plainTextEdit_2.mapToGlobal(position))

        if action == undo:
            self.plainTextEdit_2.undo()
        elif action == redo:
            self.plainTextEdit_2.redo()
        elif action == cut:
            self.plainTextEdit_2.cut()
        elif action == copy:
            self.plainTextEdit_2.copy()
        elif action == paste:
            self.plainTextEdit_2.paste()
        elif action == delete:
            cursor = self.plainTextEdit_2.textCursor()
            cursor.removeSelectedText()
        elif action == select_all:
            self.plainTextEdit_2.selectAll()   

    def get_jog_distance(self):
        try:
            distance = float(self.jogValue.text())
            return max(distance, 1.0) # ขั้นต่ำ 1mm
        except:
            return 1.0

    def execute_jog(self, dx, dy, dz, axis_label):

        distance = self.get_jog_distance()

        new_mx = self.cnc_app.planner_x + (dx * distance)
        new_my = self.cnc_app.planner_y + (dy * distance)
        new_mz = self.cnc_app.planner_z + (dz * distance)

        jog_command = (
            f"G91;\n"
            f"G1 X{dx*distance} Y{dy*distance} Z{dz*distance} F1000;\n"
            f"G90;\n"
        )

        
        if self.cnc_app.serial and self.cnc_app.serial.is_open:
            self.cnc_app.serial.write(jog_command.encode())

        # update planner
        self.cnc_app.planner_x = new_mx
        self.cnc_app.planner_y = new_my
        self.cnc_app.planner_z = new_mz

        self.jog_status(axis_label, distance)

        self.queueList.addItem(f"{axis_label} {distance}")
        self.update_queue_display()

        wx = self.cnc_app.planner_x - self.cnc_app.work_offset_x
        wy = self.cnc_app.planner_y - self.cnc_app.work_offset_y
        wz = self.cnc_app.planner_z - self.cnc_app.work_offset_z

        self.cnc_app.motion_queue.append((wx, wy, wz))
        self.cnc_app.process_queue()

    # --- เชื่อมต่อปุ่มบน UI กับฟังก์ชันกลาง ---

    def move_x_right(self):
        self.execute_jog(1, 0, 0, "X+")

    def move_x_left(self):
        self.execute_jog(-1, 0, 0, "X-")

    def move_y_up(self):
        self.execute_jog(0, 1, 0, "Y+")

    def move_y_down(self):
        self.execute_jog(0, -1, 0, "Y-")

    def move_z_up(self):
        self.execute_jog(0, 0, 1, "Z+")

    def move_z_down(self):
        self.execute_jog(0, 0, -1, "Z-")
    def send_gcode(self):
         gcode = self.plainTextEdit_2.toPlainText()
         self.global_gcode = gcode
         self.textEdit.setPlainText(gcode)

    def send_command(self, command):  # ← อยู่ตรงนี้
        """ฟังก์ชันช่วยส่งคำสั่งไปยัง Arduino (เพิ่ม ; อัตโนมัติ)"""
        if self.arduino and self.arduino.isOpen():
            try:
                # เพิ่ม semicolon ถ้ายังไม่มี
                if not command.endswith(';'):
                    command = command + ';'
                
                self.arduino.write((command + '\n').encode())
                self.set_state("RUN", f"Sent: {command}")
                
                import time
                time.sleep(0.05)
                
                while self.arduino.in_waiting > 0:
                    response = self.arduino.readline().decode().strip()
                    if response:
                        print(f'Arduino: {response}')
            except Exception as e:
                self.set_state("STOP", f"ข้อผิดพลาด: {str(e)}")
        else:
            self.set_state("STOP", "ไม่ได้เชื่อมต่อ Arduino")
    # Edit for Test
    def play(self):
        # ส่ง G-code ไปยัง Arduino
        gcode = self.global_gcode
        if self.arduino:
            self.arduino.write(gcode.encode())
            self.arduino.write(b'\n')
            self.set_state("IDLE", "เสร็จสิ้น")
            response = self.arduino.readline().decode().strip()
            print(response)
        else:
            self.set_state("IDLE", "(SIM) เสร็จสิ้น")
        self.openGLWidget.load_gcode(gcode)
        print(gcode)
    
    def stop_cnc(self):
        # บอก CNCApp ให้หยุด
        self.cnc_app.stop_requested = True
        if self.arduino:
            self.arduino.write(b'M0\n')
            response = self.arduino.readline().decode().strip()
            print(response)
        self.set_state("HOLD", "หยุดชั่วคราว")
        
    def update_queue_display(self):

        if self.queueList.count() == 0:
            self.runningLabel.setText("RUNNING : -")
            return

        running = self.queueList.item(0).text()
        self.runningLabel.setText(f"RUNNING : {running}")

        for i in range(self.queueList.count()):

            item = self.queueList.item(i)

            if i == 0:
                item.setBackground(QtGui.QColor("#ff8800"))
                item.setForeground(QtGui.QColor("black"))
            else:
                item.setBackground(QtGui.QColor("#1a3cff"))
                item.setForeground(QtGui.QColor("white"))
    def reset_CNC(self):

        if self.cnc_app.timer:
            self.cnc_app.timer.stop()

        self.cnc_app.stop_requested = True

        # -------------------------
        # RESET MACHINE POSITION
        # -------------------------

        self.cnc_app.machine_x = 0.0
        self.cnc_app.machine_y = 0.0
        self.cnc_app.machine_z = 0.0

        # planner ต้องใช้ machine coordinate
        self.cnc_app.planner_x = self.cnc_app.machine_x
        self.cnc_app.planner_y = self.cnc_app.machine_y
        self.cnc_app.planner_z = self.cnc_app.machine_z

        # -------------------------
        # RESET INFO VALUES
        # -------------------------

        self.cnc_app.executed_path = 0
        self.cnc_app.remaining_path = 0
        self.cnc_app.progress = 0

        if self.infoWindow:

            self.infoWindow.progressLabel.setText("-")
            self.infoWindow.execLabel.setText("-")
            self.infoWindow.remainLabel.setText("-")

            self.infoWindow.distance.setText("-")
            self.infoWindow.feedLabel.setText("-")
            self.infoWindow.speedLabel.setText("-")
            self.infoWindow.timeLabel.setText("-")

            self.infoWindow.arcCenterX.setText("-")
            self.infoWindow.arcCenterY.setText("-")
            self.infoWindow.arcRadius.setText("-")
            self.infoWindow.arcLength.setText("-")

        # -------------------------
        # RESET VIEWER
        # -------------------------

        self.openGLWidget.drawn_path.clear()
        self.openGLWidget.vertices.clear()
        self.openGLWidget.arcs.clear()

        self.openGLWidget.segments.clear()
        self.openGLWidget.current_axis = None
        self.openGLWidget.last_segment_index = -1

        # ใช้ตำแหน่ง machine จริง
        self.openGLWidget.last_pos = (
            self.cnc_app.machine_x,
            self.cnc_app.machine_y,
            self.cnc_app.machine_z
        )

        self.openGLWidget.current_x = self.cnc_app.machine_x
        self.openGLWidget.current_y = self.cnc_app.machine_y
        self.openGLWidget.current_z = self.cnc_app.machine_z

        self.openGLWidget.update()

        # -------------------------
        # RESET QUEUE
        # -------------------------

        self.cnc_app.motion_queue.clear()

        self.queueList.clear()
        self.runningLabel.setText("RUNNING : -")

        self.update_queue_display()

        # -------------------------
        # RESET LCD (Work coordinate)
        # -------------------------

        wx = self.cnc_app.machine_x - self.cnc_app.work_offset_x
        wy = self.cnc_app.machine_y - self.cnc_app.work_offset_y
        wz = self.cnc_app.machine_z - self.cnc_app.work_offset_z

        self.lcdNumber.display(round(wx,2))
        self.lcdNumber_2.display(round(wy,2))
        self.lcdNumber_3.display(round(wz,2))

        self.set_state("IDLE", "RESET → Tool at W0")
    def set_zero(self):

        # ปิดการวาดชั่วคราว
        self.openGLWidget.draw_enabled = False

        ox = self.cnc_app.work_offset_x
        oy = self.cnc_app.work_offset_y
        oz = self.cnc_app.work_offset_z

        # -------------------------
        # MOVE TOOL TO W0
        # -------------------------

        self.cnc_app.machine_x = ox
        self.cnc_app.machine_y = oy
        self.cnc_app.machine_z = oz

        # -------------------------
        # SYNC PLANNER
        # -------------------------

        self.cnc_app.planner_x = self.cnc_app.machine_x
        self.cnc_app.planner_y = self.cnc_app.machine_y
        self.cnc_app.planner_z = self.cnc_app.machine_z

        # -------------------------
        # RESET DRAW START
        # -------------------------

        self.openGLWidget.last_pos = (
            self.cnc_app.machine_x,
            self.cnc_app.machine_y,
            self.cnc_app.machine_z
        )

        # เริ่ม path ใหม่
        self.openGLWidget.current_x = self.cnc_app.machine_x
        self.openGLWidget.current_y = self.cnc_app.machine_y
        self.openGLWidget.current_z = self.cnc_app.machine_z

        # -------------------------
        # UPDATE LCD (WORK = 0)
        # -------------------------

        self.lcdNumber.display(0)
        self.lcdNumber_2.display(0)
        self.lcdNumber_3.display(0)

        # เปิดวาดอีกครั้ง
        self.openGLWidget.draw_enabled = True

        self.openGLWidget.update()

        self.set_state("IDLE","Tool moved to W0 (SET ZERO)")
    def set_home(self):

        ox = self.cnc_app.work_offset_x
        oy = self.cnc_app.work_offset_y
        oz = self.cnc_app.work_offset_z

        # ย้าย tool ไป W0
        self.cnc_app.machine_x = 0
        self.cnc_app.machine_y = 0
        self.cnc_app.machine_z = 0

        # sync planner
        self.cnc_app.planner_x = 0
        self.cnc_app.planner_y = 0
        self.cnc_app.planner_z = 0

        # update viewer tool
        self.openGLWidget.current_x = self.cnc_app.machine_x
        self.openGLWidget.current_y = self.cnc_app.machine_y
        self.openGLWidget.current_z = self.cnc_app.machine_z

        # ไม่ให้เกิดเส้นใหม่
        self.openGLWidget.last_pos = (
            self.cnc_app.machine_x,
            self.cnc_app.machine_y,
            self.cnc_app.machine_z
        )

        # update LCD
        self.lcdNumber.display(0)
        self.lcdNumber_2.display(0)
        self.lcdNumber_3.display(0)

        self.openGLWidget.update()

        self.set_state("IDLE","Tool moved to W0")
    def zero_x(self):

        mx = self.cnc_app.machine_x

        self.cnc_app.work_offset_x = -mx

        self.offsetX.setText(str(round(self.cnc_app.work_offset_x,2)))

        wx = mx + self.cnc_app.work_offset_x

        self.lcdNumber.display(round(wx,2))

        self.openGLWidget.update()

        self.set_state("IDLE","Work X set to 0")
    def zero_y(self):

        my = self.cnc_app.machine_y

        self.cnc_app.work_offset_y = -my

        self.offsetY.setText(str(round(self.cnc_app.work_offset_y,2)))

        wy = my + self.cnc_app.work_offset_y

        self.lcdNumber_2.display(round(wy,2))

        self.openGLWidget.update()

        self.set_state("IDLE","Work Y set to 0")
    def zero_z(self):

        mz = self.cnc_app.machine_z

        self.cnc_app.work_offset_z = -mz

        self.offsetZ.setText(str(round(self.cnc_app.work_offset_z,2)))

        wz = mz + self.cnc_app.work_offset_z

        self.lcdNumber_3.display(round(wz,2))

        self.openGLWidget.update()

        self.set_state("IDLE","Work Z set to 0")
