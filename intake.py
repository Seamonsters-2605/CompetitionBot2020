import wpilib, rev

class Intake:

    # pistonNums should be a list of length 4
    # the first 2 values for one piston and the
    # other 2 values for the other piston
    def __init__(self, sparkNum, pistonNums : list):

        if len(pistonNums) != 4:
            raise ValueError("pistonNums must be length 4")

        self.piston1 = wpilib.DoubleSolenoid(pistonNums[0], pistonNums[1])
        self.piston2 = wpilib.DoubleSolenoid(pistonNums[2], pistonNums[3])

        motor = rev.CANSparkMax(sparkNum, rev.CANSparkMax.MotorType.kBrushless)
        self.motorController = motor.getPIDController()

    # Piston Functions:

    # pushes out the pistons
    def deploy(self):
        for piston in [self.piston1, self.piston2]:
            piston.set(wpilib.DoubleSolenoid.Value.kForward)

    # pulls in the pistons
    def retract(self):
        for piston in [self.piston1, self.piston2]:
            piston.set(wpilib.DoubleSolenoid.Value.kReverse)

    # Motor functions:

    # spins the motor at 10,000 rpm
    def start(self):
        self.motorController.setReference(10_000, rev.ControlType.kVelocity)

    # stops the motor
    def stop(self):
        self.motorController.setReference(0, rev.ControlType.kVelocity)