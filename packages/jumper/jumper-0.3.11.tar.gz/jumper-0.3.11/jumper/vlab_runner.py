import re
import sys
from time import sleep
from .common import VlabException
from .vlab import Vlab
from threading import Event


class VlabRunner:
    def __init__(self):
        self.stop = Event()
        self.stop.clear()
        pass

    def start(self, args):
        try:
            reached_bkpt = Event()

            def bkpt_callback(code):
                print('Firmware reached a BKPT instruction with code {}'.format(code))
                reached_bkpt.set()

            vlab = VlabRunner.init_vlab(args)
            vlab.on_bkpt(bkpt_callback)
            ns = None

            if args.stop_after:
                vlab._send_stop_after_event()

                def raise_invalid_time():
                    print('Invalid time format for --stop-after: {}'.format(args.stop_after))
                    return 1

                match = re.match('^\d+', args.stop_after)
                if not match:
                    raise_invalid_time()
                ns = int(match.group(0))

                if re.match('^\d+$', args.stop_after) or re.match('^\d+ms$', args.stop_after):
                    ns = ns * 1000 * 1000
                elif re.match('^\d+s$', args.stop_after):
                    ns = ns * 1000 * 1000 * 1000
                elif re.match('^\d+us$', args.stop_after):
                    ns = ns * 1000
                elif re.match('^\d+ns$', args.stop_after):
                    pass
                else:
                    raise_invalid_time()

            if not args.print_uart and not args.traces_list:
                print(
                    '\nVirtual device is running without UART/Trace prints (use -u and/or -t to get your firmware '
                    'execution status)\n')
            else:
                print('\nVirtual device is running\n')
                sys.stdout.flush()

            vlab.start(0)
            if ns:
                vlab.stop_after_ns(ns)
            vlab.resume()

            try:
                while (not reached_bkpt.is_set()) and not self.stop.is_set() and vlab.get_state() == 'running':
                    sleep(0.5)
            except KeyboardInterrupt:
                pass

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

    @staticmethod
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




