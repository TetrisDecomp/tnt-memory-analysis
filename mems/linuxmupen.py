import sys

from .linux import LinuxProcessMemory

class LinuxMupenMemory(LinuxProcessMemory):
    def __init__(self, verbose=False):
        super().__init__(verbose=verbose)

        p = self.find_process('mupen64plus')
        if p is None:
            print("process not found: mupen64plus", file=sys.stderr)
            sys.exit(1)

        mmaps = self.grep_mmaps(p, 'libmupen64plus')
        if not mmaps:
            print("mmaps not found: libmupen64plus", file=sys.stderr)
            sys.exit(1)

        _, end = self.mmap_addr(mmaps[-1])

        # magic number 0x9037D0
        self.set_offset(end + 0x9037D0 - 0x80000000)

        self.set_target_byteorder('big')

        self.open_mem(p.pid)
