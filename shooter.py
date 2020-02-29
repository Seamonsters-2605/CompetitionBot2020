import rev

class Shooter:

    def __init__(self, motorNum1, motorNum2):
        
        motor1 = rev.CANSparkMax(motorNum1, rev.CANSparkMax.MotorType.kBrushless)
        motor2 = rev.CANSparkMax(motorNum2, rev.CANSparkMax.MotorType.kBrushless)

        self.motorController1 = motor1.getPIDController()
        self.motorController2 = motor2.getPIDController()

        self.speed = 5_500 # rpm

    # drives the motors, should be called 50 times a second
    def spin(self):
        self.motorController1.setReference(self.speed, rev.ControlType.kVelocity)
        self.motorController2.setReference(-self.speed, rev.ControlType.kVelocity)

    # stops the motors
    def stop(self):
        self.speed = 0

    def start(self):
        self.speed = 5_500

    def toggleMotor(self):
        if self.speed == 0:
            self.start()
        else:
            self.stop()

    # allows the speed the motor spins to be adjusted
    def adjustSpeed(self, change):
        self.speed += change

        if self.speed < 0:
            self.speed = 0
        elif self.speed > 5_676: # max speed of neo motor
            self.speed = 5_676