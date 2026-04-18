from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QTextEdit, QWidget
from PyQt5.QtGui import QTextCursor, QColor, QTextFormat
from PyQt5.QtCore import QTimer
import re
import math
import time


class CNCApp(QWidget):
    def __init__(self, text_edit, serial_port, start_button, status_display, ui):
        super().__init__()
        self.textEdit = text_edit
        self.serial = serial_port
        self.status_display = status_display
        self.current_line_index = 0
        self.lines = []
        self.timer = None
        self.state = "IDLE"
        self.stop_requested = False
        self.ui = ui
        start_button.clicked.connect(self.start_execution)
        self.motion_queue = []
        self.motion_running = False

        # ---- GCODE INFO SYSTEM ----
        self.total_path = 0
        self.executed_path = 0
        self.remaining_path = 0
        self.progress = 0
        self.last_target = (0,0,0)

        #--------------Motion State---------------
        self.machine_x = 0.0
        self.machine_y = 0.0
        self.machine_z = 0.0
        self.absolute_mode = True   # G90 default
        self.feedrate = 1000        # mm/min default
        # ---- Machine Parameters ----
        self.steps_per_rev = 200
        self.microstep = 8
        self.lead = 4

        self.steps_per_mm = (self.steps_per_rev * self.microstep) / self.lead
        self.max_pps = 20000
        self.acceleration = 300.0        # mm/sec²
        # planner position (ใช้สำหรับ jog queue)
        self.planner_x = 0.0
        self.planner_y = 0.0
        self.planner_z = 0.0

        self.work_offset_x = 0
        self.work_offset_y = 0
        self.work_offset_z = 0
        #-----------------------------------------
    def calc_distance(self,x1,y1,z1,x2,y2,z2):

        dx = x2-x1
        dy = y2-y1
        dz = z2-z1

        return math.sqrt(dx*dx + dy*dy + dz*dz)
    def calculate_total_path(self):

        lines = self.textEdit.toPlainText().splitlines()

        px = 0
        py = 0
        pz = 0

        total = 0

        for line in lines:

            line = line.strip().upper()

            if not line:
                continue

            # ---------- LINE ----------
            if line.startswith(("G0","G1","G00","G01")):

                tx,ty,tz = self.parse_motion(line)

                d = self.calc_distance(px,py,pz,tx,ty,tz)

                total += d

                px,py,pz = tx,ty,tz

            # ---------- ARC ----------
            elif line.startswith(("G2","G3","G02","G03")):

                coords = re.findall(r'[XYIJ]-?\d*\.?\d+', line)

                tx,ty = px,py
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

                center_x = px + i
                center_y = py + j

                radius = math.sqrt(i*i + j*j)

                start_angle = math.atan2(py-center_y,px-center_x)
                end_angle   = math.atan2(ty-center_y,tx-center_x)

                cw = line.startswith(("G2","G02"))

                if cw:
                    if start_angle <= end_angle:
                        start_angle += 2*math.pi
                    arc_angle = start_angle - end_angle
                else:
                    if end_angle <= start_angle:
                        end_angle += 2*math.pi
                    arc_angle = end_angle - start_angle

                arc_length = radius * abs(arc_angle)

                total += arc_length

                px,py = tx,ty

        self.total_path = total
    def update_info(self,command,target_x,target_y,target_z):

        start_x = self.machine_x
        start_y = self.machine_y
        start_z = self.machine_z

        ui = self.ui.infoWindow

        ui.commandLabel.setText(f"LINE : {command}")

        # -------------------------
        # PROGRESS
        # -------------------------

        ui.progressLabel.setText(str(round(self.progress,2)))
        ui.execLabel.setText(str(round(self.executed_path,2)))
        ui.remainLabel.setText(str(round(self.remaining_path,2)))

        # -------------------------
        # POSITION
        # -------------------------

        ui.startX.setText(str(round(start_x,3)))
        ui.startY.setText(str(round(start_y,3)))
        ui.startZ.setText(str(round(start_z,3)))

        ui.targetX.setText(str(round(target_x,3)))
        ui.targetY.setText(str(round(target_y,3)))
        ui.targetZ.setText(str(round(target_z,3)))


        # SPEED mm/sec
        speed = self.feedrate / 60
        

        # STEP FREQUENCY
        step_frequency = speed * self.steps_per_mm

        # ACCELERATION TIME
        accel_time = speed / self.acceleration

        # ACCELERATION DISTANCE
        accel_dist = (speed * speed) / (2 * self.acceleration)



        # -------------------------
        # LINEAR MOVE
        # -------------------------
        
        if step_frequency > self.max_pps:
            limit_status = "OVER"
        else:
            limit_status = "OK"
        if command.startswith(("G0","G1","G00","G01")):
           
            dist = self.calc_distance(start_x,start_y,start_z,target_x,target_y,target_z)
            steps = dist * self.steps_per_mm
            rpm = self.feedrate / self.lead
            time_est = dist/speed if speed>0 else 0
            ui.accelerationLabel.setText(str(self.acceleration))
            ui.distance.setText(str(round(dist,3)))
            ui.stepFreqLabel.setText(str(round(step_frequency,2)))
            ui.feedLabel.setText(str(self.feedrate))
            ui.speedLabel.setText(str(round(speed,3)))
            ui.timeLabel.setText(str(round(time_est,3)))
            
            # clear arc
            ui.arcCenterX.setText("-")
            ui.arcCenterY.setText("-")
            ui.arcRadius.setText("-")
            ui.arcLength.setText("-")
            ui.arcSegments.setText("-")
            ui.stepLabel.setText(str(round(steps,2)))
            ui.rpmLabel.setText(str(round(rpm,2)))
            ui.stepFreqLabel.setText(str(round(step_frequency,2)))
           
            ui.limitLabel.setText(limit_status)
            
            ui.accelLabel.setText(str(round(accel_time,4)))
            ui.accelDistLabel.setText(str(round(accel_dist,3))) 
        # -------------------------
        # ARC MOVE
        # -------------------------

        elif command.startswith(("G2","G3","G02","G03")):

            coords = re.findall(r'[XYZIJ]-?\d*\.?\d+', command)

            tx, ty = target_x, target_y
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

            center_x = start_x + i
            center_y = start_y + j

            radius = math.sqrt(i*i + j*j)

            start_angle = math.atan2(start_y-center_y,start_x-center_x)
            end_angle   = math.atan2(ty-center_y,tx-center_x)

            cw = command.startswith(("G2","G02"))

            if cw:
                if start_angle <= end_angle:
                    start_angle += 2*math.pi
                arc_angle = start_angle - end_angle
            else:
                if end_angle <= start_angle:
                    end_angle += 2*math.pi
                arc_angle = end_angle - start_angle

            arc_length = radius * abs(arc_angle)
            steps = arc_length * self.steps_per_mm
            segments = max(int(arc_length / 0.2),1)
            rpm = self.feedrate / self.lead
            time_est = arc_length/speed if speed>0 else 0

            ui.distance.setText(str(round(arc_length,3)))

            ui.feedLabel.setText(str(self.feedrate))
            ui.speedLabel.setText(str(round(speed,3)))
            ui.timeLabel.setText(str(round(time_est,3)))
            ui.stepFreqLabel.setText(str(round(step_frequency,2)))
            ui.accelLabel.setText(str(round(accel_time,4)))
            ui.accelDistLabel.setText(str(round(accel_dist,3)))
            ui.limitLabel.setText(limit_status)
            # ARC INFO
            ui.arcCenterX.setText(str(round(center_x,3)))
            ui.arcCenterY.setText(str(round(center_y,3)))
            ui.arcRadius.setText(str(round(radius,3)))
            ui.arcLength.setText(str(round(arc_length,3)))
            ui.stepLabel.setText(str(round(steps,2)))
            ui.arcSegments.setText(str(segments))
            ui.rpmLabel.setText(str(round(rpm,2)))
