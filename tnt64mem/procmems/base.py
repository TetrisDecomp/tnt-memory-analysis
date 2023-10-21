import sys

import psutil

class BaseProcessMemory:
    def __init__(self):
        self.offset = 0x0
        self.target_byteorder = 'big'  # or 'little'

    def find_process(self, name):
        for p in psutil.process_iter():
            if name in p.name():
                print(f"process found: {p.pid}\t{p.name()}", file=sys.stderr)
                return p
        return None

    def set_offset(self, offset):
        if offset != offset & ~3:
            print(f"offset should be a multiple of 4: {offset}", file=sys.stderr)
            sys.exit(1)
        self.offset = offset

    def set_target_byteorder(self, byteorder):
        if byteorder not in ('little', 'big'):
            print(f"byteorder should be either 'little' or 'big': {byteorder}", file=sys.stderr)
            sys.exit(1)
        self.target_byteorder = byteorder

    def reverse_endianness(self, data):
        reversed_data = bytearray(data)
        reversed_data[0::4], reversed_data[1::4], reversed_data[2::4], reversed_data[3::4] = data[3::4], data[2::4], data[1::4], data[0::4]
        return bytes(reversed_data)

    def dump(self, addr, length):
        addr += self.offset

        start_addr = addr & ~3
        end_addr = addr + length + 3 & ~3
        data = self.read_mem(start_addr, end_addr - start_addr)

        if sys.byteorder != self.target_byteorder:
            data = self.reverse_endianness(data)

        return data[(addr & 3) : (addr & 3) + length]

    def deref(self, addr, size=4):
        data = self.read_mem(addr + self.offset, size)
        return int.from_bytes(data, byteorder=sys.byteorder)

    # override this method in derived class
    def read_mem(self, addr, length):
        return None
