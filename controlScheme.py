import math
import wpilib
import seamonsters as sea

"""
to use, create a subclass of ControlScheme and override all the functions
the competition profile using logitech controllers is the default control scheme
"""

class ControlScheme:

    # set up variables
    def __init__(self, driverController, operatorController):
        self.CONTROLLER_RIGHT = wpilib.interfaces._interfaces.GenericHID.Hand.kRightHand
        self.CONTROLLER_LEFT = wpilib.interfaces._interfaces.GenericHID.Hand.kLeftHand

        self.driverController = driverController
        self.operatorController = operatorController

    # reset buttons every update cycle
    def resetButtons(self):
        self.operatorController.getXButtonPressed()
        self.operatorController.getYButtonPressed()
        self.driverController.getAButtonPressed()

    # get the direction the robot should go
    def getDirection(self) -> float:
        return math.pi/2

    # get the speed the robot should turn
    def getTurn(self) -> float:
        return -sea.deadZone(self.driverController.getX(self.CONTROLLER_RIGHT), deadZone=0.05)
    
    # get the speed the robot should drive
    def getMagnitude(self) -> float:
        return -sea.deadZone(self.driverController.getY(self.CONTROLLER_LEFT), deadZone=0.05)

    # get weather or not the robot should search for a vision target
    def shouldUseVision(self) -> bool:
        return self.driverController.getBumper(self.CONTROLLER_LEFT)

    # get weather or not the robot should spin the intake
    def shouldSpinIntake(self) -> bool:
        return self.driverController.getBumper(self.CONTROLLER_RIGHT)

    # get weather or not the robot should reverse the intake
    def shouldReverseIntake(self) -> bool:
        return self.operatorController.getAButton()

    # get weather or not the robot should retract/extend the intake
    def shouldToggleIntake(self) -> bool:
        return self.driverController.getAButtonPressed()

    # get weather or not the robot should spin the indexer
    def shouldSpinIndexer(self) -> bool:
        return self.operatorController.getBumper(self.CONTROLLER_LEFT)

    # get weather or not the robot should spin the indexer in reverse
    def shouldReverseIndexer(self) -> bool:
        return self.operatorController.getBButton()

    # get weather or not the robot should toggle auto index
    def shouldToggleAutoIndex(self) -> bool:
        return self.operatorController.getYButtonPressed()

    # get weather or not the robot should toggle the shooter
    def shouldToggleShooter(self) -> bool:
        return self.operatorController.getXButtonPressed()

# comp control scheme but with an inverted x axis for anyone with a different controller
class InvertedX(ControlScheme):

    def getTurn(self):
        return -super().getTurn()

# control scheme for a single joystick or just one on a controller
class SingleJoystickScheme(ControlScheme):

    def getTurn(self):
        return sea.deadZone(self.driverController.getX(self.CONTROLLER_LEFT), deadZone=0.05)