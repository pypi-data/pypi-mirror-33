import sys, os

CORE_LINUX_OS = "linux"
CORE_WINDOWS_OS1 = "win"
CORE_WINDOWS_OS2 = "cygwin"
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
elif sys.platform.startswith(CORE_WINDOWS_OS1) or sys.platform.startswith(CORE_WINDOWS_OS2):
    JEMU_DIR = os.path.join(HERE, 'jemu', JEMU_WINDOWS_DIR)


def get_jemu_path():
    jemu_exe = 'jemu.exe' if sys.platform.startswith(CORE_WINDOWS_OS1) or sys.platform.startswith(CORE_WINDOWS_OS2) \
        else 'jemu'
    return os.path.join(JEMU_DIR, jemu_exe)
