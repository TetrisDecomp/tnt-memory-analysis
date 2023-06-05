#!/usr/bin/env python3

import sys
import platform
import argparse

import tkinter as tk

from tnt64mem.windows.playfield import Playfield


def auto_int(x):
    return int(x, 0)


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase verbosity')
    parser.add_argument('--emu', choices=['project64', 'mupen'], default='project64', help='(default: %(default)s)')
    group_mupen = parser.add_argument_group('mupen', 'When running mupen on the command line, you should see it print out "&ConfigOpenSection is {ADDRESS}".')
    group_mupen.add_argument('--cos', metavar='ADDRESS', type=auto_int, help='&ConfigOpenSection address')
    args = parser.parse_args()

    system = platform.system()
    if system == 'Windows':
        if args.verbose:
            print(f'detected system: {system}', file=sys.stderr)
        if args.emu == 'project64':
            from tnt64mem.procmems.windowsproject64 import WindowsProject64Memory
            procmem = WindowsProject64Memory(verbose=args.verbose)
        else:
            print(f'unimplemented', file=sys.stderr)
            sys.exit(1)
    elif system == 'Linux':
        if args.verbose:
            print(f'detected system: {system}', file=sys.stderr)
        if args.emu == 'mupen':
            if args.cos is not None:
                from tnt64mem.procmems.linuxmupen import LinuxMupenMemory
                procmem = LinuxMupenMemory(args.cos, verbose=args.verbose)
            else:
                print(f'must specify --cos option', file=sys.stderr)
                sys.exit(1)
        else:
            print(f'unimplemented', file=sys.stderr)
            sys.exit(1)
    elif system == 'Darwin':
        print(f'unsupported system: {system}', file=sys.stderr)
        sys.exit(1)
    else:
        print(f'unrecognized system: {system}', file=sys.stderr)
        sys.exit(1)

    root = tk.Tk()
    Playfield(root, procmem, verbose=args.verbose)
    root.mainloop()


if __name__ == '__main__':
    main()
