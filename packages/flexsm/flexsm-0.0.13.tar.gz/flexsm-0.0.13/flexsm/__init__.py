from collections import defaultdict
import inspect
import time
import threading

class TransitionWithoutOverloadException(Exception):
    pass

nop = lambda *a, **kw: None

class Transition:
    def __init__(self, next=None, check=None, watch=[]):
        if next is not None:
            self.next = next
        self.watch = watch
        if check is not None:
            self.check = check

    def getNextState(self, *args):
        return self.next

    def watchParameters(self):
        return self.watch

    def check(self, *args):
        return True

    def onTrigger(self, *args, **kwargs):
        pass


class Timeout(Transition):
    def __init__(self, next, seconds):
        Transition.__init__(self, next=next, watch=["time_in_state"])
        self.seconds = seconds

    def check(self, time_in_state):
        return time_in_state > self.seconds


def addTransition(state=None, next=None, watch=None):
    def decorator(fn):
        w = watch
        if w is None:
            if fn.check != Transition.check:
                w = inspect.getargspec(fn.check).args[1:]
            elif fn.getNextState != Transition.getNextState:
                w = inspect.getargspec(fn.getNextState).args[1:]
            elif fn.onTrigger != Transition.onTrigger:
                w = inspect.getargspec(fn.onTrigger).args[1:]
            elif fn.watchParameters == Transition.watchParameters:
                raise TransitionWithoutOverloadException("""Transition has not overloaded any of the following methods:
                                                         check, getNextState, onTrigger, watchParameters""")
        if fn.watchParameters == Transition.watchParameters:
            t = fn(next=next, watch=w)
        else:
            t = fn(next=next)
        if state is not None:
            state.addTransition(t)
        return fn
    return decorator

class State:
    def __init__(self, name="", parent=None, onEnter=nop, onExit=nop):
        self.name = name
        self.parent = parent
        self.transitions = []
        self.watch = defaultdict(list)
        self._onEnter = onEnter
        self._onExit = onExit

    def addTransition(self, t):
        self.transitions.append(t)
        wparams = t.watchParameters()

        if len(wparams)>0:
            for w in wparams:
                self.watch[w].append(t)
        else:
            self.watch["__any__"].append(t)

    def onEnter(self):
        self._onEnter()

    def onExit(self):
        self._onExit()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

class StateMachine:
    def __init__(self, root, time_resolution=0.1):
        self.current_state = list()
        self.current_state_set = set()
        self.values = dict()
        self.known_params = set()
        self.just_transitioned = True
        self.watch_params = defaultdict(list)
        self.transitions = []
        self.changeState(root)
        self._stop_event = threading.Event()

        def selfheartbeat(sm):
            while not self._stop_event.is_set():
                sm.heartbeat()
                time.sleep(time_resolution)

        self.heartbeat_thread = threading.Thread(target=selfheartbeat, args=(self,))
        self.heartbeat_thread.setDaemon(True)
        self.heartbeat_thread.start()

    def __del__(self):
        self._stop_event.set()

    def changeState(self, s):
        newState = list()
        newStateSet = set()
        while s is not None:
            if s not in newStateSet:
                newState.append(s)
                newStateSet.add(s)
            s = s.parent

        if self.current_state != set():
            if self.current_state != newState:
                for s in (self.current_state_set - newStateSet):
                    s.onExit()
                for s in (newStateSet - self.current_state_set):
                    s.onEnter()

        self.current_state = newState
        self.current_state_set = newStateSet

        self.state_time_entered = time.time()
        self.heartbeat(quiet=True)
        self.onChangeState(newState)

        self.watch_params = defaultdict(list)
        self.transitions = []
        for s in self.current_state:
            for (param, transitions) in s.watch.items():
                self.watch_params[param].extend(transitions)
                self.transitions.extend(transitions)

    def heartbeat(self, quiet=False):
        if quiet:
            self.values["time_in_state"] = time.time() - self.state_time_entered
        else:
            self.update("time_in_state", time.time() - self.state_time_entered)

    def update(self, param, value):
        if param in self.values and value == self.values[param]:
            return
        self.values[param] = value
        self.known_params.add(param)

        if self.just_transitioned:
            transitions = self.transitions
        else:
            transitions = self.watch_params[param] + self.watch_params["__any__"]

        for t in transitions:
            params = t.watchParameters()
            if self.known_params.issuperset(params):
                needed_params = [self.values[p] for p in params]
                if t.check(*needed_params):
                    nextState = t.getNextState(*needed_params)
                    if nextState is not None:
                        t.onTrigger(*needed_params)
                        self.changeState(nextState)
                        self.just_transitioned = True
                        return

        self.just_transitioned = False

    def onChangeState(self, s):
        pass
