"""This is IOS river implementation."""

from functools import partial
import re
import pexpect

from condoor.drivers.generic import Driver as Generic
from condoor.actions import a_send_password, a_expected_prompt, a_send_line, a_send, a_disconnect, a_reconnect
from condoor.exceptions import ConnectionAuthenticationError, ConnectionError, CommandError, CommandSyntaxError, \
    CommandTimeoutError
from condoor.fsm import FSM


SAVE_CONFIG = re.compile(re.escape("System configuration has been modified. Save? [yes/no]: "))
PROCEED = re.compile(re.escape("Proceed with reload? [confirm]"))


class Driver(Generic):
    """This is a Driver class implementation for IOS."""

    platform = 'IOS'
    inventory_cmd = 'show inventory'
    users_cmd = 'show users'
    enable_cmd = 'enable'
    reload_cmd = 'reload'
    target_prompt_components = ['prompt_dynamic', 'prompt_default', 'rommon']
    prepare_terminal_session = ['terminal len 0', 'terminal width 0']
    families = {
        'A9': 'ASR900',
        'IOSv': 'IOSv',
    }

    def __init__(self, device):
        """Initialize the IOS Driver object."""
        super(Driver, self).__init__(device)

    def get_version_text(self):
        """Return the version information from IOS device."""
        version_text = None
        try:
            version_text = self.device.send("show version", timeout=120)
        except CommandError as exc:
            exc.command = 'show version'
            raise exc

        return version_text

    def enable(self, enable_password):
        """Change to the privilege mode."""
        if self.device.prompt[-1] == '#':
            self.log("Device is already in privileged mode")
            return

        events = [self.password_re, self.device.prompt_re, pexpect.TIMEOUT, pexpect.EOF]
        transitions = [
            (self.password_re, [0], 1, partial(a_send_password, enable_password), 10),
            (self.password_re, [1], -1, ConnectionAuthenticationError("Incorrect enable password",
                                                                      self.device.hostname), 0),
            (self.device.prompt_re, [0, 1, 2, 3], -1, a_expected_prompt, 0),
            (pexpect.TIMEOUT, [0, 1, 2], -1, ConnectionAuthenticationError("Unable to get privileged mode",
                                                                           self.device.hostname), 0),
            (pexpect.EOF, [0, 1, 2], -1, ConnectionError("Device disconnected"), 0)
        ]
        self.device.ctrl.send_command(self.enable_cmd)
        fsm = FSM("IOS-ENABLE", self.device, events, transitions, timeout=10, max_transitions=5)
        fsm.run()
        if self.device.prompt[-1] != '#':
            raise ConnectionAuthenticationError("Privileged mode not set", self.device.hostname)

    def reload(self, reload_timeout=300, save_config=True):
        """Reload the device.

        CSM_DUT#reload

        System configuration has been modified. Save? [yes/no]: yes
        Building configuration...
        [OK]
        Proceed with reload? [confirm]
        """
        response = "yes" if save_config else "no"

        events = [SAVE_CONFIG, PROCEED, pexpect.TIMEOUT, pexpect.EOF]

        transitions = [
            (SAVE_CONFIG, [0], 1, partial(a_send_line, response), 60),
            (PROCEED, [0, 1], 2, partial(a_send, "\r"), reload_timeout),
            # if timeout try to send the reload command again
            (pexpect.TIMEOUT, [0], 0, partial(a_send_line, self.reload_cmd), 10),
            (pexpect.TIMEOUT, [2], -1, a_reconnect, 0),
            (pexpect.EOF, [0, 1, 2], -1, a_disconnect, 0)
        ]
        fsm = FSM("IOS-RELOAD", self.device, events, transitions, timeout=10, max_transitions=5)
        return fsm.run()

    def config(self, config_text, plane):
        """Apply config."""
        nol = config_text.count('\n')
        config_lines = iter(config_text.splitlines())
        events = [self.prompt_re, self.syntax_error_re]
        transitions = [
            (self.prompt_re, [0], 0, partial(a_send_line, config_lines), 10),
            (self.syntax_error_re, [0], -1, CommandSyntaxError("Configuration syntax error."), 0)
        ]
        self.device.ctrl.send_command(self.config_cmd)
        fsm = FSM("CONFIG", self.device, events, transitions, timeout=10, max_transitions=nol + 5)
        fsm.run()

        # after the configuration the hostname may change. Need to detect it again
        try:
            self.device.send("", timeout=2)
        except CommandTimeoutError:
            prompt = self.device.ctrl.detect_prompt()
            self.device.prompt_re = self.make_dynamic_prompt(prompt)
            self.device.update_config_mode(prompt)

        if self.device.mode == "config":
            self.device.send("end")

        self.device.send("write memory")

        return "NO-COMMIT-ID"
