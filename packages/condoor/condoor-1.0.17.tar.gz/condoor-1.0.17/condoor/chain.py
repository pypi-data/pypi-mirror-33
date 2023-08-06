"""Provides the Chain class keeping the information about intermediate devices (jumphosts) on the paths to target."""
import re
import logging

from condoor.device import Device
from condoor.hopinfo import make_hop_info_from_url
from condoor.controller import Controller
from condoor.protocols import make_protocol
from condoor.exceptions import ConnectionError, CommandSyntaxError, CommandError


def device_gen(chain, urls):
    """Device object generator."""
    itr = iter(urls)
    last = next(itr)
    for url in itr:
        yield Device(chain, make_hop_info_from_url(last), driver_name='jumphost', is_target=False)
        last = url
    yield Device(chain, make_hop_info_from_url(last), driver_name='generic', is_target=True)


class Chain(object):
    """Chain class keeping information about the intermediate jumphosts and target device."""

    def __init__(self, connection, urls):
        """Initialize the new Chain object."""
        self.connection = connection
        self.ctrl = Controller(connection)
        self.devices = [device for device in device_gen(self, urls)]
        self.target_device.driver_name = 'generic'
        self.target_device.is_target = True

    def __repr__(self):
        """Return the string representation of devices in the chain."""
        name = ""
        for device in self.devices:
            name += "->{}".format(str(device))
        return name[2:]

    def connect(self):
        """Connect to the target device using the intermediate jumphosts."""
        device = None
        # logger.debug("Connecting to: {}".format(str(self)))
        for device in self.devices:
            if not device.connected:
                self.connection.emit_message("Connecting {}".format(str(device)), log_level=logging.INFO)
                protocol_name = device.get_protocol_name()
                device.protocol = make_protocol(protocol_name, device)
                command = device.protocol.get_command()
                self.ctrl.spawn_session(command=command)
                try:
                    result = device.connect(self.ctrl)
                except CommandSyntaxError as exc:
                    # all commands during discovery provides itself in exception except
                    # spawn session which is handled differently. If command syntax error is detected during spawning
                    # a new session then the problem is either on jumphost or csm server.
                    # The problem with spawning session is detected in connect FSM for telnet and ssh.
                    if exc.command:
                        cmd = exc.command
                        host = device.hostname
                    else:
                        cmd = command
                        host = "Jumphost/CSM"

                    self.connection.log(
                        "Command not supported or not authorized on {}: '{}'".format(host, cmd))
                    raise CommandError(message="Command not supported or not authorized",
                                       command=cmd,
                                       host=host)

                if result:
                    # logger.info("Connected to {}".format(device))
                    self.connection.emit_message("Connected {}".format(device), log_level=logging.INFO)
                else:
                    if device.last_error_msg:
                        message = device.last_error_msg
                        device.last_error_msg = None
                    else:
                        message = "Connection error"

                    self.connection.log(message)
                    raise ConnectionError(message)  # , host=str(device))

        if device is None:
            raise ConnectionError("No devices")

        return True

    def disconnect(self):
        """Disconnect from the device."""
        self.target_device.disconnect()
        self.ctrl.disconnect()
        self.tail_disconnect(-1)

    @property
    def target_device(self):
        """Return the target device object (last) in the chain."""
        try:
            return self.devices[-1]
        except IndexError:
            return None

    @property
    def is_connected(self):
        """Return if target device is connected."""
        if self.ctrl and self.ctrl.is_connected:
            # FIXME: Walk through device and check is_connected
            return True
        else:
            return False

    @property
    def is_discovered(self):
        """Return if target device is discovered."""
        if self.target_device is None:
            return False

        if None in (self.target_device.version_text, self.target_device.os_type, self.target_device.os_version,
                    self.target_device.inventory_text, self.target_device.family, self.target_device.platform):
            return False
        return True

    @property
    def is_console(self):
        """Return is target device is connected over console."""
        if self.target_device is None:
            return False

        return self.target_device.is_console

    def get_previous_prompts(self, device):
        """Return the list of intermediate prompts. All except target."""
        device_index = self.devices.index(device)
        prompts = [re.compile("(?!x)x")] + \
                  [dev.prompt_re for dev in self.devices[:device_index] if dev.prompt_re is not None]
        return prompts

    def get_device_index_based_on_prompt(self, prompt):
        """Return the device index in the chain based on prompt."""
        conn_info = ""
        for device in self.devices:
            conn_info += str(device) + "->"
            if device.prompt == prompt:
                self.connection.log("Connected: {}".format(conn_info))
                return self.devices.index(device)
        else:
            return None

    def tail_disconnect(self, index):
        """Mark all devices disconnected except target in the chain."""
        try:
            for device in self.devices[index + 1:]:
                device.connected = False
        except IndexError:
            pass

    def send(self, cmd, timeout, wait_for_string, password):
        """Send command to the target device."""
        return self.target_device.send(cmd, timeout=timeout, wait_for_string=wait_for_string, password=password)

    def update(self, data):
        """Update the chain object with the predefined data."""
        if data is None:
            for device in self.devices:
                device.clear_info()
        else:
            for device, device_info in zip(self.devices, data):
                device.device_info = device_info
                self.connection.log("Device information updated -> [{}]".format(device))
