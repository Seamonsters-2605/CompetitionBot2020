import wpilib, rev
from rev.color import ColorSensorV3

PROXIMITY_THRESH = 350
ROTATIONS_PER_BALL = 115

class Indexer:

    def __init__(self, motorNum, placeHolderNum):

        self.motor = rev.CANSparkMax(motorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.motorController = self.motor.getPIDController()
        self.encoder = self.motor.getEncoder()

        # used for proximity sensing
        self.sensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

    # generator to run the indexer when it detects a ball
    def runGenerator(self):

        self.encoder.setPosition(0)

        while True:

            color = self.sensor.getColor()
            
            if color > PROXIMITY_THRESH:

                print("ball detected")
                self.encoder.setPosition(0)

                while self.encoder.getPosition() < ROTATIONS_PER_BALL:

                    self.motor.set(0.05)
                
                print("rotation complete")

            yield

    # starts the motors to move the balls
    def start(self, rpm):
        
        self.motorController.setReference(rpm, rev.ControlType.kVelocity)

    # stops the motors
    def stop(self):
        self.motor.set(0)
