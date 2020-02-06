import wpilib, rev

class Indexer:

    def __init__(self, motorNum1, motorNum2, pistonNum1, pisonNum2):

        self.piston = wpilib.DoubleSolenoid(pistonNum1, pisonNum2)

        # may need to add a third motor
        self.motor1 = rev.CANSparkMax(motorNum1, rev.CANSparkMax.MotorType.kBrushless)
        self.motor2 = rev.CANSparkMax(motorNum2, rev.CANSparkMax.MotorType.kBrushless)

    # Piston Functions:

    # extends the piston so balls stay in the indexer
    def close(self):
        self.piston.set(wpilib.DoubleSolenoid.Value.kForward)

    # releases the piston so balls can get through
    def release(self):
        self.piston.set(wpilib.DoubleSolenoid.Value.kReverse)

    # Motor Functions:

    # starts the motors to move the balls
    def start(self):
        for motor in [self.motor1, self.motor2]:
            # this needs to be adjusted
            motor.set(0.5)

    # stops the motors
    def stop(self):
        for motor in [self.motor1, self.motor2]:
            motor.set(0)