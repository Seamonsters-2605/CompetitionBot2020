import wpilib, rev
from rev.color import ColorSensorV3

PROXIMITY_THRESH = 350
ROTATIONS_PER_BALL = 100

class Indexer:

    def __init__(self, indexerMotorNum, kickerWheelMotorNum):

        self.indexerMotor = rev.CANSparkMax(indexerMotorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.indexerMotor.setIdleMode(rev.CANSparkMax.IdleMode.kBrake)
        self.indexerEncoder = self.indexerMotor.getEncoder()

        self.kickerWheel = rev.CANSparkMax(kickerWheelMotorNum, rev.CANSparkMax.MotorType.kBrushless)

        # used for proximity sensing
        try:
            self.sensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)
        except:
            pass # crashes in the sim, don't worry about it

        self.running = False
        self.reversed = False

        self.balls = 3

    # generator to run the indexer when it detects a ball
    def runGenerator(self):
        
        self.indexerEncoder.setPosition(0)

        while True:

            if not self.running:

                proximity = self.sensor.getProximity()
                
                if proximity > PROXIMITY_THRESH:

                    for _ in range(8):
                        yield

                    proximity = self.sensor.getProximity()

                    self.indexerEncoder.setPosition(0)

                    if proximity > PROXIMITY_THRESH:

                        while self.indexerEncoder.getPosition() < ROTATIONS_PER_BALL:

                            self.running = True
                            reversed = False
                            self.indexerMotor.set(0.8)
                            self.kickerWheel.set(0.8)
                            
                    self.balls += 1
                    self.stop()

            yield

    # starts the motors to move the balls
    def start(self):
        self.running = True
        reversed = False
        self.indexerMotor.set(0.8)
        self.kickerWheel.set(1)
        self.balls = 0

    def reverse(self):
        self.running = True
        reversed = False
        self.indexerMotor.set(-0.8)
        self.kickerWheel.set(-1)

    # stops the motors
    def stop(self):
        self.running = False
        self.indexerMotor.set(0)
        self.kickerWheel.set(1)

    # turns the motors on or off
    def toggleMotors(self):
        if not self.running:
            self.start()
        else:
            self.stop()