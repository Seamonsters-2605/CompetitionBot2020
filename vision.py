import seamonsters as sea
from networktables import NetworkTables
import math

LIMELIGHT_HEIGHT = 1.33 # feet
TARGET_HEIGHT = 7.48 # feet
LIMELIGHT_ANGLE = math.radians(0) # angle in radians, needs to changed fixed later

BASE_TARGET_RATIO = .4

# pipeline
DUAL_PIPELINE = 0

# used for default values, the actual number doesn't matter
DEFAULT_VALUE = 12345

# does the limelight see a vision target?
def targetDetected(limelight):
        hasTargets = limelight.getNumber('tv', DEFAULT_VALUE)

        if hasTargets == DEFAULT_VALUE:
            print("No limelight connection")
            return False

        elif hasTargets == 0:
            return False

        return True

# returns the horizontal offset of a vision target in degrees
# None if there are no vision targets
def getXOffset(limelight):
    return limelight.getNumber('tx', DEFAULT_VALUE)

# returns the vertical offset of a vision target in degreess
# None if there are no vision targets
def getYOffset(limelight):
    return limelight.getNumber('ty', DEFAULT_VALUE)

# returns the distance a vision target is away from the limelight
def getDistance(limelight):
    yAngle = getYOffset(limelight)

    leg = (TARGET_HEIGHT + 8.5/12) - LIMELIGHT_HEIGHT # 8.5 inches to center of hexagon

    return leg / math.tan(math.radians(yAngle)+LIMELIGHT_ANGLE)