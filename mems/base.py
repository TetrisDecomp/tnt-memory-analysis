import sys
import struct

class BaseProcessMemory:
    def __init__(self):
        # override these variables in derived class
        self.offset = 0x0
        self.target_byteorder = 'little'  # or 'big'

    # override this method in derived class
    def find_process(self, name):
        return None

    # override this method in derived class
    def read_mem(self, addr, length):
        return None

    def reverse_endianness(self, data):
        reversed_data = bytearray(data)
        reversed_data[0::4], reversed_data[1::4], reversed_data[2::4], reversed_data[3::4] = data[3::4], data[2::4], data[1::4], data[0::4]
        return bytes(reversed_data)

    def dump(self, addr, length):
        data = self.read_mem(addr + self.offset, length)
        if sys.byteorder != self.target_byteorder:
            data = self.reverse_endianness(data)
        return data

    def deref(self, addr):
        data = self.read_mem(addr + self.offset, 4)
        return int.from_bytes(data, byteorder=sys.byteorder)
