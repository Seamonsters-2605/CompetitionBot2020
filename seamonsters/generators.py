__author__ = "seamonsters"

import itertools, logging

logger = logging.getLogger("seamonsters")

class ParallelSignal:
    """
    A signal that can be returned from a generator in a parallel group to
    trigger an action on the group.
    """

class StopParallelSignal(ParallelSignal):
    """
    Value to signal that a group of parallel commands should be stopped.
    """

    def __init__(self, value=None):
        self.value = value

class AddParallelSignal(ParallelSignal):
    """
    Value to signal that a new generator should be added to the group of
    parallel commands.
    """

    def __init__(self, iterable):
        self.iterable = iterable


def sequence(*iterables):
    """
    Run a set of iterables sequentially
    """
    return itertools.chain(*iterables)

def parallel(*iterables):
    """
    Run a group of iterables in parallel. Ends when none are left running.

    An iterable can yield or return a ParallelSignal to trigger an action.
    """
    iterables = list(iterables)
    try:
        while len(iterables) != 0:
            toRemove = [ ]
            for iter in iterables:
                try:
                    result = next(iter)
                except StopIteration as e:
                    result = e.value
                    toRemove.append(iter)
                except BaseException as e:
                    logger.exception("A parallel action crashed",
                        exc_info=e)
                    result = None
                    toRemove.append(iter)
                if isinstance(result, ParallelSignal):
                    if isinstance(result, StopParallelSignal):
                        return result.value
                    elif isinstance(result, AddParallelSignal):
                        iterables.append(result.iterable)
            for iter in toRemove:
                iterables.remove(iter)
            yield
    finally:
        for iter in iterables:
            iter.close()

def wait(time):
    """
    Wait for a certain number of iterations.
    """
    for _ in range(int(time)):
        yield

def forever():
    """
    Iterate forever.
    """
    while True:
        yield

def timeLimit(iterable, time):
    """
    Run the iterable until it finishes or the given time limit has passed.
    Return the value of the iterable if it ends early, None otherwise.
    """
    return itertools.islice(iterable, time)

def untilTrue(iterable):
    """
    Run the iterable until it yields True, then stop.
    """
    return itertools.takewhile(lambda x: not x, iterable)

def _ensureBool(iterable, requiredCount, b):
    try:
        count = 0
        while True:
            try:
                value = next(iterable)
            except StopIteration as e:
                return e.value
            yield value
            if value == b:
                count += 1
            else:
                count = 0
            if count >= requiredCount:
                return b
    finally:
        iterable.close()

def ensureTrue(iterable, requiredCount):
    """
    Wait until the iterable yields True for a certain number of consecutive
    iterations before finishing.

    :return: the return value of the iterable if it exits early, True otherwise
    """
    return (yield from _ensureBool(iterable, requiredCount, True))

def ensureFalse(iterable, requiredCount):
    """
    Wait until the iterable yields False for a certain number of consecutive
    iterations before finishing.

    :return: the return value of the iterable if it exits early, False
        otherwise (note difference from ``ensureTrue``)
    """
    return (yield from _ensureBool(iterable, requiredCount, False))

def returnValue(iterable, value):
    """
    Run an iterable but change the return value.

    :return: value
    """
    yield from iterable
    return value

def stopAllWhenDone(iterable):
    """
    If run in a ``sea.parallel`` block, when the iterable completes all
    parallel commands will be stopped.
    """
    value = yield from iterable
    return StopParallelSignal(value)

class State:
    """
    An action to run in a StateMachine.
    """

    def __init__(self, function, subMachine=None):
        """
        :param function: A function with no arguments that returns a generator.
            If the generator returns another State, that State will be pushed
            to the stack. Otherwise the State will be popped when it completes.
        :param subMachine: Optional, another StateMachine to run in parallel
            with this State. Allows States to have nested sub-States.
        """
        self.function = function
        self.subMachine = subMachine

    def runState(self):
        if self.subMachine is None:
            yield from self.function()
        else:
            yield from parallel(
                stopAllWhenDone(self.function()),
                self.subMachine.updateGenerator())

IDLE_STATE = State(forever)

class StateMachine:
    """
    Implementation of a Pushdown Automaton. Has one state always running at a
    time, and keeps track of a stack of states.
    """

    def __init__(self):
        self.stateStack = []
        self._cancelState = False

    def currentState(self):
        """
        Get the current running state. If the state stack is empty, IDLE_STATE
        is the current state.
        """
        if len(self.stateStack) == 0:
            return IDLE_STATE
        return self.stateStack[-1]

    def updateGenerator(self):
        """
        Generator to update the state machine.
        """
        while True:
            self._cancelState = False
            yield from parallel(
                self._watchForCancelGenerator(), self._runCurrentState())

    def _runCurrentState(self):
        ret = yield from self.currentState().runState()
        if isinstance(ret, State):
            self.stateStack.append(ret)
        else:
            self.stateStack.pop()
        return StopParallelSignal()

    def clear(self):
        """
        Cancel the current state and clear the stack.
        """
        self.stateStack.clear()
        self._cancelState = True

    def push(self, state):
        """
        Cancel the current running State and push a new State to the stack.
        """
        self.stateStack.append(state)
        self._cancelState = True

    def pop(self):
        """
        Cancel the current running State and pop it. Run the State below it on
        the stack.
        """
        if len(self.stateStack) != 0:
            self.stateStack.pop()
        self._cancelState = True

    def replace(self, state):
        """
        Cancel the current running state and replace it with a new one.
        """
        self.pop()
        self.push(state)

    def runUntilStopped(self, state):
        """
        Push a state and wait until the state is either cancelled by pushing
        or popping, or it exits normally.
        """
        self.push(state)
        while self.currentState() == state:
            yield

    def runUntilPopped(self, state):
        """
        Push a state and wait until the state is popped from the stack.
        """
        self.push(state)
        stackLen = len(self.stateStack)
        while len(self.stateStack) >= stackLen:
            yield


    def _watchForCancelGenerator(self):
        while not self._cancelState:
            yield
        return StopParallelSignal()
