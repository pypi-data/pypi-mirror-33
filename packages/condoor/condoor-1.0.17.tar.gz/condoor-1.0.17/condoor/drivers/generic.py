"""This is generic driver class implementation."""

from functools import partial
import re
import pexpect

from condoor.actions import a_send, a_connection_closed, a_stays_connected, a_unexpected_prompt, a_expected_prompt
from condoor.fsm import FSM
from condoor.exceptions import ConnectionError, CommandError, CommandSyntaxError, CommandTimeoutError
from condoor.utils import pattern_to_str

from condoor import pattern_manager
from condoor.config import CONF


class Driver(object):
    """This is generic Driver class implementation."""

    platform = 'generic'
    inventory_cmd = None
    users_cmd = None
    target_prompt_components = ['prompt_dynamic']
    prepare_terminal_session = ['terminal len 0']
    config_cmd = 'configure terminal'
    families = {}

    def __init__(self, device):
        """Initialize the Driver object."""
        self.device = device

        # FIXME: Do something with this, it's insane
        self.prompt_re = pattern_manager.pattern(self.platform, 'prompt')
        self.syntax_error_re = pattern_manager.pattern(self.platform, 'syntax_error')
        self.connection_closed_re = pattern_manager.pattern(self.platform, 'connection_closed')
        self.press_return_re = pattern_manager.pattern(self.platform, 'press_return')
        self.more_re = pattern_manager.pattern(self.platform, 'more')
        self.rommon_re = pattern_manager.pattern(self.platform, 'rommon')
        self.buffer_overflow_re = pattern_manager.pattern(self.platform, 'buffer_overflow')

        self.username_re = pattern_manager.pattern(self.platform, 'username')
        self.password_re = pattern_manager.pattern(self.platform, 'password')
        self.authentication_error_re = pattern_manager.pattern(self.platform, 'authentication_error')
        self.unable_to_connect_re = pattern_manager.pattern(self.platform, 'unable_to_connect')
        self.timeout_re = pattern_manager.pattern(self.platform, 'timeout')
        self.standby_re = pattern_manager.pattern(self.platform, 'standby')

        self.pid2platform_re = pattern_manager.pattern(self.platform, 'pid2platform')
        self.platform_re = pattern_manager.pattern(self.platform, 'platform', compiled=False)
        self.version_re = pattern_manager.pattern(self.platform, 'version', compiled=False)
        self.vty_re = pattern_manager.pattern(self.platform, 'vty')
        self.console_re = pattern_manager.pattern(self.platform, 'console')

        self.plane = 'sdr'

        self.log = device.chain.connection.log
        self.platform_string = ""
        self.raw_family = None

    def __repr__(self):
        """Return the string representation of the driver class."""
        return str(self.platform)

    def get_version_text(self):
        """Return the version information from the device."""
        show_version_brief_not_supported = False
        version_text = None
        try:
            version_text = self.device.send("show version brief", timeout=120)
        except CommandError:
            show_version_brief_not_supported = True

        if show_version_brief_not_supported:
            try:
                # IOS Hack - need to check if show version brief is supported on IOS/IOS XE
                version_text = self.device.send("show version", timeout=120)
            except CommandError as exc:
                exc.command = 'show version'
                raise exc

        return version_text

    def get_inventory_text(self):
        """Return the inventory information from the device."""
        inventory_text = None
        if self.inventory_cmd:
            try:
                inventory_text = self.device.send(self.inventory_cmd, timeout=120)
                self.log('Inventory collected')
            except CommandError:
                self.log('Unable to collect inventory')
        else:
            self.log('No inventory command for {}'.format(self.platform))
        return inventory_text

    def get_hostname_text(self):  # pylint: disable=no-self-use
        """Return the hostname information from the device."""
        return None

    def get_users_text(self):
        """Return the users logged in information from the device."""
        users_text = None
        if self.users_cmd:
            try:
                users_text = self.device.send(self.users_cmd, timeout=60)
            except CommandError:
                self.log('Unable to collect connected users information')
        else:
            self.log('No users command for {}'.format(self.platform))
        return users_text

    def get_os_type(self, version_text):  # pylint: disable=no-self-use
        """Return the OS type information from the device."""
        os_type = None
        if version_text is None:
            return os_type

        match = re.search("(XR|XE|NX-OS)", version_text)
        if match:
            os_type = match.group(1)
        else:
            os_type = 'IOS'

        if os_type == "XR":
            match = re.search("Build Information", version_text)
            if match:
                os_type = "eXR"
            match = re.search("XR Admin Software", version_text)
            if match:
                os_type = "Calvados"
        return os_type

    def get_os_version(self, version_text):
        """Return the OS version information from the device."""
        os_version = None
        if version_text is None:
            return os_version
        match = re.search(self.version_re, version_text, re.MULTILINE)
        if match:
            os_version = match.group(1)

        return os_version

    def get_hw_family(self, version_text):
        """Return the HW family information from the device."""
        family = None
        if version_text is None:
            return family

        match = re.search(self.platform_re, version_text, re.MULTILINE)
        if match:
            self.platform_string = match.group()
            self.log("Platform string: {}".format(match.group()))
            self.raw_family = match.group(1)
            # sort keys on len reversed (longest first)
            for key in sorted(self.families, key=len, reverse=True):
                if self.raw_family.startswith(key):
                    family = self.families[key]
                    break
            else:
                self.log("Platform {} not supported".format(family))
        else:
            self.log("Platform string not present. Refer to CSCux08958")
        return family

    def get_hw_platform(self, udi):
        """Return th HW platform information from the device."""
        platform = None
        try:
            pid = udi['pid']
            if pid == '':
                self.log("Empty PID. Use the hw family from the platform string.")
                return self.raw_family
            match = re.search(self.pid2platform_re, pid)
            if match:
                platform = match.group(1)
        except KeyError:
            pass
        return platform

    def is_console(self, users_text):
        """Return if device is connected over console."""
        if users_text is None:
            self.log("Console information not collected")
            return None

        for line in users_text.split('\n'):
            if '*' in line:
                match = re.search(self.vty_re, line)
                if match:
                    self.log("Detected connection to vty")
                    return False
                else:
                    match = re.search(self.console_re, line)
                    if match:
                        self.log("Detected connection to console")
                        return True

        self.log("Connection port unknown")
        return None

    def update_driver(self, prompt):
        """Update driver based on the prompt."""
        # Do not update the driver if not target device
        return pattern_manager.platform(prompt) if self.device.is_target else None

    def wait_for_string(self, expected_string, timeout=60):
        """Wait for string FSM."""
        #                    0                         1                        2                        3
        events = [self.syntax_error_re, self.connection_closed_re, expected_string, self.press_return_re,
                  #        4           5                 6                7
                  self.more_re, pexpect.TIMEOUT, pexpect.EOF, self.buffer_overflow_re]

        # add detected prompts chain
        events += self.device.get_previous_prompts()  # without target prompt

        self.log("Expecting: {}".format(pattern_to_str(expected_string)))

        transitions = [
            (self.syntax_error_re, [0], -1, CommandSyntaxError("Command unknown", self.device.hostname), 0),
            (self.connection_closed_re, [0], 1, a_connection_closed, 10),
            (pexpect.TIMEOUT, [0], -1, CommandTimeoutError("Timeout waiting for prompt", self.device.hostname), 0),
            (pexpect.EOF, [0, 1], -1, ConnectionError("Unexpected device disconnect", self.device.hostname), 0),
            (self.more_re, [0], 0, partial(a_send, " "), 10),
            (expected_string, [0, 1], -1, a_expected_prompt, 0),
            (self.press_return_re, [0], -1, a_stays_connected, 0),
            # TODO: Customize in XR driver
            (self.buffer_overflow_re, [0], -1, CommandSyntaxError("Command too long", self.device.hostname), 0)
        ]

        for prompt in self.device.get_previous_prompts():
            transitions.append((prompt, [0, 1], 0, a_unexpected_prompt, 0))

        fsm = FSM("WAIT-4-STRING", self.device, events, transitions, timeout=timeout)
        return fsm.run()

    # def send_xml(self, command, timeout=60):
    #     """
    #     Handle error i.e.
    #     ERROR: 0x24319600 'XML-TTY' detected the 'informational' condition
    #     'The XML TTY Agent has not yet been started.
    #     Check that the configuration 'xml agent tty' has been committed.'
    #     """
    #     self._debug("Starting XML TTY Agent")
    #     result = self.send("xml")
    #     self._info("XML TTY Agent started")
    #
    #     result = self.send(command, timeout=timeout)
    #     self.ctrl.sendcontrol('c')
    #     return result

    # def netconf(self, command):
    #     """
    #     Handle error i.e.
    #     ERROR: 0x24319600 'XML-TTY' detected the 'informational' condition
    #     'The XML TTY Agent has not yet been started.
    #     Check that the configuration 'xml agent tty' has been committed.'
    #     """
    #     self._debug("Starting XML TTY Agent")
    #     result = self.send("netconf", wait_for_string=']]>]]>')
    #     self._info("XML TTY Agent started")
    #
    #     self.ctrl.send(command)
    #     self.ctrl.send("\r\n")
    #     self.ctrl.expect("]]>]]>")
    #     result = self.ctrl.before
    #     self.ctrl.sendcontrol('c')
    #     self.send()
    #     return result

    def enable(self, enable_password):
        """Change the device mode to privileged.

        If device does not support privileged mode the
        the informational message to the log will be posted.

        Args:
            enable_password (str): The privileged mode password. This is optional parameter. If password is not
                provided but required the password from url will be used. Refer to :class:`condoor.Connection`
        """
        self.log("Privileged mode not supported on {} platform".format(self.platform))

    def reload(self, reload_timeout=300, save_config=True):
        """Reload the device and waits for device to boot up.

        It posts the informational message to the log if not implemented by device driver.
        """
        self.log("Reload not implemented on {} platform".format(self.platform))

    def after_connect(self):
        """Execute right after connecting to the device."""
        pass

    def base_prompt(self, prompt):
        """Extract the base prompt pattern."""
        if prompt is None:
            return None
        if not self.device.is_target:
            return prompt
        pattern = pattern_manager.pattern(self.platform, "prompt_dynamic", compiled=False)
        pattern = pattern.format(prompt="(?P<prompt>.*?)")
        result = re.search(pattern, prompt)
        if result:
            base = result.group("prompt") + "#"
            self.log("base prompt: {}".format(base))
            return base
        else:
            self.log("Unable to extract the base prompt")
            return prompt

    def make_dynamic_prompt(self, prompt):
        """Extend prompt with flexible mode handling regexp."""
        patterns = ["[\r\n]" + pattern_manager.pattern(
            self.platform, pattern_name, compiled=False) for pattern_name in self.target_prompt_components]

        hostname = self.update_hostname(prompt)
        # patterns_re = "|".join(patterns).format(prompt=re.escape(prompt[:-1]))
        patterns_re = "|".join(patterns).format(hostname=re.escape(hostname))

        try:
            prompt_re = re.compile(patterns_re, re.MULTILINE)
        except re.error as e:  # pylint: disable=invalid-name
            raise RuntimeError("Pattern compile error: {} ({}:{})".format(e.message, self.platform, patterns_re))

        self.log("Platform: {} -> Dynamic prompt: '{}'".format(self.platform, repr(prompt_re.pattern)))
        return prompt_re

    def update_config_mode(self, prompt):  # pylint: disable=no-self-use
        """Update config mode based on the prompt analysis."""
        mode = 'global'
        if prompt:
            if 'config' in prompt:
                mode = 'config'
            elif 'admin' in prompt:
                mode = 'admin'

        self.log("Mode: {}".format(mode))
        return mode

    def update_hostname(self, prompt):
        """Update the hostname based on the prompt analysis."""
        result = re.search(self.prompt_re, prompt)
        if result:
            hostname = result.group('hostname')
            self.log("Hostname detected: {}".format(hostname))
        else:
            hostname = self.device.hostname
            self.log("Hostname not set: {}".format(prompt))
        return hostname

    def config(self, text, plane):
        """Apply config."""
        self.log("Device configuration not supported.")
        return None

    def rollback(self, label, plane):
        """Rollback config."""
        self.log("Device configuration rollback not supported.")
        return None

    def enter_plane(self, plane):
        """Enter the device plane.

        Enter the device plane a.k.a. mode, i.e. admin, qnx, calvados
        """
        try:
            cmd = CONF['driver'][self.platform]['planes'][plane]
            self.plane = plane
        except KeyError:
            cmd = None

        if cmd:
            self.log("Entering the {} plane".format(plane))
            self.device.send(cmd)

    def exit_plane(self):
        """Exit the device plane."""
        if self.plane != 'sdr':
            self.device.send('exit')
