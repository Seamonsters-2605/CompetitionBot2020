import remi.gui as gui
import seamonsters as sea

class App(sea.Dashboard):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, css=True, **kwargs)

    def main(self, robot, appCallback):
        
        root = gui.VBox(gui.Label("Drive controls"), width = 600, margin = "0px auto")

        manualBox = gui.VBox()
        gearButtons = []
        speedButtons = []
        compressorButtons = []
         
        for mode in robot.driveGears.keys():
            button = gui.Button(mode)
            button.set_on_click_listener(robot.c_changeGear)
            gearButtons.append(button)
        
        for speed in robot.driveGears[robot.driveMode].keys():
            button = gui.Button(speed)
            button.set_on_click_listener(robot.c_changeSpeed)
            print("onclick: " + button.EVENT_ONCLICK)
            speedButtons.append(button)

        for mode in ["Start","Stop"]:
            button = gui.Button(mode)
            button.set_on_click_listener(robot.c_compressor)
            compressorButtons.append(button)
        
        gearBox = sea.hBoxWith(gui.Label("Gears:"),gearButtons)
        speedBox = sea.hBoxWith(gui.Label("Speed:"),speedButtons)
        compressorBox = sea.hBoxWith(gui.Label("Compressor:",),compressorButtons)

        manualBox.append(gearBox)
        manualBox.append(speedBox)
        manualBox.append(compressorBox)

        root.append(manualBox)

        appCallback(self)
        return root