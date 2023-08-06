"""Provides Finite State Machine implementation."""

from inspect import isclass
from functools import wraps
from time import time

from pexpect import EOF
from condoor.exceptions import ConnectionError
from condoor.utils import pattern_to_str


def action(func):
    """Wrap the FSM action function providing extended logging information based on doc string."""
    @wraps(func)
    def call_action(*args, **kwargs):
        """Wrap the function with logger debug."""
        try:
            ctx = kwargs['ctx']
        except KeyError:
            ctx = None

        if ctx is None:
            try:
                ctx = args[-1]
            except IndexError:
                ctx = None
        if ctx:
            if func.__doc__ is None:
                ctx.device.chain.connection.log("A={}".format(func.__name__))
            else:
                ctx.device.chain.connection.log("A={}".format(func.__doc__.split('\n', 1)[0]))
        return func(*args, **kwargs)
    return call_action


class FSM(object):
    """This class represents Finite State Machine for the current device connection.

    Here is the example of usage::

        to be done


    The example action::

        def send_newline(ctx):
            ctx.ctrl.sendline()
            return True

        def error(ctx):
            ctx.message = "Filesystem error"
            return False

        def readonly(ctx):
            ctx.message = "Filesystem is readonly"
            return False

    The ctx object description refer to :class:`condoor.controllers.fsm.FSM`.

    If the action returns True then the FSM continues processing. If the action returns False then FSM stops
    and the error message passed back to the ctx object is posted to the log.


    The FSM state is the integer number. The FSM starts with initial ``state=0`` and finishes if the ``next_state``
    is set to -1.

    If action returns False then FSM returns False. FSM returns True if reaches the -1 state.

    """

    class Context(object):
        """FSM Context class."""

        _slots__ = ('fsm_name', 'ctrl', 'event', 'state', 'finished', 'msg', 'pattern', 'device')

        def __init__(self, fsm_name, device):
            """Initialize the FSM context object.

            Args:
                fsm_name (str): Name of the FSM. This is used for logging.
                device (object): The device object.
            """
            self.device = device
            self.ctrl = device.ctrl
            self.fsm_name = fsm_name
            self.event = None
            self.state = 0
            self.finished = False
            self.msg = ""
            self.pattern = None

        def __str__(self):
            """Return the string representing the FSM context."""
            return "FSM Context:E={},S={},FI={},M='{}'".format(
                self.event, self.state, self.finished, self.msg)

    def __init__(self, name, device, events, transitions, init_pattern=None, timeout=300, searchwindowsize=None,
                 max_transitions=20):
        """Initialize FSM object.

        Args:
            name (str): Name of the state machine used for logging purposes. Can't be *None*
            ctrl (object): Controller class representing the connection to the device
            events (list): List of expected strings or pexpect.TIMEOUT exception expected from the device.
            transitions (list): List of tuples in defining the state machine transitions.
            init_pattern (str): The pattern that was expected in the previous operation.
            timeout (int): Timeout between states in seconds. Defaults to 300 seconds.
            searchwindowsize (int): The size of search window. Defaults to -1.
            max_transitions (int): Max number of transitions allowed before quiting the FSM.

        The transition tuple format is as follows::

            (event, [list_of_states], next_state, action, timeout)

        - event (str): string from the `events` list which is expected to be received from device.
        - list_of_states (list): List of FSM states that triggers the action in case of event occurrence.
        - next_state (int): Next state for FSM transition.
        - action (func): function to be executed if the current FSM state belongs to `list_of_states` and the `event`
          occurred. The action can be also *None* then FSM transits to the next state without any action. Action
          can be also the exception, which is raised and FSM stops.
        """
        self.events = events
        self.device = device
        self.ctrl = device.ctrl
        self.timeout = timeout
        self.searchwindowsize = searchwindowsize
        self.name = name
        self.init_pattern = init_pattern
        self.max_transitions = max_transitions
        self.log = device.chain.connection.log

        self.transition_table = self._compile(transitions, events)

    def _compile(self, transitions, events):
        compiled = {}
        for transition in transitions:
            event, states, new_state, act, timeout = transition
            if not isinstance(states, list):
                states = list(states)
            try:
                event_index = events.index(event)
            except ValueError:
                self.log("Transition for non-existing event: {}".format(
                    event if isinstance(event, str) else event.pattern))
            else:
                for state in states:
                    key = (event_index, state)
                    compiled[key] = (new_state, act, timeout)

        return compiled

    def run(self):
        """Start the FSM.

        Returns:
            boolean: True if FSM reaches the last state or false if the exception or error message was raised

        """
        ctx = FSM.Context(self.name, self.device)
        transition_counter = 0
        timeout = self.timeout
        self.log("{} Start".format(self.name))
        while transition_counter < self.max_transitions:
            transition_counter += 1
            try:
                start_time = time()
                if self.init_pattern is None:
                    ctx.event = self.ctrl.expect(self.events, searchwindowsize=self.searchwindowsize, timeout=timeout)
                else:
                    self.log("INIT_PATTERN={}".format(pattern_to_str(self.init_pattern)))
                    try:
                        ctx.event = self.events.index(self.init_pattern)
                    except ValueError:
                        self.log("INIT_PATTERN unknown.")
                        continue
                    finally:
                        self.init_pattern = None

                finish_time = time() - start_time
                key = (ctx.event, ctx.state)
                ctx.pattern = self.events[ctx.event]

                if key in self.transition_table:
                    transition = self.transition_table[key]
                    next_state, action_instance, next_timeout = transition
                    self.log("E={},S={},T={},RT={:.2f}".format(ctx.event, ctx.state, timeout, finish_time))
                    if callable(action_instance) and not isclass(action_instance):
                        if not action_instance(ctx):
                            self.log("Error: {}".format(ctx.msg))
                            return False
                    elif isinstance(action_instance, Exception):
                        self.log("A=Exception {}".format(action_instance))
                        raise action_instance
                    elif action_instance is None:
                        self.log("A=None")
                    else:
                        self.log("FSM Action is not callable: {}".format(str(action_instance)))
                        raise RuntimeWarning("FSM Action is not callable")

                    if next_timeout != 0:  # no change if set to 0
                        timeout = next_timeout
                    ctx.state = next_state
                    self.log("NS={},NT={}".format(next_state, timeout))

                else:
                    self.log("Unknown transition: EVENT={},STATE={}".format(ctx.event, ctx.state))
                    continue

            except EOF:
                raise ConnectionError("Session closed unexpectedly", self.ctrl.hostname)

            if ctx.finished or next_state == -1:
                self.log("{} Stop at E={},S={}".format(self.name, ctx.event, ctx.state))
                return True

        # check while else if even exists
        self.log("FSM looped. Exiting")
        return False
