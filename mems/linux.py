import sys

import psutil

from .base import BaseProcessMemory

class LinuxProcessMemory(BaseProcessMemory):
    def __init__(self, verbose=False):
        super().__init__()
        self.verbose = verbose
        self.mem_file = None

    def open_mem(self, pid):
        self.mem_file = open(f"/proc/{pid}/mem", 'rb', 0)

    def read_mem(self, addr, length):
        self.mem_file.seek(addr)
        try :
            data = self.mem_file.read(length)
        except OSError as error:
            data = bytes()
        return data

    def find_process(self, name):
        for p in psutil.process_iter():
            if name in p.name():
                if self.verbose:
                    print(f"process found: {p.pid}\t{p.name()}", file=sys.stderr)
                return p
        return None

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
