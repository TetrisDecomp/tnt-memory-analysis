class BaseProcessMemory:
    def __init__(self):
        # override in subclass
        self.offset = 0x0

    # override in subclass
    def find_process(self, name):
        return None

    # override in subclass
    def read_mem(self, addr, length):
        return None

    def process_offset(self, addr):
        return addr + self.offset

    def reverse_endianness(self, data):
        reversed_data = bytearray(data)
        reversed_data[0::4], reversed_data[1::4], reversed_data[2::4], reversed_data[3::4] = data[3::4], data[2::4], data[1::4], data[0::4]
        return reversed_data

    def dump(self, addr, length, apply_offset=True, reverse_endianness=True):
        if apply_offset:
            addr = self.process_offset(addr)

        data = self.read_mem(addr, length)

        if reverse_endianness:
            data = self.reverse_endianness(data)

        return data
