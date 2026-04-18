from PyQt5 import QtWidgets


class InfoWindow(QtWidgets.QDialog):

    def __init__(self,parent=None):

        super().__init__(parent)

        self.setWindowTitle("G-Code Calculation Info")
        self.resize(420,600)

        mainLayout = QtWidgets.QVBoxLayout(self)

        # -------------------------
        # LINE LABEL
        # -------------------------

        self.commandLabel = QtWidgets.QLabel("คำสั่งที่กำลังประมวลผล : -")
        self.commandLabel.setStyleSheet("font: bold 10pt 'Segoe UI'")
        mainLayout.addWidget(self.commandLabel)

        # -------------------------
        # PROGRESS SECTION
        # -------------------------

        self.progressBox = QtWidgets.QGroupBox("PROGRESS")
        self.progressBox.setStyleSheet("font: bold 11pt 'Segoe UI';color: rgb(0, 120, 0);")
        mainLayout.addWidget(self.progressBox)

        progressLayout = QtWidgets.QGridLayout(self.progressBox)

        self.progressLabel = QtWidgets.QLabel("-")
        self.execLabel = QtWidgets.QLabel("-")
        self.remainLabel = QtWidgets.QLabel("-")

        progressLayout.addWidget(QtWidgets.QLabel("Progress"),0,0)
        progressLayout.addWidget(self.progressLabel,0,1)
        progressLayout.addWidget(QtWidgets.QLabel("%"),0,2)

        progressLayout.addWidget(QtWidgets.QLabel("Executed Path"),1,0)
        progressLayout.addWidget(self.execLabel,1,1)
        progressLayout.addWidget(QtWidgets.QLabel("mm"),1,2)

        progressLayout.addWidget(QtWidgets.QLabel("Remaining Path"),2,0)
        progressLayout.addWidget(self.remainLabel,2,1)
        progressLayout.addWidget(QtWidgets.QLabel("mm"),2,2)

        # -------------------------
        # POSITION SECTION
        # -------------------------

        self.positionBox = QtWidgets.QGroupBox("POSITION")
        self.positionBox.setStyleSheet("font: bold 11pt 'Segoe UI'")
        mainLayout.addWidget(self.positionBox)

        posLayout = QtWidgets.QGridLayout(self.positionBox)

        self.startX = QtWidgets.QLabel("-")
        self.startY = QtWidgets.QLabel("-")
        self.startZ = QtWidgets.QLabel("-")

        self.targetX = QtWidgets.QLabel("-")
        self.targetY = QtWidgets.QLabel("-")
        self.targetZ = QtWidgets.QLabel("-")

        self.distance = QtWidgets.QLabel("-")

        posLayout.addWidget(QtWidgets.QLabel("Start X"),0,0)
        posLayout.addWidget(self.startX,0,1)
        posLayout.addWidget(QtWidgets.QLabel("mm"),0,2)

        posLayout.addWidget(QtWidgets.QLabel("Start Y"),1,0)
        posLayout.addWidget(self.startY,1,1)
        posLayout.addWidget(QtWidgets.QLabel("mm"),1,2)

        posLayout.addWidget(QtWidgets.QLabel("Start Z"),2,0)
        posLayout.addWidget(self.startZ,2,1)
        posLayout.addWidget(QtWidgets.QLabel("mm"),2,2)

        posLayout.addWidget(QtWidgets.QLabel("Target X"),3,0)
        posLayout.addWidget(self.targetX,3,1)
        posLayout.addWidget(QtWidgets.QLabel("mm"),3,2)

        posLayout.addWidget(QtWidgets.QLabel("Target Y"),4,0)
        posLayout.addWidget(self.targetY,4,1)
        posLayout.addWidget(QtWidgets.QLabel("mm"),4,2)

        posLayout.addWidget(QtWidgets.QLabel("Target Z"),5,0)
        posLayout.addWidget(self.targetZ,5,1)
        posLayout.addWidget(QtWidgets.QLabel("mm"),5,2)

        posLayout.addWidget(QtWidgets.QLabel("Distance"),6,0)
        posLayout.addWidget(self.distance,6,1)
        posLayout.addWidget(QtWidgets.QLabel("mm"),6,2)

        # -------------------------
        # MOTION SECTION
        # -------------------------
        self.motionBox = QtWidgets.QGroupBox("MOTION")
        self.motionBox.setStyleSheet("font: bold 11pt 'Segoe UI'")
        mainLayout.addWidget(self.motionBox)

        motionLayout = QtWidgets.QGridLayout(self.motionBox)

        # ---- LABELS ----
        self.feedLabel = QtWidgets.QLabel("-")
        self.speedLabel = QtWidgets.QLabel("-")
        self.timeLabel = QtWidgets.QLabel("-")
        self.stepLabel = QtWidgets.QLabel("-")
        self.stepFreqLabel = QtWidgets.QLabel("-")
        self.rpmLabel = QtWidgets.QLabel("-")
        self.accelLabel = QtWidgets.QLabel("-")
        self.limitLabel = QtWidgets.QLabel("-")

        # ---- FEEDRATE ----
        motionLayout.addWidget(QtWidgets.QLabel("Feedrate"),0,0)
        motionLayout.addWidget(self.feedLabel,0,1)
        motionLayout.addWidget(QtWidgets.QLabel("mm/min"),0,2)

        # ---- SPEED ----
        motionLayout.addWidget(QtWidgets.QLabel("Speed"),1,0)
        motionLayout.addWidget(self.speedLabel,1,1)
        motionLayout.addWidget(QtWidgets.QLabel("mm/sec"),1,2)

        # ---- TIME ----
        motionLayout.addWidget(QtWidgets.QLabel("Time"),2,0)
        motionLayout.addWidget(self.timeLabel,2,1)
        motionLayout.addWidget(QtWidgets.QLabel("sec"),2,2)

        # ---- STEPS ----
        motionLayout.addWidget(QtWidgets.QLabel("Steps"),3,0)
        motionLayout.addWidget(self.stepLabel,3,1)
        motionLayout.addWidget(QtWidgets.QLabel("steps"),3,2)

        # ---- STEP FREQUENCY ----
        motionLayout.addWidget(QtWidgets.QLabel("Step Frequency"),4,0)
        motionLayout.addWidget(self.stepFreqLabel,4,1)
        motionLayout.addWidget(QtWidgets.QLabel("steps/sec"),4,2)

        # ---- MOTOR RPM ----
        motionLayout.addWidget(QtWidgets.QLabel("Motor RPM"),5,0)
        motionLayout.addWidget(self.rpmLabel,5,1)
        motionLayout.addWidget(QtWidgets.QLabel("rpm"),5,2)
        # ---- ACCELERATION ----
        self.accelerationLabel = QtWidgets.QLabel("-")

        motionLayout.addWidget(QtWidgets.QLabel("Acceleration"),6,0)
        motionLayout.addWidget(self.accelerationLabel,6,1)
        motionLayout.addWidget(QtWidgets.QLabel("mm/sec²"),6,2)
        # ---- ACCEL TIME ----
        motionLayout.addWidget(QtWidgets.QLabel("Accel Time"),7,0)
        motionLayout.addWidget(self.accelLabel,7,1)
        motionLayout.addWidget(QtWidgets.QLabel("sec"),7,2)

        # ---- ACCEL DISTANCE ----
        self.accelDistLabel = QtWidgets.QLabel("-")

        motionLayout.addWidget(QtWidgets.QLabel("Accel Distance"),8,0)
        motionLayout.addWidget(self.accelDistLabel,8,1)
        motionLayout.addWidget(QtWidgets.QLabel("mm"),8,2)

        # ---- SPEED LIMIT ----
        motionLayout.addWidget(QtWidgets.QLabel("Speed Limit"),9,0)
        motionLayout.addWidget(self.limitLabel,9,1)
        motionLayout.addWidget(QtWidgets.QLabel("status"),9,2)
        # -------------------------
        # ARC SECTION
        # -------------------------

        self.arcBox = QtWidgets.QGroupBox("ARC INFO")
        self.arcBox.setStyleSheet("font: bold 11pt 'Segoe UI'")
        mainLayout.addWidget(self.arcBox)

        arcLayout = QtWidgets.QGridLayout(self.arcBox)

        self.arcCenterX = QtWidgets.QLabel("-")
        self.arcCenterY = QtWidgets.QLabel("-")
        self.arcRadius = QtWidgets.QLabel("-")
        self.arcLength = QtWidgets.QLabel("-")

        arcLayout.addWidget(QtWidgets.QLabel("Center X"),0,0)
        arcLayout.addWidget(self.arcCenterX,0,1)

        arcLayout.addWidget(QtWidgets.QLabel("Center Y"),1,0)
        arcLayout.addWidget(self.arcCenterY,1,1)

        arcLayout.addWidget(QtWidgets.QLabel("Radius"),2,0)
        arcLayout.addWidget(self.arcRadius,2,1)

        arcLayout.addWidget(QtWidgets.QLabel("Arc Length"),3,0)
        arcLayout.addWidget(self.arcLength,3,1)
        self.arcSegments = QtWidgets.QLabel("-")

        arcLayout.addWidget(QtWidgets.QLabel("Segments"),4,0)
        arcLayout.addWidget(self.arcSegments,4,1)
