"""Provides Telnet driver class."""

from functools import partial
import re
import pexpect

from condoor.fsm import FSM
from condoor.utils import pattern_to_str
from condoor.protocols.base import Protocol
from condoor.actions import a_send, a_send_password, a_authentication_error, a_unable_to_connect,\
    a_save_last_pattern, a_standby_console, a_send_username, a_send_newline

from condoor.exceptions import ConnectionError, ConnectionTimeoutError, CommandSyntaxError
from condoor.config import CONF


# Telnet connection initiated
ESCAPE_CHAR = "Escape character is|Open"
# Connection refused i.e. line busy on TS
CONNECTION_REFUSED = re.compile("Connection refused")
PASSWORD_OK = "[Pp]assword [Oo][Kk]"

_C = CONF['protocol']['telnet']


class Telnet(Protocol):
    """Telnet protocol implementation."""

    def __init__(self, device):
        """Initialize the Telnet object."""
        super(Telnet, self).__init__(device)

    def get_command(self):
        """Return the Telnet protocol specific command to connect."""
        return "telnet {} {}".format(self.hostname, self.port)

    def connect(self, driver):
        """Connect using the Telnet protocol specific FSM."""
        #              0            1                              2                      3
        events = [ESCAPE_CHAR, driver.press_return_re, driver.standby_re, driver.username_re,
                  #            4                   5                  6                     7
                  driver.password_re, driver.more_re, self.device.prompt_re, driver.rommon_re,
                  #       8                              9              10            11              12
                  driver.unable_to_connect_re, driver.timeout_re, pexpect.TIMEOUT, PASSWORD_OK, driver.syntax_error_re]

        transitions = [
            (ESCAPE_CHAR, [0], 1, None, _C['esc_char_timeout']),
            (driver.syntax_error_re, [0], -1, CommandSyntaxError("Command syntax error"), 0),
            (driver.press_return_re, [0, 1], 1, a_send_newline, 10),
            (PASSWORD_OK, [0, 1], 1, a_send_newline, 10),
            (driver.standby_re, [0, 5], -1, partial(a_standby_console), 0),
            (driver.username_re, [0, 1, 5, 6], -1, partial(a_save_last_pattern, self), 0),
            (driver.password_re, [0, 1, 5], -1, partial(a_save_last_pattern, self), 0),
            (driver.more_re, [0, 5], 7, partial(a_send, "q"), 10),
            # router sends it again to delete
            (driver.more_re, [7], 8, None, 10),
            # (prompt, [0, 1, 5], 6, a_send_newline, 10),
            (self.device.prompt_re, [0, 1, 5], 0, None, 10),
            (self.device.prompt_re, [6, 8, 5], -1, partial(a_save_last_pattern, self), 0),
            (driver.rommon_re, [0, 1, 5], -1, partial(a_save_last_pattern, self), 0),
            (driver.unable_to_connect_re, [0, 1, 5], -1, a_unable_to_connect, 0),
            (driver.timeout_re, [0, 1, 5], -1, ConnectionTimeoutError("Connection Timeout", self.hostname), 0),
            (pexpect.TIMEOUT, [0, 1], 5, a_send_newline, 10),
            (pexpect.TIMEOUT, [5], -1, ConnectionTimeoutError("Connection timeout", self.hostname), 0)
        ]

        self.log("EXPECTED_PROMPT={}".format(pattern_to_str(self.device.prompt_re)))
        # setting max_transitions to large number to swallow prompt like strings from prompt
        fsm = FSM("TELNET-CONNECT", self.device, events, transitions, timeout=_C['connect_timeout'],
                  init_pattern=self.last_pattern, max_transitions=500)
        return fsm.run()

    def authenticate(self, driver):
        """Authenticate using the SSH protocol specific FSM."""
        #                      0                      1                    2                    3
        events = [driver.username_re, driver.password_re, self.device.prompt_re, driver.rommon_re,
                  #       4                              5                              6           7
                  driver.unable_to_connect_re, driver.authentication_error_re, pexpect.TIMEOUT, pexpect.EOF]

        transitions = [
            (driver.username_re, [0], 1, partial(a_send_username, self.username), 10),
            (driver.username_re, [1], 1, None, 10),
            (driver.password_re, [0, 1], 2, partial(a_send_password, self._acquire_password()),
             _C['first_prompt_timeout']),
            (driver.username_re, [2], -1, a_authentication_error, 0),
            (driver.password_re, [2], -1, a_authentication_error, 0),
            (driver.authentication_error_re, [1, 2], -1, a_authentication_error, 0),
            (self.device.prompt_re, [0, 1, 2], -1, None, 0),
            (driver.rommon_re, [0], -1, a_send_newline, 0),
            (pexpect.TIMEOUT, [0], 1, a_send_newline, 10),
            (pexpect.TIMEOUT, [2], -1, None, 0),
            (pexpect.TIMEOUT, [3, 7], -1, ConnectionTimeoutError("Connection Timeout", self.hostname), 0),
            (driver.unable_to_connect_re, [0, 1, 2], -1, a_unable_to_connect, 0),
        ]
        self.log("EXPECTED_PROMPT={}".format(pattern_to_str(self.device.prompt_re)))
        fsm = FSM("TELNET-AUTH", self.device, events, transitions, timeout=_C['connect_timeout'],
                  init_pattern=self.last_pattern)
        return fsm.run()

    def disconnect(self, device):
        """Disconnect using protocol specific method."""
        # self.device.ctrl.sendcontrol(']')
        # self.device.ctrl.sendline('quit')
        self.log("TELNET disconnect")
        try:
            self.device.ctrl.send(chr(4))
        except OSError:
            self.log("Protocol already disconnected")


