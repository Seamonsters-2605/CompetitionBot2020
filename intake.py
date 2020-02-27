import wpilib, rev

class Intake:

    # pistonNums should be a list of length 4
    # the first 2 values for one piston and the
    # other 2 values for the other piston
    def __init__(self, sparkNum, pistonNum1, pistonNum2):

        self.piston = wpilib.DoubleSolenoid(pistonNum1, pistonNum2)

        motor = rev.CANSparkMax(sparkNum, rev.CANSparkMax.MotorType.kBrushless)
        motor.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.motorController = motor.getPIDController()
        self.encoder = motor.getEncoder()

        self.running = False
        self.reversed = False
        self.deployed = False

        self.stop()
        self.retract()

    # Piston Functions:

    # pushes out the pistons
    def deploy(self):
        self.deployed = True
        self.piston.set(wpilib.DoubleSolenoid.Value.kForward)

    # pulls in the pistons
    def retract(self):
        self.deployed = False
        self.piston.set(wpilib.DoubleSolenoid.Value.kReverse)

    # switches between in and out
    def toggleIntake(self):
        if self.deployed:
            self.retract()
        else:
            self.deploy()

    # Motor functions:

    # spins the motor forwards
    def spinForwards(self):
        self.reversed = False
        self.running = True
        
    # spins the motor backwards
    def spinReversed(self):
        self.reversed = True
        self.running = True

    # stops the motor
    def stop(self):
        self.running = False

    # starts the motor
    def start(self):
        self.running = True

    # this is a generator, should be called every iteration
    def run(self):

        while True:

            if self.running:
                if self.reversed:
                    motorSpeed = -10_000
                else:
                    motorSpeed = 10_000
            else:
                motorSpeed = 0

            # drives the motor
            self.motorController.setReference(motorSpeed, rev.ControlType.kVelocity)

            yield

    # toggles between spinning and not spinning each time it is called
    def toggleMotor(self):
        self.running = not self.running