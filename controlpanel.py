import robot
import random

# randomly returns yellow, green, blue, or red
def getColor():
    return ["red", "yellow", "green", "blue"][random.randint(0,3)]

cpColors = ["red","yellow","blue","green"] # The order of colors as they show up on the control panel, clockwise

# Converts the color that the ROBOT SENSOR sees to the color that the GAME SENSOR sees. 
# Any color that the ROBOT SENSOR sees is two colors clockwise from the one that the GAME SENSOR sees.
def cpConvertColor(color):
    colorIndex = cpColors.index(color) # the index of the given color on the control panel.
    newColorIndex = (colorIndex + 2) % 4 # the index of the given color, shifted two colors clockwise.
    
    return cpColors[newColorIndex]
    

# Turns the wheel clockwise until it is on the next color.
def cpNextColor(): 
    startColor = getColor() # the color the camera starts on
    colorsSeen = [startColor]*5 # The previous 5 colors the camera has seen, from most recent (4) to oldest (0)

    # keeps turning the wheel until it's on a different color
    while startColor in colorsSeen: 
        #rotate(x degrees) THIS IS A PLACEHOLDER
        colorsSeen.append(getColor()) # Records the current color
        del colorsSeen[0]

    # rotates the control panel a little bit more. Ideally, this puts the middle of the pie slice below the color sensor.
    for _ in range(5): 
        #rotate(x degrees) also a placeholder

# turns control panel certain number of rotations
def cpTurn(rotations):
    for _ in range(0, rotations * 8):
        cpNextColor()

# Turns the control panel until it's on the requested color
def cpGoto(color): 
    while getColor() != color:
        cpNextColor()