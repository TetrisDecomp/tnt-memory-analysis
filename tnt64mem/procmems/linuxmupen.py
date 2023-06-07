import sys

from .linux import LinuxProcessMemory

class LinuxMupenMemory(LinuxProcessMemory):
    def __init__(self, cos, *args, **kwargs):
        super().__init__(*args, **kwargs)

        p = self.find_process('mupen64plus')
        if p is None:
            print("process not found: mupen64plus", file=sys.stderr)
            sys.exit(1)

        self.open_mem(p.pid)

        """
        &ConfigOpenSection is 0x7f9c77369d20
        > dump 7f9c77369d20 112
        0x7f9c77369d20: 10 53 A1 98 9C 7F 00 00 F0 64 A1 98 9C 7F 00 00
        0x7f9c77369d30: 70 5F A1 98 9C 7F 00 00 20 62 A1 98 9C 7F 00 00
        0x7f9c77369d40: 60 73 63 FB AE 55 00 00 50 5D A1 98 9C 7F 00 00
        0x7f9c77369d50: A4 21 4E FA AE 55 00 00 20 9E 4D FA AE 55 00 00
        0x7f9c77369d60: 00 00 00 00 01 00 00 00 01 00 00 00 46 06 00 00
        0x7f9c77369d70: 87 05 00 00 00 00 00 00 30 9B 62 FB AE 55 00 00
        0x7f9c77369d80: 00 00 00 88 9C 7F 00 00 00 00 00 78 9C 7F 00 00
                                                ^^^^^^^^^^^^^^^^^^^^^^^
        """

        self.set_offset(self.deref(cos + 13 * 8, 8) - 0x80000000)
