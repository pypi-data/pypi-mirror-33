"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from threading import Lock
from common import JemuConnectionException


class JemuGpio:
    _PIN_NUM = "pin_number"
    _TRANSITION_TYPE = "transition_type"
    _DESCRIPTION = "description"
    _PIN_LEVEL_EVENT = "pin_level_event"
    _PIN_LEVEL = "pin_level"
    _PIN_NUMBER = "pin_number"
    _GET_PIN_LEVEL = "get_pin_level"
    _SET_PIN_LEVEL = "set_pin_level"
    _VALUE_RESPONSE = "value_response"
    _DEVICE_TIME = "device_time"
    _COMMAND = "command"
    _VALUE = "value"
    _ID = 12

    def __init__(self, mcu_name="nrf52832"):
        self._pin_level_callback = None
        self._jemu_socket_manager = None
        self._lock = Lock()
        self._peripheral_type = mcu_name

    def on_pin_level_event(self, callback):
        with self._lock:
            self._pin_level_callback = callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._DESCRIPTION] == self._PIN_LEVEL_EVENT:
            with self._lock:
                if self._pin_level_callback:
                    try:
                        self._pin_level_callback(
                            jemu_packet[self._PIN_NUM],
                            jemu_packet[self._TRANSITION_TYPE],
                            jemu_packet[self._DEVICE_TIME]
                        )
                    except TypeError:
                        self._pin_level_callback(jemu_packet[self._PIN_NUM], jemu_packet[self._TRANSITION_TYPE])

    def set_connection_manager(self, jemu_socket_manager):
        self._jemu_socket_manager = jemu_socket_manager
        self._jemu_socket_manager.register(self.receive_packet)

    def _get_pin_level_message(self, pin_num):
        return {
            self._COMMAND: self._GET_PIN_LEVEL,
            self._PIN_NUMBER: pin_num
        }

    def _set_pin_level_message(self, pin_num, pin_level):
        return {
            self._COMMAND: self._SET_PIN_LEVEL,
            self._PIN_LEVEL: pin_level,
            self._PIN_NUMBER: pin_num
        }

    def get_pin_level(self, pin_num):
        jemu_packet = self._jemu_socket_manager.send_command(self._get_pin_level_message(pin_num), self._ID, self._peripheral_type)
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._VALUE_RESPONSE and self._VALUE in jemu_packet:
            return jemu_packet[self._VALUE]
        else:
            raise JemuConnectionException("Error: Couldn't get pin [{}] level".format(pin_num))

    def set_pin_level(self, pin_num, pin_level):
        self._jemu_socket_manager.send_command_async(self._set_pin_level_message(pin_num, pin_level), self._ID, self._peripheral_type)
