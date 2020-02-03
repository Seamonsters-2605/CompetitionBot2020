import math, sys, os, time

ITERATIONS_PER_SECOND = 50.0

def getRobotPath(*paths):
    if sys.argv[1] == 'run': # running on robot
        root = "/home/lvuser/py"
    else:
        root = os.getcwd()
    return os.path.join(root, *paths)

def circleDistance(a, b, circle=math.pi*2):
    """
    Returns the shortest arc length between two points on a circle. Positive if
    direction is positive from a to b.

    :param circle: Total arc length of the circle. Optional, defaults to 2 pi.
    """
    diff = b - a
    while diff > circle / 2:
        diff -= circle
    while diff < -circle / 2:
        diff += circle
    return diff

def feedbackLoopScale(value, scale, exponent=1, maxValue=None):
    negative = (value < 0) ^ (scale < 0) # true if only one is negative
    value = abs(value) ** exponent * abs(scale)
    if maxValue is not None:
        value = min(value, maxValue)
    return -value if negative else value

def setSimulatedDrivetrain(drivetrain):
    if sys.argv[1] == 'sim':
        import physics
        physics.simulatedDrivetrain = drivetrain

def readDataFile(filename):
    lines = [ ]
    filename = getRobotPath(filename)
    with open(filename, 'r') as f:
        for line in f.readlines():
            values = line.split()
            if len(values) == 0:
                continue
            lines.append(tuple(values))
    return lines

class TimingMonitor:
    """
    Monitors the rate of the update loop, to see how closely it matches 50Hz.
    Check ``fps`` for the measured number of iterations per second.
    """

    def __init__(self):
        self.reset()
    
    def reset(self):
        self._count = 0
        self._lastTime = time.time()
        self.fps = 0
    
    def step(self):
        self._count += 1
        t = time.time()
        if t - self._lastTime >= 1:
            self.fps = self._count
            self._count = 0
            self._lastTime = t

    def updateGenerator(self):
        self.reset()
        while True:
            self.step()
            yield
