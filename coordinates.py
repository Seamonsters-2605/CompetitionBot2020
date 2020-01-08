import math

class FieldCoordinate:

    def __init__(self, name, x, y, angle):
        self.name = name
        self.x = x
        self.y = y
        self.angle = angle

    def __repr__(self):
        return "%s (%f, %f, %f deg)" \
            % (self.name, self.x, self.y, math.degrees(self.angle))

targetPoints = []