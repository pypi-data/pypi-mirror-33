"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""


class JemuButton(object):
    _id = None
    _jemu_connection = None
    _LEVEL_HIGH = 1
    _LEVEL_LOW = 0

    _PIN_LEVEL = "pin_level"
    _COMMAND = "command"
    _COMMAND_PIN_LOGIC_LEVEL = "set_pin_level"
    _EXTERNAL_PERIPHERAL = "External"

    def _button_gpio_json(self, level):
        return {
            self._PIN_LEVEL: level,
            self._COMMAND: self._COMMAND_PIN_LOGIC_LEVEL,
        }

    def __init__(self, jemu_connection, id):
        self._id = id
        self._jemu_connection = jemu_connection

    def on(self):
        self._jemu_connection.send_command(self._button_gpio_json(self._LEVEL_LOW), self._id, self._EXTERNAL_PERIPHERAL)

    def off(self):
        self._jemu_connection.send_command(self._button_gpio_json(self._LEVEL_HIGH), self._id, self._EXTERNAL_PERIPHERAL)

    def id(self):
        return self._id
