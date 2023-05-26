#!/usr/bin/env python3

import sys
import platform
import argparse
import time

def auto_int(x):
    return int(x, 0)

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase verbosity')
    parser.add_argument('ADDR', type=auto_int, help='addr')
    parser.add_argument('LENGTH', type=auto_int , help='length')

    args = parser.parse_args()


    system = platform.system()
    if system == 'Linux':
        if args.verbose:
            print(f"detected system: {system}", file=sys.stderr)
        from mems.linuxmupen import LinuxMupenMemory
        mem = LinuxMupenMemory(verbose=args.verbose)
    elif system == 'Windows':
        if args.verbose:
            print(f"detected system: {system}", file=sys.stderr)
        from mems.windowsproject64 import WindowsProject64Memory
        mem = WindowsProject64Memory(verbose=args.verbose)
    elif system == 'Darwin':
        print(f"unsupported system: {system}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"unrecognized system: {system}", file=sys.stderr)
        sys.exit(1)


    start_time = time.time()
    how_often = 1 # secs
    counter = 0
    while True:
        counter += 1
        if (time.time() - start_time) > how_often:
            print("FPS: ", int(counter / (time.time() - start_time)))
            counter = 0
            start_time = time.time()

        data = mem.dump(args.ADDR, args.LENGTH)

if __name__ == "__main__":
    main()
