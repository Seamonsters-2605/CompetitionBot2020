import os
import sys
import queue
import threading
import remi
import remi.gui as gui
import socket
import time
import logging
import seamonsters as sea

DASHBOARD_PORT = 5805

logger = logging.getLogger("seamonsters")

def hBoxWith(*args, **kwargs):
    """
    Construct a REMI HBox with the given keyword arguments, and add all of the
    given widgets to it.
    """
    box = gui.HBox(**kwargs)
    for widget in args:
        box.append(widget)
    return box

def vBoxWith(*args, **kwargs):
    """
    Construct a REMI VBox with the given keyword arguments, and add all of the
    given widgets to it.
    """
    box = gui.VBox(**kwargs)
    for widget in args:
        box.append(widget)
    return box

def startDashboard(robot, dashboardClass):
    """
    Start the dashboard in a separate thread. Behavior of this function will
    depend on the RobotPy command line arguments -- in "run" mode the server
    will be started quietly, in "sim" mode a web browser will also be opened,
    and in "deploy" mode nothing will happen.

    :param robot: a robot object with an ``app`` variable. This will be set
        when the dashboard has started.
    :param dashboardClass: a class which extends from ``sea.Dashboard``
    """
    robot.app = None

    def appCallback(app):
        logger.info("Dashboard initialized")
        robot.app = app

    def startDashboardThread(robot, appCallback):
        if sys.argv[1] == 'sim':
            if sys.platform == 'darwin': # macOS
                # issue with macOS Sierra and later
                address = '127.0.0.1'
            else:
                # doesn't work with 127.0.0.1 or localhost on school laptops
                address = socket.gethostbyname(socket.gethostname())
            remi.start(dashboardClass, start_browser=True,
                address=address, port=DASHBOARD_PORT, userdata=(robot, appCallback,))
        elif sys.argv[1] == 'depoly':
            pass
        elif sys.argv[1] == 'run': # run on robot
            while True:
                try:
                    remi.start(dashboardClass, start_browser=False,
                        address='10.26.5.2', port=DASHBOARD_PORT, userdata=(robot, appCallback,))
                    break
                except:
                    logger.warning("Dashboard couldn't start, trying again in 5 seconds")
                    time.sleep(5.0)

    thread = threading.Thread(target=startDashboardThread,
                                args=(robot, appCallback))
    thread.daemon = True
    thread.start()


def queuedDashboardEvent(eventF):
    """
    Given a function ``eventF`` which takes any number of arguments,
    returns a new function which will add ``eventF`` and given arguments
    to the Dashboard event queue, to be called later.
    """
    def queueTheEvent(self, *args, **kwargs):
        # self is the robot
        def doTheEvent():
            logger.info("Event: " + eventF.__name__)
            return eventF(self, *args, **kwargs)
        self.app.eventQueue.put(doTheEvent)
    return queueTheEvent

class Dashboard(remi.App):
    """
    Adds some utilities for building robot dashboards to ``remi.App``.

    A dashboard class must have a ``main`` function which takes ``robot`` and
    ``appCallback`` as arguments, where ``robot`` is the robot object and
    ``appCallback`` is a function that should be called with ``self`` as an
    argument when ``main`` has completed.

    :param css: Whether to use a custom css file. Must be located at 'res/style.css'
    """
    def __init__(self, *args, css=False, **kwargs):
        self.eventQueue = queue.Queue()
        if css:
            res_path = sea.getRobotPath('res')
            super(Dashboard, self).__init__(*args, static_file_path={'res':res_path}, **kwargs)
        else:
            super(Dashboard,self).__init__(*args, **kwargs)

    def clearEvents(self):
        """
        Clear the event queue without executing any events. It's a good idea to
        call this at the start of teleop, in case someone clicked some buttons
        while the robot was disabled.
        """
        while not self.eventQueue.empty():
            self.eventQueue.get()

    def doEvents(self):
        """
        Execute all events in the event queue and clear the queue. This should
        be called continuously during teleop.
        """
        value = None
        while not self.eventQueue.empty():
            event = self.eventQueue.get()
            v = event()
            if value is None:
                value = v
        return value


class ToggleButtonGroup:

    def __init__(self):
        self.buttons = []

    def addButton(self, button = gui.Button, key=None):
        if key is None:
            key = button.get_text()
        button.key = key
        self.buttons.append(button)

    def highlight(self, key):
        for button in self.buttons:
            if button.key == key:
                button.style["background"] = "rgb(21, 130, 21)"
            else:
                button.style["background"] = "rgb(21, 182, 21)"
