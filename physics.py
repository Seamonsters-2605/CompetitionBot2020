__author__ = "seamonsters"
import math
import wpilib
from wpilib.kinematics import ChassisSpeeds
from wpilib.geometry import Transform2d
import inspect, os, sys
import configparser
from pyfrc.physics import drivetrains
from pyfrc.physics.core import PhysicsInterface
from pyfrc.physics.visionsim import VisionSim
from hal.simulation import PWMSim
from hal.simulation import EncoderSim
import rev
import navx
from networktables import NetworkTables

STARTING_POSITION = [-16, 10]

simulatedDrivetrain = None

simulatedSparks = []

class SimulatedEncoder:

    def __init__(self, deviceID):
        self.deviceID = deviceID
        self.position = 0
        self.velocity = 0
    
    def getPosition(self):
        return self.position
    
    def getVelocity(self):
        return self.velocity
    
    def setPosition(self, value):
        self.position = value

class SimulatedPIDController:

    def __init__(self, deviceID):
        self.deviceID = deviceID
        self.value = 0
    
    def setP(self, p):
        pass
    def setI(self, i):
        pass
    def setD(self, d):
        pass
    def setFF(self, ff):
        pass

    def setReference(self, value, ctrl):
        if ctrl == rev.ControlType.kVelocity:
            self.value = value
        else:
            print("[SIMULATION] Only velocity mode is supported in the simulation")
            self.value = 0

class SimulatedSpark:

    def __init__(self, deviceID, type):
        self.deviceID = deviceID
        self.lastPosition = 0
        self.enabled = False
        self.encoder = SimulatedEncoder(deviceID)
        self.PIDController = SimulatedPIDController(deviceID)
        self.maxVelocity = 1

    def setIdleMode(self, arg0):
        pass

    def restoreFactoryDefaults(self):
        self.PIDController.value = 0
        self.encoder.position = 0
        self.encoder.velocity = 0

    def disable(self):
        self.enabled = False

    def enable(self):
        self.enabled = True
    
    def get(self):
        return self.encoder.getVelocity()
    
    def getEncoder(self):
        return self.encoder
    
    def getMotorTemperature(self):
        return 0
    
    def getOutputCurrent(self):
        return 0

    def getPIDController(self):
        return self.PIDController

    def set(self, speed):
        self.PIDController.value = self.maxVelocity * speed

    def update(self, tm_diff):
        self.encoder.velocity = self.PIDController.value
        self.encoder.position += self.encoder.velocity * tm_diff / 60

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

    def __init__(self, physics_Controller : PhysicsInterface):
        self.physicsController = physics_Controller

        # NavX simulation
        self.ahrs = None
        def createAHRSSim():
            self.ahrs = AHRSSim()
            return self.ahrs
        navx.AHRS.create_spi = createAHRSSim

        # self.physicsController.add_analog_gyro_channel(0)

        config = configparser.ConfigParser()
        filename = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe()))) \
            + os.sep + "sim" + os.sep + "drivetrain.ini"
        print("Reading robot data from", filename)
        config.read(filename)

        self.simulatedSparkVelocities = [ ]
        if 'sparks' in config:
            for key, value in config['sparks'].items():
                num = int(key.replace('spark', ''))
                maxVel = float(value)
                self.simulatedSparkVelocities.append(maxVel)
        
        for i in range(len(self.simulatedSparkVelocities)):
            simulatedSparks[i].maxVelocity = self.simulatedSparkVelocities[i]
            
        x, y = self._fieldToSimulatorCoords(STARTING_POSITION[0], STARTING_POSITION[1])
        transform = Transform2d.fromFeet(x, y, 0)
        self.physicsController.move_robot(transform)

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

        self._drivePositionState = None

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

    # special function called by pyfrc to update the robot state
    def update_sim(self, now : float, tm_diff: float):
        global simulatedDrivetrain
        for simSpark in simulatedSparks:
            simSpark.update(tm_diff)

        if simulatedDrivetrain is not None:
            #robotMag, robotDir, robotTurn = simulatedDrivetrain.getRobotMovement()
            robotMag, robotDir, robotTurn, self._drivePositionState = \
                simulatedDrivetrain.getRobotPositionOffset(self._drivePositionState, target=False)

            robotMag /= tm_diff 
            robotTurn /= tm_diff

            xVel = robotMag * math.cos(robotDir - math.pi/2) * 0.3048 # 1 ft = 0.3048 m
            yVel = robotMag * math.sin(robotDir - math.pi/2) * 0.3048

            speeds = ChassisSpeeds(xVel, yVel, robotTurn)
            #self.physicsController.vector_drive(xVel, yVel, -robotTurn, elapsed)
            # HACKS: set the time diff to 1 to move by absolute position
            # increments instead of velocities
            self.physicsController.drive(speeds, tm_diff)
        
        if self.ahrs != None:
            self.ahrs.angle = math.degrees(self.physicsController.angle)

        # Vision simulation not yet working

        # x, y, angle = self.physicsController.get_position()
        # visionData = self.visionSim.compute(time, x, y, angle)
        # if visionData is not None:
        #     targetData = visionData[0]
        #     self.visionTable.putNumber('tv', targetData[0])
        #     if targetData[0] != 0:
        #         self.visionTable.putNumber('tx', targetData[2])
        # else:
        #     # DOESN'T mean no vision. vision just doesn't always update
        #     pass

    def _fieldToSimulatorCoords(self, x, y):
        return x + 26, y + 13