#-----------------Set State----------------------#
    def set_state(self, new_state, message=None):
        self.state = new_state

        color_map = {
            "IDLE": "#3B1E54",
            "RUN": "#2E8B57",
            "HOLD": "#E67E22",
            "STOP": "#C0392B",
            "JOG": "#2980B9"
        }

        bg_color = color_map.get(new_state, "#3B1E54")

        # ถ้าไม่ส่ง message มา → ใช้ state เป็นข้อความ
        display_text = message if message else new_state

        self.ui.statusLabel.setText(display_text)

        self.ui.statusLabel.setStyleSheet(f"""
            background-color: {bg_color};
            color: white;
            font: bold 15pt 'Segoe UI';
            border-radius: 8px;
            padding: 5px;
        """)
        self.ui.adjust_status_font()
#-------------------------------------------------#
#------------------G-Code Parser------------------#
    def parse_motion(self, line):
        line = line.upper()

        # G90 / G91
        if "G90" in line:
            self.absolute_mode = True
        if "G91" in line:
            self.absolute_mode = False

        # Feedrate
        f = re.findall(r'F(\d+\.?\d*)', line)
        if f:
            self.feedrate = float(f[0])

        target_x = self.machine_x
        target_y = self.machine_y
        target_z = self.machine_z

        coords = re.findall(r'[XYZ]-?\d*\.?\d+', line)

        for coord in coords:
            axis = coord[0]
            value = float(coord[1:])

            if self.absolute_mode:
                if axis == 'X':
                    target_x = value
                elif axis == 'Y':
                    target_y = value
                elif axis == 'Z':
                    target_z = value
            else:
                if axis == 'X':
                    target_x += value
                elif axis == 'Y':
                    target_y += value
                elif axis == 'Z':
                    target_z += value
        return target_x, target_y, target_z
