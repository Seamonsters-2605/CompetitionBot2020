import wpilib, rev

class Indexer:

    def __init__(self, motorNum1, motorNum2):
        self.motor1 = rev.CANSparkMax(motorNum1, rev.CANSparkMax.MotorType.kBrushless)
        self.motor2 = rev.CANSparkMax(motorNum2, rev.CANSparkMax.MotorType.kBrushless)

    # Motor Functions:

    # runs the motors to hold the balls inside
    def spinSlow(self):
        for motor in [self.motor1, self.motor2]:
            # this needs to be adjusted
            motor.set(0.5)

    # runs the motors to get them into the shooter
    def spinFast(self):
        for motor in [self.motor1, self.motor2]:
            # this needs to be adjusted
            motor.set(1)

    # stops the motors
    def stop(self):
        for motor in [self.motor1, self.motor2]:
            motor.set(0)