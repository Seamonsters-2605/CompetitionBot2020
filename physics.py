__author__ = "seamonsters"
import math
import wpilib
import inspect, os
import configparser
from pyfrc.physics import drivetrains
from pyfrc.physics.visionsim import VisionSim
import rev
import navx
from networktables import NetworkTables

# HAL keys

HALK_SPARK_PERCENT = 'value'
HALK_SPARK_POSITION = 'position'
HALK_SPARK_VELOCITY = 'velocity'
HALK_SPARK_PID_TARGET = 'value' # this is the wrong value, must find correct one

simulatedDrivetrain = None


class SimulatedSpark:

    def __init__(self, port, maxVel):
        self.port = "sparkmax-" + str(port)
        self.maxVel = maxVel
        self.lastPosition = 0

    def update(self, data):
        """
        Update the spark. ``data`` is the HAL dictionary, which has many nested
        dictionaries of data about the simulated robot. Some documentation can
        be found in the ``_reset_hal_data`` in this file:
        https://github.com/robotpy/robotpy-wpilib/blob/master/hal-sim/hal_impl/data.py
        """
        if not data['control']['enabled']:
            return
        if not self.port in data['CAN']:
            return
        sparkData = data['CAN'][self.port]
        controlMode = sparkData['ctrlType']
        if controlMode == rev.ControlType.kVoltage:
            value = sparkData[HALK_SPARK_PERCENT]
            if value < -1:
                value = -1.0
            elif value > 1:
                value = 1.0
            velocity = int(value * self.maxVel / 60)
            # update encoder
            # velocity is measured in encoder counts per 1/10 second
            # position is updated 50 times a second
            # so position should be incremented by 1/5 of the velocity value
            sparkData[HALK_SPARK_POSITION] += velocity // 50
            sparkData[HALK_SPARK_VELOCITY] = velocity
        elif controlMode == rev.ControlType.kPosition:
            targetPos = sparkData[HALK_SPARK_PID_TARGET]
            diff = targetPos - self.lastPosition
            self.lastPosition = targetPos
            # update encoder
            sparkData[HALK_SPARK_POSITION] = targetPos
            sparkData[HALK_SPARK_VELOCITY] = int(diff * 50)
        elif controlMode == rev.ControlType.kVelocity:
            targetVel = sparkData[HALK_SPARK_PID_TARGET]
            # update encoder
            sparkData[HALK_SPARK_POSITION] += int(targetVel / 50) / 60
            sparkData[HALK_SPARK_VELOCITY] = int(targetVel) / 60

class AHRSSim:

    def __init__(self):
        self.angle = 0

    def getAngle(self):
        return self.angle
    
    def getDisplacementX(self):
        return 0.0
    
    def getDisplacementY(self):
        return 0.0

class PhysicsEngine:

    def __init__(self, physicsController):
        self.physicsController = physicsController

        # NavX simulation
        self.ahrs = None
        def createAHRSSim():
            self.ahrs = AHRSSim()
            return self.ahrs
        navx.AHRS.create_spi = createAHRSSim

        self.physicsController.add_analog_gyro_channel(0)

        config = configparser.ConfigParser()
        filename = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe()))) \
            + os.sep + "sim" + os.sep + "drivetrain.ini"
        print("Reading robot data from", filename)
        config.read(filename)

        self.simulatedSparks = [ ]
        if 'sparks' in config:
            for key, value in config['sparks'].items():
                num = int(key.replace('spark', ''))
                maxVel = float(value)
                self.simulatedSparks.append(SimulatedSpark(num, maxVel))

        if 'ds' in config:
            ds = config['ds']
        else:
            ds = { }
        location = int(ds.get('location', '1'))
        team = 1 if (ds.get('team', 'red').lower() == 'blue') else 0
        self.allianceStation = location - 1 + team * 3

        if 'field' in config:
            field = config['field']
        else:
            field = { }
        self.visionX = float(field.get('visionx', '0'))
        self.visionY = float(field.get('visiony', '0'))
        self.visionAngleStart = float(field.get('visionanglestart', '90'))
        self.visionAngleEnd = float(field.get('visionangleend', '270'))

    # special function called by pyfrc when simulator starts
    def initialize(self, hal_data):
        self.visionTable = NetworkTables.getTable('limelight')
        self.visionTable.putNumber('tv', 1) # some arbitrary default vision data
        self.visionTable.putNumber('tx', 0)
        self.visionTable.putNumber('ty', 0)
        self.visionTable.putNumber('ts', 0)
        self.visionTable.putNumber('ta', 5)

        visionTarget = VisionSim.Target(self.visionX, self.visionY,
                                        self.visionAngleStart,
                                        self.visionAngleEnd)
        self.visionSim = VisionSim([visionTarget], 60, 2, 50)
        hal_data['alliance_station'] = self.allianceStation

        self._drivePositionState = None

    # special function called by pyfrc to update the robot state
    def update_sim(self, hal_data, time, elapsed):
        global simulatedDrivetrain
        for simSpark in self.simulatedSparks:
            simSpark.update(hal_data)

        if simulatedDrivetrain is not None:
            #robotMag, robotDir, robotTurn = simulatedDrivetrain.getRobotMovement()
            robotMag, robotDir, robotTurn, self._drivePositionState = \
                simulatedDrivetrain.getRobotPositionOffset(self._drivePositionState)
            xVel = robotMag * math.cos(robotDir)
            yVel = robotMag * math.sin(robotDir)
            #self.physicsController.vector_drive(xVel, yVel, -robotTurn, elapsed)
            # HACKS: set the time diff to 1 to move by absolute position
            # increments instead of velocities
            self.physicsController.vector_drive(xVel, yVel, -robotTurn, 1)
        
        if self.ahrs != None:
            self.ahrs.angle = math.degrees(self.physicsController.angle)

        x, y, angle = self.physicsController.get_position()
        visionData = self.visionSim.compute(time, x, y, angle)
        if visionData is not None:
            targetData = visionData[0]
            self.visionTable.putNumber('tv', targetData[0])
            if targetData[0] != 0:
                self.visionTable.putNumber('tx', targetData[2])
        else:
            # DOESN'T mean no vision. vision just doesn't always update
            pass
