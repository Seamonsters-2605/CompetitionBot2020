import seamonsters as sea
import math
from networktables import NetworkTables

ANGLE_THRESHHOLD = 2 # in degrees; if the target is off by this much or greater, shouldAlign() will return True

