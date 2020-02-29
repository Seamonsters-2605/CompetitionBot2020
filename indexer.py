import wpilib, rev
from rev.color import ColorSensorV3

class Indexer:

    def __init__(self, motorNum):

        self.motor = rev.CANSparkMax(motorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.motorController = self.motor.getPIDController()

        # used for proximity sensing
        self.sensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

    # generator to run the indexer when it detects a ball
    def runGenerator(self):

        proximity = self.sensor.getProximity()
        color = self.sensor.getColor()

        print(proximity, color)

        yield

    # starts the motors to move the balls
    def start(self, rpm):
        
        self.motorController.setReference(rpm, rev.ControlType.kVelocity)

    # stops the motors
    def stop(self):
        self.motor.set(0)
