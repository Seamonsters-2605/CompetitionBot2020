import math

class DriveGear:

    def __init__(self, name, driveMode, gearRatio, moveScale, turnScale,
                 p=0.0, i=0.0, d=0.0, f=0.0, realTime=True):
        self.name = name
        self.driveMode = driveMode
        self.moveScale = moveScale
        self.turnScale = turnScale
        self.gearRatio = gearRatio
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
            wheel.driveMode = self.driveMode
            wheel.realTime = self.realTime
            wheel.gearRatio = self.gearRatio
            wheel.encoderCountsPerFoot = math.pi / (self.gearRatio * wheel.circumference) 
            for motorController in wheel.motorControllers:
                motorController.setP(self.p)
                motorController.setI(self.i)
                motorController.setD(self.d)
                motorController.setFF(self.f)
        return True