class TelnetConsole(Telnet):
    """Telnet to the console protocol implementation."""

    def connect(self, driver):
        """Connect using console specific FSM."""
        #              0            1                    2                      3
        events = [ESCAPE_CHAR, driver.press_return_re, driver.standby_re, driver.username_re,
                  #            4                   5            6                     7
                  driver.password_re, driver.more_re, self.device.prompt_re, driver.rommon_re,
                  #       8                           9              10             11
                  driver.unable_to_connect_re, driver.timeout_re, pexpect.TIMEOUT, PASSWORD_OK]

        transitions = [
            (ESCAPE_CHAR, [0], 1, a_send_newline, _C['esc_char_timeout']),
            (driver.press_return_re, [0, 1], 1, a_send_newline, 10),
            (PASSWORD_OK, [0, 1], 1, a_send_newline, 10),
            (driver.standby_re, [0, 1, 5], -1, ConnectionError("Standby console", self.hostname), 0),
            (driver.username_re, [0, 1, 5, 6], -1, partial(a_save_last_pattern, self), 0),
            (driver.password_re, [0, 1, 5], -1, partial(a_save_last_pattern, self), 0),
            (driver.more_re, [0, 5], 7, partial(a_send, "q"), 10),
            # router sends it again to delete
            (driver.more_re, [7], 8, None, 10),
            # (prompt, [0, 1, 5], 6, a_send_newline, 10),
            (self.device.prompt_re, [0, 5], 0, None, 10),
            (self.device.prompt_re, [1, 6, 8, 5], -1, partial(a_save_last_pattern, self), 0),
            (driver.rommon_re, [0, 1, 5], -1, partial(a_save_last_pattern, self), 0),
            (driver.unable_to_connect_re, [0, 1], -1, a_unable_to_connect, 0),
            (driver.timeout_re, [0, 1], -1, ConnectionTimeoutError("Connection Timeout", self.hostname), 0),
            (pexpect.TIMEOUT, [0, 1], 5, a_send_newline, 10),
            (pexpect.TIMEOUT, [5], -1, ConnectionTimeoutError("Connection timeout", self.hostname), 0)
        ]
        self.log("EXPECTED_PROMPT={}".format(pattern_to_str(self.device.prompt_re)))
        fsm = FSM("TELNET-CONNECT-CONSOLE", self.device, events, transitions, timeout=_C['connect_timeout'],
                  init_pattern=None)
        return fsm.run()

    def disconnect(self, driver):
        """Disconnect from the console."""
        self.log("TELNETCONSOLE disconnect")
        try:
            while self.device.mode != 'global':
                self.device.send('exit', timeout=10)
        except OSError:
            self.log("TELNETCONSOLE already disconnected")
        except pexpect.TIMEOUT:
            self.log("TELNETCONSOLE unable to get the root prompt")

        try:
            self.device.ctrl.send(chr(4))
        except OSError:
            self.log("TELNETCONSOLE already disconnected")
