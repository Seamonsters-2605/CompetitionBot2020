__author__ = "seamonsters"

import math
import seamonsters as sea


class AccelerationFilter:
    """
    Calculates acceleration filtering for drive inputs (magnitude, direction, turn).
    """

    def __init__(self, linearAccel, angularAccel):
        """
        :param linearAccel: Linear acceleration, in feet per second per second
        :param angularAccel: Angular acceleration, in radians per second per second
        """
        self.linearAccelPerFrame = linearAccel / sea.ITERATIONS_PER_SECOND
        self.angularAccelPerFrame = angularAccel / sea.ITERATIONS_PER_SECOND
        self.previousX = 0.0
        self.previousY = 0.0
        self.previousTurn = 0.0

    def filter(self, magnitude, direction, turn):
        """
        :param magnitude: linear velocity in feet per second
        :param direction: linear direction in radians
        :param turn: angular velocity in radians per second
        :return: tuple of filtered magnitude, direction, turn
        """
        if abs(self.previousTurn - turn) <= self.angularAccelPerFrame:
            filteredTurn = turn
        else:
            if turn > self.previousTurn:
                filteredTurn = self.previousTurn + self.angularAccelPerFrame
            else:
                filteredTurn = self.previousTurn - self.angularAccelPerFrame

        x = magnitude * math.cos(direction)
        y = magnitude * math.sin(direction)
        distanceFromPrev = math.sqrt((x - self.previousX) ** 2
                                   + (y - self.previousY) ** 2)

        if distanceFromPrev <= self.linearAccelPerFrame:
            filteredX = x
            filteredY = y
            filteredMag = magnitude
            filteredDir = direction
        else:
            filteredX = self.previousX \
                + (x - self.previousX) * self.linearAccelPerFrame / distanceFromPrev
            filteredY = self.previousY \
                + (y - self.previousY) * self.linearAccelPerFrame / distanceFromPrev
            filteredMag = math.sqrt(filteredX ** 2 + filteredY ** 2)
            filteredDir = math.atan2(filteredY, filteredX)

        self.previousX = filteredX
        self.previousY = filteredY
        self.previousTurn = filteredTurn
        return filteredMag, filteredDir, filteredTurn


class MultiDrive:
    """
    Wraps a SuperHolonomicDrive, and allows ``drive()`` to be called multiple
    times in a loop. The values for all of these calls are added together,
    and sent to the SuperHolonomicDrive when ``update()`` is called.
    """

    def __init__(self, superDrive):
        super().__init__()
        self.superDrive = superDrive
        self._reset()

    def _reset(self):
        self.totalX = 0
        self.totalY = 0
        self.totalTurn = 0

    def drive(self, magnitude, direction, turn):
        self.totalX += magnitude * math.cos(direction)
        self.totalY += magnitude * math.sin(direction)
        self.totalTurn += turn

    def update(self):
        magnitude = math.sqrt(self.totalX ** 2 + self.totalY ** 2)
        direction = math.atan2(self.totalY, self.totalX)
        scale = self.superDrive.drive(magnitude, direction, self.totalTurn)
        self._reset()
        return scale


if __name__ == "__main__":
    # test acceleration filter drive
    accelFilter = AccelerationFilter(2.0, 2.0)
    for i in range(0, 25):
        print(accelFilter.filter(1.0, math.radians(45), 1.0))
    print("--------")
    for i in range(0, 25):
        print(accelFilter.filter(1.0, math.radians(90), 1.0))