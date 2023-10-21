import sys
import ctypes
from ctypes import wintypes

import win32api
import win32con

from .base import BaseProcessMemory

class WindowsProcessMemory(BaseProcessMemory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process = None
        self.read_process_memory = ctypes.WinDLL('kernel32', use_last_error=True).ReadProcessMemory
        self.read_process_memory.argtypes = [wintypes.HANDLE, wintypes.LPCVOID, wintypes.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
        self.read_process_memory.restype = wintypes.BOOL
        self.bytes_read = ctypes.c_size_t()

    def open_process(self, pid):
        self.process = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)

    def read_mem(self, addr, length):
        buffer = ctypes.create_string_buffer(length)
        self.read_process_memory(self.process.handle, addr, buffer, length, ctypes.byref(self.bytes_read))
        return bytes(buffer)
