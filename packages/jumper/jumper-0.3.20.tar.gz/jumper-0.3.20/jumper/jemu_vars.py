import sys, os

CORE_LINUX_OS = "linux"
CORE_MAC_OS = "darwin"

JEMU_LINUX_DIR = "jemu-linux"
JEMU_MAC_DIR = "jemu-mac"
JEMU_WINDOWS_DIR = "jemu-windows"

HERE = os.path.abspath(os.path.dirname(__file__))

JEMU_DIR = None
if sys.platform.startswith(CORE_LINUX_OS):
    JEMU_DIR = os.path.join(HERE, 'jemu', JEMU_LINUX_DIR)
elif sys.platform.startswith(CORE_MAC_OS):
    JEMU_DIR = os.path.join(HERE, 'jemu', JEMU_MAC_DIR)
elif os.name == 'nt':
    JEMU_DIR = os.path.join(HERE, 'jemu', JEMU_WINDOWS_DIR)


def _get_file_path(filename_without_extension):
    filename = filename_without_extension
    if os.name == 'nt':
        filename += '.exe'
    return os.path.join(JEMU_DIR, filename)


JEMU_PATH = _get_file_path('jemu')
OBJCOPY_PATH = _get_file_path('arm-none-eabi-objcopy')
OBJDUMP_PATH = _get_file_path('arm-none-eabi-objdump')
