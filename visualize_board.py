#!/usr/bin/env python3

import argparse

import tkinter as tk

from tnt64mem.platform import add_args, get_procmem
from tnt64mem.windows.playfield import Playfield

def main():
    parser = argparse.ArgumentParser(description='')
    add_args(parser)
    args = parser.parse_args()

    procmem = get_procmem(args)

    root = tk.Tk()
    Playfield(root, procmem)
    root.mainloop()

if __name__ == '__main__':
    main()
