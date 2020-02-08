import random, math, colorSensor, rev
import seamonsters as sea

class ControlPanelSpinner:
    
    def __init__(self, motorNum):
        motor = rev.CANSparkMax(motorNum, rev.CANSparkMax.MotorType.kBrushless)
        self.motorController = motor.getPIDController()
        self.speed = 60

        self.cpColors = ["R","Y","B","G"] # The order of colors as they show up on the control panel, clockwise


    # Starts the motor
    def start(self):
        self.motorController.setReference(self.speed, rev.ControlType.kVelocity)
    
    
    # Stops the motor
    def stop(self):
        self.motorController.setReference(0, rev.ControlType.kVelocity)
        

    # It then returns the value of that color, shifted STEPS colors clockwise. 
    # For example, typing shiftColor("red", 2) will return "blue" because that is two colors clockwise of red on the color wheel.
    def shiftColor(self, color : str, steps : int) -> int:
        colorIndex = self.cpColors.index(color) # the index of the given color on the control panel.
        newColorIndex = (colorIndex + steps) % 4 # the index of the given color, shifted two colors clockwise.
        return self.cpColors[newColorIndex]


    # Turns the wheel clockwise until it is on the next color.
    def nextColor(self): 
        startColor = colorSensor.getColor() # the color the camera starts on
        endColor = self.shiftColor(startColor, 1)
        colorsSeen = [startColor]*5 # The previous 5 colors the camera has seen, from most recent (4) to oldest (0)

        # keeps turning the wheel until it's on the correct color
        self.start()
        while not (colorsSeen == [endColor]*5): 
            colorsSeen.append(colorSensor.getColor()) # Records the current color
            del colorsSeen[0]

        # rotates the control panel a little bit more. Ideally, this puts the middle of the pie slice below the color sensor.
        yield from sea.wait(0.2)
        self.stop()


        print("turned to color " + colorSensor.getColor())


    # turns control panel certain number of rotations
    def rotate(self, rotations):
        for _ in range(0, rotations * 8):
            self.nextColor()
        
        print("finished rotate(), on color " + colorSensor.getColor())


    # Turns the control panel until it's on the requested color
    def goto(self, color): 
        while colorSensor.getColor() != color:
            self.nextColor()

        print("finished goto(), on color " + colorSensor.getColor())

# Color Sensor drive testing

def driveToColor(robot, color : str, speed):

    detectedColor = colorSensor.getColor()
    if detectedColor != color:
        robot.multiDrive.drive(speed, math.pi/2, 0)
        robot.multiDrive.update()
        detectedColor = colorSensor.getColor()
    

