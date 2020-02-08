import wpilib
from rev.color import ColorSensorV3

yellow = wpilib.Color(0.326, 0.553, 0.123)
red    = wpilib.Color(0.530, 0.342, 0.128)
green  = wpilib.Color(0.175, 0.571, 0.251)
blue   = wpilib.Color(0.129, 0.444, 0.427)

def getDiff(color1, color2):
    dif = 0
    dif += abs(color1.red - color2.red)
    dif += abs(color1.blue - color2.blue)
    dif += abs(color1.green - color2.green)
    return dif

colorSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

def getColor():
    detectedColor = colorSensor.getColor()
    dif = {
        "Y" : getDiff(detectedColor, yellow),
        "R" : getDiff(detectedColor, red),
        "G" : getDiff(detectedColor, green),
        "B" : getDiff(detectedColor, blue)
    }
    minDif = min([dif[key] for key in dif])
    for key, value in dif.items():
        if value == minDif:
            return key
            
    print("Color Sensor: Something went wrong!")
    return None