#--------------------------------------------------#
    def process_queue(self):

        if self.motion_running:
            return

        if not self.motion_queue:
            return

        self.motion_running = True

        wx, wy, wz = self.motion_queue.pop(0)

        # remove UI queue item
        if self.ui.queueList.count() > 0:
            item = self.ui.queueList.takeItem(0)
            del item
            self.ui.update_queue_display()
            QtWidgets.QApplication.processEvents()

        mx = wx + self.work_offset_x
        my = wy + self.work_offset_y
        mz = wz + self.work_offset_z

        target = (mx, my, mz)

        self.move_linear(*target)

        if self.stop_requested:
            self.motion_running = False
            return

        self.motion_running = False

        # run next command
        if self.motion_queue:
            self.process_queue()
#------------------Linear Cartesian Interpolation------------------#
    def move_linear(self, target_x, target_y, target_z):

        start_x = self.machine_x
        start_y = self.machine_y
        start_z = self.machine_z

        dx = target_x - start_x
        dy = target_y - start_y
        dz = target_z - start_z
        # lock axis ที่ไม่ได้ถูกสั่ง
        if abs(dx) < 0.000001:
            dx = 0
        if abs(dy) < 0.000001:
            dy = 0
        if abs(dz) < 0.000001:
            dz = 0
        distance = math.sqrt(dx*dx + dy*dy + dz*dz)

        if distance == 0:
            return

        steps = int(distance / 0.5)
        if steps < 1:
            steps = 1

        step_x = dx / steps
        step_y = dy / steps
        step_z = dz / steps

        step_distance = distance / steps
        delay = (step_distance / self.feedrate) * 60.0

        for i in range(steps):

            if self.stop_requested:
                break

            self.machine_x += step_x
            self.machine_y += step_y
            self.machine_z += step_z

            # update viewer (machine coordinate)
            self.ui.openGLWidget.update_position(
                self.machine_x,
                self.machine_y,
                self.machine_z
            )

            # -------- WORK COORDINATE --------
            wx = self.machine_x - self.work_offset_x
            wy = self.machine_y - self.work_offset_y
            wz = self.machine_z - self.work_offset_z

            self.ui.lcdNumber.display(round(wx,2))
            self.ui.lcdNumber_2.display(round(wy,2))
            self.ui.lcdNumber_3.display(round(wz,2))

            QtWidgets.QApplication.processEvents()
            time.sleep(delay)

        if not self.stop_requested:

            self.machine_x = target_x
            self.machine_y = target_y
            self.machine_z = target_z
            segment = self.calc_distance(
                start_x,start_y,start_z,
                target_x,target_y,target_z
            )

            self.executed_path += segment

            self.remaining_path = max(
                self.total_path - self.executed_path,
                0
            )

            if self.total_path > 0:
                self.progress = min((self.executed_path/self.total_path)*100,100)
            else:
                self.progress = 0
            # ⭐ update info window
            self.ui.infoWindow.progressLabel.setText(str(round(self.progress,2)))
            self.ui.infoWindow.execLabel.setText(str(round(self.executed_path,2)))
            self.ui.infoWindow.remainLabel.setText(str(round(self.remaining_path,2)))
            self.planner_x = target_x
            self.planner_y = target_y
            self.planner_z = target_z
