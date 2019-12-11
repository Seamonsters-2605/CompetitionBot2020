import seamonsters as sea
import math
from networktables import NetworkTables
import robot

ANGLE_THRESHHOLD = 2 # in degrees; if the target is off by this much or greater, shouldAlign() will return True

# very rough values
LIMELIGHT_HEIGHT = 10 # inches
TARGET_HEIGHT = 30 # inches

BASE_TARGET_RATIO = 1 / 2

# pipelines
DUAL_PIPELINE = 0
LEFT_PIPELINE = 1
RIGHT_PIPELINE = 2

def visionHasTarget(limelight):
        hasTargets = limelight('tv', None)

        if hasTargets == None:
            print("No limelight connection")
            return False

        elif hasTargets == 0:
            print("No vision targets")
            return False

        return True

def getAngleOffset(limelight):

    limelight.putNumber('pipeline', DUAL_PIPELINE)

    hor = limelight.getNumber('thor') # horizontal value of the box
    vert = limelight.getNumber('tvert') # vertical value of the box

    ratio = vert / hor

    offset = math.acos(ratio / BASE_TARGET_RATIO)

    limelight.putNumber('pipeline', LEFT_PIPELINE)
    leftDist = getDistance(limelight.getNumber('ty'))

    limelight.putNumber('pipeline', RIGHT_PIPELINE)
    rightDist = getDistance(limelight.getNumber('ty'))

    if leftDist < rightDist:
        offset *= -1

    return offset

# this is inaccurate when the limelight is a similar height to the target
def getDistance(yAngle):

    leg = TARGET_HEIGHT - LIMELIGHT_HEIGHT

    return leg / math.tan(yAngle)  

# uses the limelight to align with a vision target returns True if completes without error
def driveIntoVisionTarget(robot : robot.CompetitionBot2020):

    # Step 1: point at target

    robot.limelight.putNumber('pipeline', DUAL_PIPELINE)

    if not visionHasTarget(robot.limelight):
        return False

    hOffset = robot.limelight.getNumber('th')
    robot.turnDegrees(-1 * hOffset)

    while True:

        # needs to be reformatted, if the robot
        # looses the vision target for just 1/50
        # of a second, the function will end
        if not visionHasTarget(robot.limelight):
            return False
        
        yAngle = robot.limelight.getNumber('ty', None)

        dist = getDistance(yAngle)

        # this is where the drive-a-distance function goes
        print(dist)

        yield

    robot.superDrive.drive(0,0,0)