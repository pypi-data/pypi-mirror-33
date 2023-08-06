import re
import sys
from .common import VlabException
from .vlab import Vlab
from threading import Event


def init_vlab(args):
    registers_trace = False
    functions_trace = False
    interrupts_trace = False
    if args.traces_list:
        for trace in args.traces_list.split(','):
            if trace == 'registers' or trace == 'regs':
                registers_trace = True
            elif trace == 'functions':
                functions_trace = True
            elif trace == 'interrupts':
                interrupts_trace = True
            else:
                raise VlabException(
                    'jumper run: error: Invalid trace type {}. Valid traces are regs, functions, interrupts'.format(
                        trace), 1)

    vlab = Vlab(
        working_directory=args.working_directory,
        sudo_mode=args.sudo_mode,
        gdb_mode=args.gdb_mode,
        registers_trace=registers_trace,
        functions_trace=functions_trace,
        interrupts_trace=interrupts_trace,
        trace_output_file=args.trace_output_file,
        print_uart=args.print_uart,
        uart_output_file=args.uart_output_file,
        uart_device=args.uart_device,
        platform=args.platform,
        token=args.token,
        debug_peripheral=args.debug_peripheral,
        gpio=args.gpio
    )

    vlab.load(args.fw)

    return vlab


def stop_after_parse(stop_after):
    def raise_invalid_time():
        print('Invalid time format for --stop-after: {}'.format(stop_after))
        return None

    match = re.match('^\d+',stop_after)
    if not match:
        return raise_invalid_time()
    ns = int(match.group(0))

    if re.match('^\d+$', stop_after) or re.match('^\d+ms$', stop_after):
        ns = ns * 1000 * 1000
    elif re.match('^\d+s$', stop_after):
        ns = ns * 1000 * 1000 * 1000
    elif re.match('^\d+us$', stop_after):
        ns = ns * 1000
    elif re.match('^\d+ns$', stop_after):
        pass
    else:
        return raise_invalid_time()

    return ns


class VlabRunner:
    def __init__(self):
        self.stop = Event()
        self.stop.clear()
        pass

    def _exit_callback(self, error_code, error_msg):
        # error_code & error_msg not it use here, but part of callback interface

        self.stop_run()

    def start(self, args):
        try:
            def bkpt_callback(code):
                print('Firmware reached a BKPT instruction with code {}'.format(code))
                self.stop.set()

            vlab = init_vlab(args)
            vlab.on_bkpt(bkpt_callback)
            vlab.register_on_exit(self._exit_callback)
            ns = None

            if args.stop_after:
                vlab._send_stop_after_event()

                ns = stop_after_parse(args.stop_after)
                if ns is None:
                    return 1

            vlab.start(0)

            if not args.print_uart and not args.traces_list:
                print(
                    '\nVirtual device is running without UART/Trace prints (use -u and/or -t to get your firmware '
                    'execution status)\n')
            else:
                print('\nVirtual device is running.\n')
                sys.stdout.flush()


            if ns:
                vlab.SUDO.set_timer(ns, self.stop_run)
            vlab.resume()

            self.wait_to_finish()

            vlab.stop()
            return vlab.get_return_code()

        except VlabException as e:
            print('jumper run: error: {}'.format(e.message))
            try:
                if vlab:
                    vlab.stop()
            finally:
                return e.exit_code

    def stop_wait(self):
        while not self.stop.wait(timeout=0.1):
            pass

    def stop_run(self):
        self.stop.set()

    def wait_to_finish(self):
        self.stop.wait()