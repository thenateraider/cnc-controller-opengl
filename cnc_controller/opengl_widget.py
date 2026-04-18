from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import Qt
import OpenGL.GL as gl
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import re
import math


class MyOpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(MyOpenGLWidget, self).__init__(parent)
        self.gcode_lines = []
        self.vertices = []
        self.arcs = []
        self.last_mouse_position = None
        self.rotation_x = 0  # มุมมอง 
        self.rotation_y = 0
        self.zoom_level = -40.0  # ซูมเข้าใกล้
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.setFocusPolicy(Qt.StrongFocus)
        self.cnc = None
        self.segments = []
        self.last_segment_index = -1
        self.active_axis = None

        # ตำแหน่งปัจจุบันของเครื่อง (mm)
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_z = 0.0
        
        # ขนาดพื้นที่ทำงาน CNC 3018 (mm)
        self.bed_width = 300.0   # X
        self.bed_depth = 180.0   # Y
        self.bed_height = 40.0   # Z
        
        # เส้นทางที่วาดไปแล้ว
        self.drawn_path = []
        # การเน้นเส้น
        self.segments = []          # เก็บเส้นแต่ละช่วง
        self.current_axis = None    # แกนที่กำลังวาด
        self.last_pos = (0,0,0)

        self.draw_enabled = True


       
    def load_gcode(self, gcode):
        """โหลด G-code และ parse"""
        self.gcode_lines = gcode.split('\n')
        self.vertices = []
        self.arcs = []
        self.drawn_path = []
        self.parse_gcode()
        self.update()
    def parse_gcode(self):

        """แปลง G-code เป็น vertices และ arcs สำหรับ viewer"""

        x = 0
        y = 0
        z = 0

        self.vertices = []
        self.arcs = []

        for line in self.gcode_lines:

            line = line.strip().upper()

            if not line or line.startswith(';'):
                continue

            if line.endswith(';'):
                line = line[:-1].strip()

            # -------------------------
            # LINEAR MOVE
            # -------------------------

            if line.startswith(('G0','G1','G00','G01')):

                coords = re.findall(r'[XYZ]-?\d*\.?\d+', line)

                temp_x, temp_y, temp_z = x, y, z

                for coord in coords:

                    if coord.startswith('X'):
                        temp_x = float(coord[1:])

                    elif coord.startswith('Y'):
                        temp_y = float(coord[1:])

                    elif coord.startswith('Z'):
                        temp_z = float(coord[1:])

                start = (x, y, z)

                x, y, z = temp_x, temp_y, temp_z

                end = (x, y, z)

                self.vertices.append(end)

            # -------------------------
            # ARC MOVE
            # -------------------------

            elif line.startswith(('G2','G3','G02','G03')):

                cw = line.startswith(('G2','G02'))

                coords = re.findall(r'[XYZIJ]-?\d*\.?\d+', line)

                temp_x, temp_y = x, y

                i = 0.0
                j = 0.0

                for coord in coords:

                    if coord.startswith('X'):
                        temp_x = float(coord[1:])

                    elif coord.startswith('Y'):
                        temp_y = float(coord[1:])

                    elif coord.startswith('I'):
                        i = float(coord[1:])

                    elif coord.startswith('J'):
                        j = float(coord[1:])

                # จุดเริ่ม arc
                if len(self.vertices) > 0:
                    start = self.vertices[-1]
                else:
                    start = (x, y, z)

                # จุดจบ arc
                end = (temp_x, temp_y, z)

                # เก็บ arc
                self.arcs.append((start, end, i, j, cw))

                # เพิ่ม vertex ปลาย
                self.vertices.append(end)

                print("ARC PARSED:", start, end, i, j, cw)

                x, y = temp_x, temp_y
    def update_position(self, x, y, z, is_arc=False):

        if not self.cnc:
            return

        # MACHINE → WORK
        wx = x - self.cnc.work_offset_x
        wy = y - self.cnc.work_offset_y
        wz = z - self.cnc.work_offset_z

        start = (
            self.last_pos[0] - self.cnc.work_offset_x,
            self.last_pos[1] - self.cnc.work_offset_y,
            self.last_pos[2] - self.cnc.work_offset_z
        )

        new_pos = (wx, wy, wz)

        if start == new_pos:
            return

        # UPDATE TOOL POSITION
        self.current_x = x
        self.current_y = y
        self.current_z = z

        if self.draw_enabled:

            dx = abs(new_pos[0] - start[0])
            dy = abs(new_pos[1] - start[1])
            dz = abs(new_pos[2] - start[2])

            axis = None

            if dx >= dy and dx >= dz:
                axis = "X"
            elif dy >= dx and dy >= dz:
                axis = "Y"
            else:
                axis = "Z"

            # เก็บ segment
            self.segments.append((start, new_pos, axis))

            # ⭐ สำคัญ
            self.active_axis = axis

        self.last_pos = (x, y, z)

        self.update()
    def draw_text(self, x, y, z, text):
        glRasterPos3f(x, y, z)
        for ch in text:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    def initializeGL(self):
        glutInit()
        glClearColor(0.15, 0.15, 0.15, 1.0)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glLineWidth(3)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / h if h != 0 else 1
        gluPerspective(45.0, aspect, 0.01, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def draw_cnc_bed(self):
        """วาดฐาน CNC 3018"""
        w = self.bed_width / 10.0
        d = self.bed_depth / 10.0
        h = self.bed_height / 10.0
        
        # ป้องกัน Z-fighting
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(1.0, 1.0)

        # ฐาน (สีเทา)
        glColor4f(0.3, 0.3, 0.3, 0.8)
        glBegin(GL_QUADS)
        glVertex3f(0, 0, 0)
        glVertex3f(w, 0, 0)
        glVertex3f(w, d, 0)
        glVertex3f(0, d, 0)
        glEnd()

        glDisable(GL_POLYGON_OFFSET_FILL)
        
        # เส้นขอบฐาน
        glColor3f(0.6, 0.6, 0.6)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(0, 0, 0)
        glVertex3f(w, 0, 0)
        glVertex3f(w, d, 0)
        glVertex3f(0, d, 0)
        glEnd()
        
        # เส้นกริด
        glColor3f(0.4, 0.4, 0.4)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        
        for i in range(1, int(d/2)):
            y = i * 2.0
            glVertex3f(0, y, 0)
            glVertex3f(w, y, 0)

        for i in range(1, int(w/2)):
            x = i * 2.0
            glVertex3f(x, 0, 0)
            glVertex3f(x, d, 0)

        glEnd()
    
    def draw_axes(self):
        """วาดแกน XYZ ที่มุมซ้ายล่าง ห่างจากโต๊ะ"""
        offset = -5.0  # เลื่อนออกมาจากขอบโต๊ะ
        length = 8.0   # ความยาวลูกศร
        
        glLineWidth(4.0)
        glBegin(GL_LINES)
        # แกน X (แดง)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(offset, offset, 0)
        glVertex3f(offset + length, offset, 0)
        # แกน Y (เขียว)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(offset, offset, 0)
        glVertex3f(offset, offset + length, 0)
        # แกน Z (น้ำเงิน)
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(offset, offset, 0)
        glVertex3f(offset, offset, length)
        glEnd()
        
        # หัวลูกศร
        glPointSize(10.0)
        glBegin(GL_POINTS)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(offset + length, offset, 0)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(offset, offset + length, 0)
        glColor3f(0.0, 0.5, 1.0)
        glVertex3f(offset, offset, length)
        glEnd()

        # ---- Axis Labels ----
        glColor3f(1.0, 0.0, 0.0)
        self.draw_text(offset + length + 0.5, offset, 0, "X")

        glColor3f(0.0, 1.0, 0.0)
        self.draw_text(offset, offset + length + 0.5, 0, "Y")

        glColor3f(0.0, 0.5, 1.0)
        self.draw_text(offset, offset, length + 0.5, "Z")
    def draw_work_origin(self):

        if not self.cnc:
            return

        ox = self.cnc.work_offset_x / 10.0
        oy = self.cnc.work_offset_y / 10.0
        oz = self.cnc.work_offset_z / 10.0

        glColor3f(1,1,0)
        glPointSize(10)

        glBegin(GL_POINTS)
        glVertex3f(ox, oy, oz)
        glEnd()

        glColor3f(1,1,0)
        self.draw_text(ox+0.3, oy, oz+0.3, "W0")

    def draw_tool_head(self):
        """วาดหัวเครื่องมือ (tool head) ที่ตำแหน่งปัจจุบัน"""
        x = self.current_x / 10
        y = self.current_y / 10
        z = self.current_z / 10
        
        # วาดแท่งแกน Z (สีเทาอ่อน)
        glColor3f(0.7, 0.7, 0.7)
        glLineWidth(4.0)
        glBegin(GL_LINES)
        tool_offset = 0.03
        glVertex3f(x, y, 0 + tool_offset)
        glVertex3f(x, y, z + tool_offset)
        glEnd()
        
        # วาดหัวเครื่องมือ (สีส้ม)
        glColor3f(1.0, 0.5, 0.0)
        glPointSize(12.0)
        glBegin(GL_POINTS)
        glVertex3f(x, y, z + tool_offset)
        glEnd()
        
        # วาดวงกลมรอบหัวเครื่องมือ
        glColor4f(1.0, 0.5, 0.0, 0.3)
        glBegin(GL_LINE_LOOP)
        for i in range(20):
            angle = 2.0 * math.pi * i / 20
            cx = x + 0.5 * math.cos(angle)
            cy = y + 0.5 * math.sin(angle)
            glVertex3f(cx, cy, z)
        glEnd()

    def draw_toolpath(self):

        if not self.cnc:
            return

        if len(self.vertices) < 2:
            return

        z_offset = 0.02

        glColor4f(0.5, 1, 0.0, 1.0)
        glLineWidth(2.0)

        glBegin(GL_LINE_STRIP)

        for vertex in self.vertices:

            # vertex = WORK coordinate
            wx, wy, wz = vertex

            # convert → MACHINE
            mx = wx + self.cnc.work_offset_x
            my = wy + self.cnc.work_offset_y
            mz = wz + self.cnc.work_offset_z

            glVertex3f(
                mx / 10.0,
                my / 10.0,
                mz / 10.0 + z_offset
            )

        glEnd()

    # 3. แก้ไขการวาดเส้นที่วิ่งไปแล้ว (Completed Path)
    def draw_completed_path(self):

        if not self.cnc:
            return

        z_offset = 0.02
        active = self.active_axis

        ox = self.cnc.work_offset_x
        oy = self.cnc.work_offset_y
        oz = self.cnc.work_offset_z

        for start, end, axis in self.segments:

            color = (0,1,1)
            width = 2

            if axis == active:
                width = 4
                if axis == "X": color = (1,0,0)
                elif axis == "Y": color = (0,1,0)
                elif axis == "Z": color = (0,0,1)

            glColor3f(*color)
            glLineWidth(width)

            # convert WORK -> MACHINE
            sx = (start[0] + ox) / 10.0
            sy = (start[1] + oy) / 10.0
            sz = (start[2] + oz) / 10.0 + z_offset

            ex = (end[0] + ox) / 10.0
            ey = (end[1] + oy) / 10.0
            ez = (end[2] + oz) / 10.0 + z_offset

            glBegin(GL_LINES)
            glVertex3f(sx,sy,sz)
            glVertex3f(ex,ey,ez)
            glEnd()
    def paintGL(self):

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.pan_x, self.pan_y, self.zoom_level)

        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)

        # center bed
        glTranslatef(-15, -9, 0)

        self.draw_cnc_bed()
        self.draw_axes()
        self.draw_work_origin()
        self.draw_toolpath()
        self.draw_completed_path()
        self.draw_tool_head()

        if not self.cnc:
            return

        ox = self.cnc.work_offset_x
        oy = self.cnc.work_offset_y
        oz = self.cnc.work_offset_z

        # ---------------- ARC DRAW ----------------
        for arc_data in self.arcs:

            start_vertex, end_vertex, i, j, cw = arc_data

            centerX = start_vertex[0] + i
            centerY = start_vertex[1] + j

            radius = math.sqrt(i*i + j*j)

            startAngle = math.atan2(
                start_vertex[1] - centerY,
                start_vertex[0] - centerX
            )

            endAngle = math.atan2(
                end_vertex[1] - centerY,
                end_vertex[0] - centerX
            )

            diff = endAngle - startAngle

            if cw:
                if diff >= 0:
                    diff -= 2 * math.pi
            else:
                if diff <= 0:
                    diff += 2 * math.pi

            arc_length = radius * abs(diff)
            steps = int(arc_length / 0.2)

            if steps < 20:
                steps = 20
            angle_step = diff / steps

            glColor4f(1.0, 0.0, 0.0, 1.0)
            glLineWidth(3.0)

            glBegin(GL_LINE_STRIP)

            for s in range(steps + 1):

                angle = startAngle + (s * angle_step)

                xPos = centerX + radius * math.cos(angle)
                yPos = centerY + radius * math.sin(angle)

                mx = xPos + self.cnc.work_offset_x
                my = yPos + self.cnc.work_offset_y
                mz = start_vertex[2] + self.cnc.work_offset_z

                glVertex3f(
                    mx / 10.0,
                    my / 10.0,
                    mz / 10.0 + 0.02
                )

            glEnd() 
    def mousePressEvent(self, event):
        self.last_mouse_position = event.pos()
        self.mouse_button = event.button()

    def mouseMoveEvent(self, event):
        if self.last_mouse_position:
            dx = event.x() - self.last_mouse_position.x()
            dy = event.y() - self.last_mouse_position.y()

            if self.mouse_button == Qt.LeftButton:
                # PAN
                self.pan_x += dx * 0.05
                self.pan_y -= dy * 0.05

            elif self.mouse_button == Qt.RightButton:
                # ROTATE
                self.rotation_x += dy * 0.5
                self.rotation_y += dx * 0.5

            self.last_mouse_position = event.pos()
            self.update()
    def wheelEvent(self, event):
        delta = event.angleDelta().y()

        zoom_speed = 0.01
        self.zoom_level += delta * zoom_speed

        # จำกัดระยะ
        self.zoom_level = max(-200, min(-5, self.zoom_level))

        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.pan_x += 2
        elif event.key() == Qt.Key_Right:
            self.pan_x -= 2
        elif event.key() == Qt.Key_Up:
            self.pan_y -= 2
        elif event.key() == Qt.Key_Down:
            self.pan_y += 2
        self.update()
