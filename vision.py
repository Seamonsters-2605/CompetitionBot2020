import seamonsters as sea
from networktables import NetworkTables
import math

# very rough values
LIMELIGHT_HEIGHT = 16 # inches
TARGET_HEIGHT = 29 # inches

BASE_TARGET_RATIO = .4

# pipelines
DUAL_PIPELINE = 0
LEFT_PIPELINE = 1
RIGHT_PIPELINE = 2

# does the limelight see a vision target?
def targetDetected(limelight):
        hasTargets = limelight.getNumber('tv', None)

        if hasTargets == None:
            print("No limelight connection")
            return False

        elif hasTargets == 0:
            return False

        return True

# returns the horizontal offset of a vision target in degrees
# None if there are no vision targets
def getXOffset(limelight):
    return limelight.getNumber('tx', None)

# returns the vertical offset of a vision target in degrees
# None if there are no vision targets
def getYOffset(limelight):
    return limelight.getNumber('ty', None)

# returns the distance a vision target is away from the limelight
def getDistance(limelight):
    yAngle = getYOffset(limelight)

    leg = TARGET_HEIGHT - LIMELIGHT_HEIGHT

    return leg / math.tan(math.radians(yAngle)) * (1 - .234)

# returns the anglular offset of the normal of the vision target
def getAngleOffset(limelight):

    limelight.putNumber('pipeline', DUAL_PIPELINE)

    hor = limelight.getNumber('thor', None) # horizontal value of the box
    vert = limelight.getNumber('tvert', None) # vertical value of the box

    if (hor / vert * BASE_TARGET_RATIO) > 1:
        offset = 0
    else:
        offset = math.acos((hor / vert) * BASE_TARGET_RATIO)

    limelight.putNumber('pipeline', LEFT_PIPELINE)
    leftDist = getDistance(limelight.getNumber('ty', None))

    limelight.putNumber('pipeline', RIGHT_PIPELINE)
    rightDist = getDistance(limelight.getNumber('ty', None))

    if leftDist < rightDist:
        offset *= -1

    return math.degrees(offset)