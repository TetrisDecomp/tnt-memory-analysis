import sys

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
