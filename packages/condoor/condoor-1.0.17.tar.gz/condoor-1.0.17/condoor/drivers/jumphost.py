"""This is jumphost driver class implementation."""

import re

from condoor.drivers.generic import Driver as Generic
from condoor import pattern_manager, CommandError, ConnectionError


class Driver(Generic):
    """This is a Driver class implementation for Unix Jumphost."""

    platform = 'jumphost'
    inventory_cmd = None
    target_prompt_components = ['prompt_dynamic']
    prepare_terminal_session = []

    def __init__(self, device):
        """Initialize the Unix Jumphost driver object."""
        super(Driver, self).__init__(device)

    def get_version_text(self):
        """Return the version information from Unix host."""
        try:
            version_text = self.device.send('uname -sr', timeout=10)
        except CommandError:
            self.log("Non Unix jumphost type detected")
            return None
            raise ConnectionError("Non Unix jumphost type detected.")
        return version_text

    def update_hostname(self, prompt):
        """Return the hostname."""
        return self.device.hostname

    def get_hostname_text(self):
        """Return hostname information from the Unix host."""
        # FIXME: fix it, too complex logic
        try:
            hostname_text = self.device.send('hostname', timeout=10)
            if hostname_text:
                self.device.hostname = hostname_text.splitlines()[0]
                return hostname_text
        except CommandError:
            self.log("Non Unix jumphost type detected")
            return None

    def make_dynamic_prompt(self, prompt):
        """Extend prompt with flexible mode handling regexp."""
        patterns = ["[\r\n]" + pattern_manager.pattern(
            self.platform, pattern_name, compiled=False) for pattern_name in self.target_prompt_components]

        patterns_re = "|".join(patterns).format(hostname=re.escape(prompt))

        try:
            prompt_re = re.compile(patterns_re)
        except re.error as e:  # pylint: disable=invalid-name
            raise RuntimeError("Pattern compile error: {} ({}:{})".format(e.message, self.platform, patterns_re))

        self.log("Dynamic prompt: '{}'".format(repr(prompt_re.pattern)))
        return prompt_re
