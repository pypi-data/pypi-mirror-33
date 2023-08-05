"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from threading import Lock
from time import sleep
from common import TimeoutException
from common import WrongStateError
import sys


class JemuUartJson(object):
    _DESCRIPTION = "description"
    _VALUE_RESPONSE = "value_response"
    _COMMAND = "command"
    _WRITE_DATA = "write_uart_data"
    _READ_DATA = "read_uart_data"
    _UART_EVENT = "uart_event"
    _VALUE = "value"
    _ID = 15  # peripheral id of Uart in nRF52
    _LINE_SEPARATOR = b'\r\n'

    def __init__(self, vlab, mcu_name="nrf52832"):
        self._uart_callback = None
        self._jemu_socket_manager = None
        self._peripheral_type = mcu_name
        self._uart_buffer = None
        self._vlab = vlab
        self._lock = Lock()
        self._print_to_screen = False
        self._callback_read_uart_line = None
        self._lock_callback = Lock()


    def print_uart_to_screen(self):
        self._print_to_screen = True

    def open(self):
        self._uart_buffer = b''
        # TODO: jemu_connection should be a member instead of using a private member from another class
        if self._vlab._jemu_connection:
            self._vlab._jemu_connection.register(self.receive_packet)

    def receive_packet(self, jemu_packet):
        if self._DESCRIPTION in jemu_packet and jemu_packet[self._DESCRIPTION] == self._UART_EVENT and self._VALUE in jemu_packet:
            with self._lock:
                new_data = chr(jemu_packet[self._VALUE])
                if self._print_to_screen:
                    # dansheme 18/4/2018: Flush is needed for testing purposes.
                    # BLE test is setting stdout of this process to PIPE and data is not being flushed automatically
                    # by the kernel.
                    sys.stdout.write(new_data)
                    sys.stdout.flush()
                self._uart_buffer += new_data

            if self._LINE_SEPARATOR not in self._uart_buffer:
                return

            with self._lock_callback:
                if self._callback_read_uart_line:
                    data = self._get_data_line()
                    if data:
                        self._callback_read_uart_line(data)

    def _write_to_uart_message(self, data):
        return {
            self._COMMAND: self._WRITE_DATA,
            self._VALUE: data
        }

    def write(self, data):
        """
         Writes data to UART

         :param data: Data to write
         """
        if self._vlab._jemu_connection:
            self._vlab._jemu_connection.send_command_async(self._write_to_uart_message(data), self._ID,
                                                          self._peripheral_type)

    def read(self):
        """
        :return: data available on the UART device. Returns an empty bytes string if no data is available.
        """
        with self._lock:
            data = self._uart_buffer
            self._uart_buffer = b''
        return data

    def wait_until_uart_receives(self, data, timeout=None):
        """
        Blocks until specified data is received on UART.
        If the device is paused, this function will continue the execution and will pause the device when the data is ready or timeout occured.
        If the device is running, the function will not pause the device.

        :param data: Expected bytes string.
        :param timeout: Emulation time specified in milliseconds. jumper.vlab.TimeoutException is raised if timeout occurred before data was available in the buffer.
        :return: The data available on in the UART buffer when the specified data was received. Note that this can be more than the data provided in the data parameter.
        """
        original_state = self._vlab.get_state()

        if original_state == 'running':
            self._vlab.pause()
        elif original_state != 'paused':
            raise WrongStateError('state should be paused or running but was {}'.format(original_state))

        if timeout is not None:
            self._vlab.stop_after_ms(timeout)

        self._vlab.resume()

        while data not in self._uart_buffer and self._vlab.get_state() == 'running':
            sleep(0.2)

        if timeout is not None:
            self._vlab.cancel_stop()

        if original_state == 'running':
            self._vlab.resume()
        elif original_state == 'paused':
            self._vlab.pause()

        with self._lock:
            if data in self._uart_buffer:
                tmp = self._uart_buffer
                self._uart_buffer = b''
                return tmp

        raise TimeoutException("timeout while waiting for data from uart")

    def read_line(self, line_separator=_LINE_SEPARATOR):
        while line_separator not in self._uart_buffer:
            sleep(0.2)
        return self._get_data_line(line_separator)

    def on_uart_read_line(self, callback):
        with self._lock_callback:
            self._callback_read_uart_line = callback

    def _get_data_line(self, line_separator=_LINE_SEPARATOR):
        with self._lock:
            line_length = self._uart_buffer.find(line_separator) + len(line_separator)
            data = self._uart_buffer[:line_length]
            self._uart_buffer = self._uart_buffer[line_length:]
        return data
