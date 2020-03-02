import wpilib, rev

class Indexer:

    def __init__(self, motorNum1, motorNum2):
        self.motor1 = rev.CANSparkMax(motorNum1, rev.CANSparkMax.MotorType.kBrushless)
        self.motor2 = rev.CANSparkMax(motorNum2, rev.CANSparkMax.MotorType.kBrushless)

        self.running = False

    # Motor Functions:

    # should be called 50 times a second for speed adjustment
    def run(self):
        speed = 0

        if self.running:
            speed = 1

        for motor in [self.motor1, self.motor2]:
            motor.set(speed)

    # stops the motors
    def stop(self):
        self.running = False

    # turns the motors on or off
    def toggleMotors(self):
        self.running = not self.running