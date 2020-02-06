import math

# field: 52, 26

class FieldCoordinate:

    def __init__(self, name, x, y, angle):
        self.name = name
        self.x = x
        self.y = y
        self.angle = angle

    def __repr__(self):
        return "%s (%f, %f, %f deg)" \
            % (self.name, self.x, self.y, math.degrees(self.angle))

targetPoints = [
    # Red
    FieldCoordinate("Low Port", -24.5, 5.11, math.pi/2),
    FieldCoordinate("Control Panel", 0, 10.69, 3 * math.pi/2),
    FieldCoordinate("Loading Bay", 24.5, 4.625, 3 * math.pi/2),
    # Blue
    FieldCoordinate("Low Port", 24.5, -5.11, 3 * math.pi/2),
    FieldCoordinate("Control Panel", 0, -10.69, math.pi/2),
    FieldCoordinate("Loading Bay", -24.5, -4.625, math.pi/2)
]