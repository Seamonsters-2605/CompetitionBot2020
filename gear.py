class DriveGear:

    def __init__(self, name, driveMode, moveScale, turnScale,
                 p=0.0, i=0.0, d=0.0, f=0.0, realTime=True):
        self.name = name
        self.driveMode = driveMode
        self.moveScale = moveScale
        self.turnScale = turnScale
        self.p = p
        self.i = i
        self.d = d
        self.f = f
        self.realTime = realTime

    def __repr__(self):
        return self.name

    def applyGear(self, superDrive):
        if superDrive.gear == self:
            return False
        print("Set gear to", self)
        superDrive.gear = self # not a normal property of the superDrive
        for wheel in superDrive.wheels:
            wheel.angledWheel.driveMode = self.driveMode
            wheel.angledWheel.realTime = self.realTime
            wheelMotorController = wheel.angledWheel.motorController
            wheelMotorController.setP(0, self.p, 0)
            wheelMotorController.setI(0, self.i, 0)
            wheelMotorController.setD(0, self.d, 0)
            wheelMotorController.setFF(0, self.f, 0)
        return True
