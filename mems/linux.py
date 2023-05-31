import sys

from .base import BaseProcessMemory

class LinuxProcessMemory(BaseProcessMemory):
    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose
        self.mem_file = None

    def open_mem(self, pid):
        self.mem_file = open(f"/proc/{pid}/mem", 'rb', 0)

    def grep_mmaps(self, p, string):
        mmaps = []
        for m in p.memory_maps(False):
            if string in m.path:
                if self.verbose:
                    print(f"mmap found: {m.addr}\t{m.path}", file=sys.stderr)
                mmaps.append(m)
        return mmaps

    def mmap_addr(self, m):
        addrs = m.addr.split('-')
        start = int(addrs[0], 16)        
        end = int(addrs[1], 16)        
        return start, end

    def read_mem(self, addr, length):
        self.mem_file.seek(addr)
        try :
            data = self.mem_file.read(length)
        except OSError as error:
            data = bytes()
        return data
