import rev

class Shooter:

    def __init__(self, motorNum):
        
        motor = rev.CANSparkMax(motorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.motorController = motor.getPIDController()

        self.speed = 5_500 # rpm

    # starts the motor
    def start(self):
        self.motorController.setReference(self.speed, rev.ControlType.kVelocity)

    # stops the motor
    def stop(self):
        self.motorController.setReference(0, rev.ControlType.kVelocity)

    # allows the speed the motor spins to be adjusted
    def adjustSpeed(self, change):
        self.speed += change

        if self.speed < 0:
            self.speed = 0
        elif self.speed > 5_676: # max speed of neo motor
            self.speed = 5_676