#--------------------------------------------------#
    def move_arc(self, line):

        cw = line.startswith(("G2","G02"))

        coords = re.findall(r'[XYIJ]-?\d*\.?\d+', line)

        target_x = self.machine_x
        target_y = self.machine_y

        i = 0.0
        j = 0.0
        
        for c in coords:

            if c.startswith("X"):
                target_x = float(c[1:]) + self.work_offset_x

            elif c.startswith("Y"):
                target_y = float(c[1:]) + self.work_offset_y

            elif c.startswith("I"):
                i = float(c[1:])

            elif c.startswith("J"):
                j = float(c[1:])

        start_x = self.machine_x
        start_y = self.machine_y

        center_x = start_x + i
        center_y = start_y + j

        radius = math.sqrt(i*i + j*j)

        start_angle = math.atan2(start_y-center_y,start_x-center_x)
        end_angle = math.atan2(target_y-center_y,target_x-center_x)

        if cw:

            if start_angle <= end_angle:
                start_angle += 2*math.pi

            arc_angle = start_angle - end_angle

        else:

            if end_angle <= start_angle:
                end_angle += 2*math.pi

            arc_angle = end_angle - start_angle

        steps = int(abs(arc_angle)*radius/0.2)
        chord = 0.2
        arc_length = radius * abs(arc_angle)
        steps = int(arc_length / chord)
        if steps < 15:
            steps = 15

        angle_step = arc_angle/steps

        for s in range(steps+1):

            if self.stop_requested:
                break

            if cw:
                current_angle = start_angle - (s*angle_step)
            else:
                current_angle = start_angle + (s*angle_step)

            x = center_x + radius*math.cos(current_angle)
            y = center_y + radius*math.sin(current_angle)

            self.machine_x = x
            self.machine_y = y

            self.ui.openGLWidget.update_position(
                self.machine_x,
                self.machine_y,
                self.machine_z,
                is_arc=True
            )

            wx = self.machine_x - self.work_offset_x
            wy = self.machine_y - self.work_offset_y

            self.ui.lcdNumber.display(round(wx,2))
            self.ui.lcdNumber_2.display(round(wy,2))

            QtWidgets.QApplication.processEvents()
            QtCore.QThread.msleep(5)
        self.executed_path += arc_length

        self.remaining_path = max(
            self.total_path - self.executed_path,
            0
        )

        if self.total_path > 0:
            self.progress = min((self.executed_path/self.total_path)*100,100)
        else:
            self.progress = 0
        self.machine_x = target_x
        self.machine_y = target_y
    
    def highlight_line(self, line_number):
        extra_selections = []

        selection = QTextEdit.ExtraSelection()
        selection.format.setBackground(QColor("yellow"))
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)

        cursor = self.textEdit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, line_number)

        selection.cursor = cursor
        extra_selections.append(selection)

        self.textEdit.setExtraSelections(extra_selections)

    def start_execution(self):
        self.set_state("RUN")
        text = self.textEdit.toPlainText()
        if not text.strip():
            self.set_state("STOP", "ไม่มี G-code ให้รัน")
            return
        self.stop_requested = False
        self.lines = text.splitlines()
        self.current_line_index = 0

        self.calculate_total_path()
        self.executed_path = 0
        self.remaining_path = self.total_path

        if self.timer:
            self.timer.stop()
            
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.execute_line)
        self.timer.start(500)  # 0.5 วินาที
        self.set_state("RUN", "กำลังรัน G-code...")

    def execute_line(self):
        if self.current_line_index < len(self.lines):
            # Highlight บรรทัดที่กำลังทำงานใน UI
            self.highlight_line(self.current_line_index)
            
            command = self.lines[self.current_line_index].strip().upper()

            # 1. ข้ามบรรทัดว่าง หรือ Comment (;)
            if not command or command.startswith(';'):
                self.current_line_index += 1
                return

            # 2. จัดการคำสั่ง Modal (G17, G20, G90 ฯลฯ) ให้ข้ามไปแต่ส่งเข้า Serial ด้วยถ้าจำเป็น
            if command.startswith(("G17","G18","G19","G20","G21","G90","G91")):
                self.send_to_serial(command)
                self.current_line_index += 1
                return

            # 3. จัดการคำสั่ง M และ T (Spindle / Tool Change)
            if command.startswith(("M","T")):
                self.send_to_serial(command)
                self.current_line_index += 1
                return

            # 4. PARSE MOTION: ดึงพิกัด X Y Z จาก G-code (Work Coordinates)
            # ตรวจสอบว่าเป็นคำสั่งเคลื่อนที่ (G0, G1, G2, G3) หรือไม่
            if not any(cmd in command for cmd in ["G0", "G1", "G2", "G3", "G00", "G01", "G02", "G03"]):
                self.current_line_index += 1
                return

            wx, wy, wz = self.parse_motion(command)
            # lock axis ที่ไม่ได้อยู่ใน G-code
            if "X" not in command:
                wx = self.machine_x - self.work_offset_x

            if "Y" not in command:
                wy = self.machine_y - self.work_offset_y

            if "Z" not in command:
                wz = self.machine_z - self.work_offset_z
            self.update_info(command, wx, wy, wz)


            mx = wx + self.work_offset_x
            my = wy + self.work_offset_y
            mz = wz + self.work_offset_z
            # 

            # 6. ประมวลผลการเคลื่อนที่
            if command.startswith(('G2','G3','G02','G03')):
                # การเคลื่อนที่แบบส่วนโค้ง
                self.move_arc(command)
                self.send_to_serial(command)
            
            elif command.startswith(('G0','G1','G00','G01')):
                # การเคลื่อนที่แบบเส้นตรง (Linear)
                self.move_linear(mx, my, mz)
                self.send_to_serial(command)

            self.current_line_index += 1

        else:
            # จบการทำงาน
            self.timer.stop()
            self.progress = 100
            self.remaining_path = 0
            self.ui.infoWindow.progressLabel.setText("100")
            self.ui.infoWindow.remainLabel.setText("0")
            self.textEdit.setExtraSelections([])
            self.set_state("IDLE", "โปรแกรมทำงานเสร็จสิ้น")

    def send_to_serial(self, command):
        """ ฟังก์ชันแยกสำหรับส่งข้อมูลออก Serial Port """
        if not command.endswith(';'):
            command += ';'

        if self.serial and self.serial.isOpen():
            try:
                self.serial.write((command + '\n').encode())
                self.set_state("RUN", f"ส่ง: {command}")
                
                # รอการตอบกลับสั้นๆ เพื่อไม่ให้ Buffer เต็ม
                time.sleep(0.01) 
                if self.serial.in_waiting > 0:
                    response = self.serial.readline().decode().strip()
                    if response:
                        print(f"Arduino Response: {response}")
            except Exception as e:
                self.set_state("STOP", f"Serial Error: {str(e)}")
                self.timer.stop()
