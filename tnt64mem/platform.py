import sys
import platform

def auto_int(x):
    return int(x, 0)

def add_args(parser):
    parser.add_argument('EMU', choices=['mupen', 'project64'], help='emulator')
    group_mupen = parser.add_argument_group('mupen', 'When running mupen on the command line, you should see it print out "&ConfigOpenSection is {ADDRESS}".')
    group_mupen.add_argument('--cos', metavar='ADDRESS', type=auto_int, help='&ConfigOpenSection address')

def get_procmem(args):
    system = platform.system()

    if system == 'Linux':
        print(f'detected system: {system}', file=sys.stderr)

        if args.EMU == 'mupen':
            if args.cos is not None:
                from .procmems.linuxmupen import LinuxMupenMemory
                procmem = LinuxMupenMemory(args.cos)
            else:
                print(f'must specify --cos option for {args.EMU}', file=sys.stderr)
                sys.exit(1)
        else:
            print(f'procmem unimplemented for {args.EMU} on {system}', file=sys.stderr)
            sys.exit(1)

    elif system == 'Windows':
        print(f'detected system: {system}', file=sys.stderr)

        if args.EMU == 'project64':
            from .procmems.windowsproject64 import WindowsProject64Memory
            procmem = WindowsProject64Memory()
        else:
            print(f'procmem unimplemented for {args.EMU} on {system}', file=sys.stderr)
            sys.exit(1)

    elif system == 'Darwin':
        print(f'unsupported system: {system}', file=sys.stderr)
        sys.exit(1)

    else:
        print(f'unrecognized system: {system}', file=sys.stderr)
        sys.exit(1)

    return procmem
