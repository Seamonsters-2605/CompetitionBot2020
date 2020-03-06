import wpilib, rev

MOTOR_SPEED = 5_000

class Intake:
    # pistonNums should be a list of length 4
    # the first 2 values for one piston and the
    # other 2 values for the other piston
    def __init__(self, sparkNum, pistonNum1, pistonNum2):

        self.piston = wpilib.DoubleSolenoid(pistonNum1, pistonNum2)

        self.motor = rev.CANSparkMax(sparkNum, rev.CANSparkMax.MotorType.kBrushless)
        self.encoder = self.motor.getEncoder()
        self.motor.setIdleMode(rev.CANSparkMax.IdleMode.kCoast)
        self.motorController = self.motor.getPIDController()

        p = 0.00007
        i = 0.0000007
        d = 0
        f = 0

        self.motorController.setP(p)
        self.motorController.setI(i)
        self.motorController.setD(d)
        self.motorController.setFF(f)

        self.running = False
        self.reversed = False
        self.deployed = False

        self.stop()
        self.retract()

    # Piston Functions:

    # pushes out the pistons
    def deploy(self):
        self.deployed = True
        self.piston.set(wpilib.DoubleSolenoid.Value.kReverse)

    # pulls in the pistons
    def retract(self):
        self.deployed = False
        self.piston.set(wpilib.DoubleSolenoid.Value.kForward)

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
        self.motor.set(0)

    # starts the motor
    def start(self):
        self.running = True

        speed = -MOTOR_SPEED if self.reversed else MOTOR_SPEEDf

        self.motorController.setReference(speed, rev.ControlType.kVelocity)

    # this is a generator, should be iterated 50 times a second
    def run(self):

        # for keeping track of motor stalling
        motorStallCount = 0

        while True:

            if self.running:
                if self.reversed:
                    speed = -MOTOR_SPEED
                else:
                    speed = MOTOR_SPEED

                    # counts if the motor is stalling while going forwards	
                    if abs(self.encoder.getVelocity()) <  50:	
                        motorStallCount += 1
                    else:	
                        motorStallCount = 0	

                    # rotate the motor backwards if it has stalled for too long
                    if motorStallCount >= 10:
                        motorStallCount = 0
                        for _ in range(200):
                            self.motor.set(0)
                            yield
                
                # actually run the motor
                self.motorController.setReference(speed, rev.ControlType.kVelocity)
            else:
                # if it isn't running, set to zero voltage so it won't move
                self.motor.set(0)

            yield

    # toggles between spinning and not spinning each time it is called
    def toggleMotor(self):
        self.running = not self.running

    # toggles between forwards and backwards
    def toggleDirection(self):
        self.reversed = not self.reversed