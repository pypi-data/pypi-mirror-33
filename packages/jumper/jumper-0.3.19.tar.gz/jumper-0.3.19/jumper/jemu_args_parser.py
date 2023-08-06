import argparse
from .vlab import Vlab
from os import getcwd
from . import __version__


class _VersionAction(argparse.Action):
    def __init__(self,
                 option_strings,
                 version=None,
                 dest=argparse.SUPPRESS,
                 default=argparse.SUPPRESS,
                 help="show program's version number and exit"):
        super(_VersionAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            default=default,
            nargs=0,
            help=help)
        self.version = version

    def __call__(self, parser, namespace, values, option_string=None):
        version = self.version
        if version is None:
            version = parser.version
        formatter = parser._get_formatter()
        formatter.add_text(version)
        Vlab.check_sdk_version(False)
        parser.exit(message=formatter.format_help())


class JemuArgsParser:
    def __init__(self):
        self.args_parsed = None

    def parse(self, args):
        parser = argparse.ArgumentParser(
            prog='jumper',
            description="CLI interface for using Jumper's emulator"
        )

        parser.add_argument('--version', action=_VersionAction, version='%(prog)s {}'.format(__version__))
        parser.add_argument('--token', default=None, dest='token', type=str, help='Your secret token')

        subparsers = parser.add_subparsers(title='Commands', dest='command')

        login_parser = subparsers.add_parser(
            'login', help='Login through a URL, does not work on servers without a desktop and browser'
        )

        run_parser = subparsers.add_parser(
            'run',
            help='Executes a FW file on a virtual device. Currently only support nRF52 devices'
        )
        run_parser.add_argument(
            '--fw',
            '--bin',
            '-b ',
            help="Firmware to be flashed to the virtual device (supported extensions are bin, out, elf, hex). In case more than one file needs to be flashed (such as using Nordic's softdevice), the files should be merged first. Check out https://vlab.jumper.io/docs#softdevice for more details",
        )

        run_parser.add_argument(
            '--debug-peripheral',
            action='store_true',
            help="Debug peripherals, enables to attach debugger to pid",
            default=False,
            dest='debug_peripheral'
        )

        run_parser.add_argument(
            '--directory',
            '-d ',
            help='Working directory, should include the board.json and scenario.json files. Default is current working directory',
            default=getcwd(),
            dest='working_directory'
        )

        run_parser.add_argument(
            '--sudo',
            '-s ',
            help='Run in sudo mode => FW can write to read-only registers. This should usually be used for testing low-level drivers, fuzzing (error injection) and certification tests.',
            action='store_true',
            default=False,
            dest='sudo_mode'
        )

        run_parser.add_argument(
            '--gdb',
            '-g ',
            help='Opens a GDB port for debugging the FW on port 5555. The FW will not start running until the GDB client connects.',
            action='store_true',
            default=False,
            dest='gdb_mode'
        )

        run_parser.add_argument(
            '--version',
            '-v ',
            help='Jumper sdk version.',
            action='store_true',
            default=False
        )

        run_parser.add_argument(
            '--trace',
            '-t ',
            help=
            """
            Prints a trace report to stdout.
            Valid reports: regs,interrupts,functions. (the functions trace can only be used with an out/elf file) 
            Example: jumper run --fw my_bin.bin -t interrupts,regs --trace-dest trace.txt
            Default value: regs 
            This can be used with --trace-dest to forward it to a file.
            """,
            const='regs',  # default when there are 0 arguments
            nargs='?',  # 0-or-1 arguments
            dest='traces_list'
        )

        run_parser.add_argument(
            '--trace-dest',
            type=str,
            help=
            """
            Forwards the trace report to a destination file. Must be used with -t.
            To print to stdout, just hit -t.
            """,
            default='',
            dest='trace_output_file'
        )

        run_parser.add_argument(
            '--uart',
            '-u ',
            action='store_true',
            default=False,
            help='Forwards UART prints to stdout, this can be used with --uart-dest to forward it to a file.',
            dest='print_uart'
        )

        run_parser.add_argument(
            '--uart-dest',
            type=str,
            help=
            """
            Forwards UART prints to a destination file. This MUST be used -u with this flag to make it work.
            To print to stdout, just hit -u.
            """,
            default=None,
            dest='uart_output_file'
        )

        run_parser.add_argument(
            '--uart-device',
            action='store_true',
            default=False,
            help='Creates a "uart" file in the working directory which is linked to the virtual UART device. Can be used with "screen". Linux only',
            dest='uart_device'
        )

        run_parser.add_argument(
            "--gpio",
            help=
            """
            Prints GPIO events (pin changes) to stdout.
            """,
            action='store_true',
            default=False,
        )

        run_parser.add_argument(
            '--platform',
            '-p ',
            type=str,
            choices=['nrf52832', 'stm32f4'],
            help=
            """
            Sets platform type. (Valid platforms: nrf52832,stm32f4).
            """,
            default=None,
            dest='platform'
        )

        run_parser.add_argument(
            '--stop-after',
            type=str,
            help=
            """
            Stop the execution after a specific amount of time. Units should be stated, if no units are stated, time in ms is assumed.
            Examples: "--stop-after 1s, --stop-after 1000ms, --stop-after 1000000us, --stop-after 1000000000ns" 
            """,
            default=None,
            dest='stop_after'
        )

        subparsers.add_parser(
            'ble',
            help='Creates a virtual HCI device (BLE dongle) for regular Linux/Bluez programs to communicate with virtual devices'
        )

        self.args_parsed = parser.parse_args(args)

    def get_args(self):
        return self.args_parsed