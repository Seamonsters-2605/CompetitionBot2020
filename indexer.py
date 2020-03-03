import wpilib, rev
from rev.color import ColorSensorV3

PROXIMITY_THRESH = 350
ROTATIONS_PER_BALL = 100

class Indexer:

    def __init__(self, motorNum, placeHolderNum):

        self.motor = rev.CANSparkMax(motorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.motor.setIdleMode(rev.CANSparkMax.IdleMode.kBrake)
        self.encoder = self.motor.getEncoder()

        # used for proximity sensing
        self.sensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

        self.running = False

    # generator to run the indexer when it detects a ball
    def runGenerator(self):
        
        self.encoder.setPosition(0)

        while True:

            if not self.running:

                proximity = self.sensor.getProximity()
                
                if proximity > PROXIMITY_THRESH:

                    print("ball detected")
                    self.encoder.setPosition(0)

                    while self.encoder.getPosition() < ROTATIONS_PER_BALL:

                        self.start()
                    
                    self.stop()
                    print("rotation complete")

            yield

    # starts the motors to move the balls
    def start(self):
        self.running = True
        self.motor.set(1)

    # stops the motors
    def stop(self):
        self.running = False
        self.motor.set(0)

    # turns the motors on or off
    def toggleMotors(self):
        if self.running:
            self.start()
        else:
            self.stop()