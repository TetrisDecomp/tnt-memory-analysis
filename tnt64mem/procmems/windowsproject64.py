import sys

from .windows import WindowsProcessMemory

class WindowsProject64Memory(WindowsProcessMemory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        p = self.find_process('Project64')
        if p is None:
            print("process not found: Project64", file=sys.stderr)
            sys.exit(1)

        # magic number 0xDFE40000
        self.set_offset(0xDFE40000 - 0x80000000)

        self.open_process(p.pid)
