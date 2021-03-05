import math

# field: 52, 26

class FieldCoordinate:
    """
    A point (vector?) representing a position on the game field.
    (0, 0) is the middle of the field (I think).
    Attributes:
        name - the name of the point.
        x - the x position of the point (in feet).
        y - the y position of the point (in feet).
        angle - an angle (in radians).
    """

    def __init__(self, name, x, y, angle):
        """
        Constructor.
        :param name: the name of this point.
        :param x: the x position of this point (in feet).
        :param y: the y position of this point (in feet).
        :param angle: an angle (in radians).
        """
        self.name = name
        self.x = x
        self.y = y
        self.angle = angle

    def __repr__(self):
        return "%s (%f, %f, %f deg)" \
            % (self.name, self.x, self.y, math.degrees(self.angle))

    def getCoords(self):
        return self.x, self.y

targetPoints = [
    # Red
    FieldCoordinate("Power Port", -24.5, 5.11, math.pi/2),
    FieldCoordinate("Control Panel", 0, 10.69, 3 * math.pi/2),
    FieldCoordinate("Loading Bay", 24.5, 4.625, 3 * math.pi/2),
    # Blue
    FieldCoordinate("Power Port", 24.5, -5.11, 3 * math.pi/2),
    FieldCoordinate("Control Panel", 0, -10.69, math.pi/2),
    FieldCoordinate("Loading Bay", -24.5, -4.625, math.pi/2)
]