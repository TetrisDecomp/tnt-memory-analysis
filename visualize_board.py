#!/usr/bin/env python3

import sys
import platform
import argparse
import struct
import time

import tkinter as tk

def parse_int_bitfield(amount, integer):
    result = []
    while amount > 0:
        result.append(integer & 1)
        integer >>= 1
        amount -= 1
    return result

def mainloop(mem, verbose=False):
    MOBILE_PIECE_POINTER = 0x8011FB70
    MOBILE_PIECE_BUFFER_SIZE = 68
    BOARD_POINTERS = 0x8011FBD0
    BOARD_BUFFER_SIZE = 3200
    ORIENTATION_DATA_BUFFER_SIZE = 32
    TRIG_ADDRESS = 0x800D0260
    TRIG_BUFFER_SIZE = 32

    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    PIXEL_SIZE = 30
    STATS_WIDTH = 256
    STATS_HEIGHT = 256
    TEXT_HEIGHT = 25

    piece_colors = [{"name": 'L', "color": '#c148cf'},
                    {"name": 'J', "color": '#602b8f'}, 
                    {"name": 'Z', "color": '#c41f1f'}, 
                    {"name": 'S', "color": '#21bf3b'}, 
                    {"name": 'T', "color": '#d7de1b'}, 
                    {"name": 'I', "color": '#3fc1e8'}, 
                    {"name": 'O', "color": '#b2b6b8'}, 
                    {"name": 'empty', 'color': '#000000'}] 

    trig_data = struct.unpack('>8i', mem.dump(TRIG_ADDRESS, TRIG_BUFFER_SIZE))

    game_board = [[bytes(16) for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
    mobile_piece = b''
    mobile_x_coord = 0
    x_offset = 0
    rendered_mobile_y_coord = 0
    y_offset = 0
    mobile_piece_type = 7
    mobile_piece_minos = [0, 0, 0, 0]
    mobile_outline_minos = [0, 0, 0, 0]

    board_window = tk.Tk()
    board_window.title("board")
    dimensions = (BOARD_WIDTH * PIXEL_SIZE, BOARD_HEIGHT * PIXEL_SIZE)
    canvas = tk.Canvas(board_window, width=dimensions[0], height=dimensions[1] + TEXT_HEIGHT)

    stats_window = tk.Tk()
    stats_window.title("stats")
    stats_canvas = tk.Canvas(stats_window, width=STATS_WIDTH, height=STATS_HEIGHT)
    coordinates = stats_canvas.create_text(STATS_WIDTH / 2, STATS_HEIGHT / 2, text='', fill="black", font='24')

    def get_mouse_position(e):
        x = e.x // PIXEL_SIZE
        y = e.y // PIXEL_SIZE
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            cell = game_board[y][x]
            if cell[1] >= len(piece_colors):
                piece_type = piece_colors[-1]
            else:
                piece_type = piece_colors[cell[1]]
            cell_bitfield = parse_int_bitfield(3, cell[0])
            stats_canvas.itemconfigure(coordinates, text=
                                       f'broken: {cell_bitfield[0]}' +
                                       f'\nempty: {cell_bitfield[1]}' +
                                       f'\nadjacent: {cell_bitfield[2]}' +
                                       f'\npiece type: {piece_type["name"]}' +
                                       f'\n02: {cell[2]}' +
                                       f'\nsquare number: {cell[3]}' +
                                       f'\nconnected cell: {cell[4:8].hex()}' +
                                       f'\nmemory id: {cell[8]}' +
                                       f'\ncoordinates: {cell[9]}, {cell[10]}' +
                                       f'\ngraphics ref: {cell[12:16].hex()}')
        else:
            stats_canvas.itemconfigure(coordinates, text='')

    stats_canvas.pack(expand="yes", fill="both")

    canvas.bind('<Motion>', get_mouse_position)
    canvas.pack(expand="yes", fill="both")
    canvas.configure(bg="white")

    board_window.geometry(f'{dimensions[0]}x{dimensions[1]}')

    target_fps = 60
    last_frame_time = time.time()
    if verbose:
        frame_counter = 0
        counter_time = last_frame_time
        how_often = 1 # secs
    while True:
        sleep_time = 1/target_fps - (time.time() - last_frame_time)
        if sleep_time > 0:
            time.sleep(sleep_time)
        last_frame_time = time.time()

        if verbose:
            frame_counter += 1
            if (last_frame_time - counter_time) > how_often:
                print("FPS: ", int(frame_counter / (last_frame_time - counter_time)))
                frame_counter = 0
                counter_time = last_frame_time

        board_window.update()
        board_window.update_idletasks()
        board_address = mem.deref(mem.deref(BOARD_POINTERS))
        mobile_piece_address = mem.deref(MOBILE_PIECE_POINTER)
        mobile_piece = mem.dump(mobile_piece_address, MOBILE_PIECE_BUFFER_SIZE)
        board_data = mem.dump(board_address, BOARD_BUFFER_SIZE)

        try:
            if len(board_data) > 0:
                for index in range(BOARD_WIDTH * BOARD_HEIGHT):
                    start_address = index * 16
                    cell = board_data[start_address : start_address+16]
                    x_coord = (index % 10 if cell[9] == 255 else cell[9])
                    y_coord = (index // 10 if cell[10] == 255 else cell[10])

                    if game_board[y_coord][x_coord] != cell:
                        fill = piece_colors[cell[1]]["color"]
                        outline = '#303030'
                        canvas.create_rectangle(x_coord * PIXEL_SIZE, y_coord * PIXEL_SIZE, x_coord * PIXEL_SIZE + PIXEL_SIZE, y_coord * PIXEL_SIZE + PIXEL_SIZE, fill=fill, outline=outline)
                        game_board[y_coord][x_coord] = cell

            if len(mobile_piece) > 0:
                is_mobile = mobile_piece[0]
                mobile_x_coord = mobile_piece[17]
                mobile_y_coord = mobile_piece[18]
                rendered_mobile_x_coord = mobile_piece[46]
                mobile_x_subcoord = mobile_piece[47]
                rendered_mobile_y_coord = mobile_piece[48]
                mobile_y_subcoord = mobile_piece[49]
                rotation_state = mobile_piece[10]
                if rotation_state >= 2 * len(trig_data):
                    sine = trig_data[0]
                    cosine = trig_data[0]
                else:
                    sine = trig_data[rotation_state * 2]
                    cosine = trig_data[rotation_state * 2 + 1]
                if mobile_piece_minos[0] != 0:
                    for mino in mobile_piece_minos:
                        canvas.delete(mino)
                    for mino in mobile_outline_minos:
                        canvas.delete(mino)
                mobile_piece_type = mobile_piece[19]
                if is_mobile == 1:
                    orientation_data_address = int.from_bytes(mobile_piece[36:40], byteorder='big')  # must specify byteorder for python versions < 3.11

                    # TODO: move this outside the loop, since it is static
                    orientation_data = mem.dump(orientation_data_address, ORIENTATION_DATA_BUFFER_SIZE)

                    for index in range(4):
                        x_offset = orientation_data[index * 2 + 1] - mobile_piece[15]
                        y_offset = orientation_data[index * 2 + 2] - mobile_piece[16]
                        new_x_coord = (x_offset * cosine - y_offset * sine) + rendered_mobile_x_coord
                        new_y_coord = (x_offset * sine + y_offset * cosine) + rendered_mobile_y_coord
                        fill = piece_colors[mobile_piece[19]]["color"]
                        outline = '#303030'
                        mobile_piece_minos[index] = canvas.create_rectangle((new_x_coord) * PIXEL_SIZE + (mobile_x_subcoord / 255) // (1 / PIXEL_SIZE),
                                                                            (new_y_coord) * PIXEL_SIZE + (mobile_y_subcoord / 255) // (1 / PIXEL_SIZE),
                                                                            (new_x_coord) * PIXEL_SIZE + PIXEL_SIZE + (mobile_x_subcoord / 255) // (1 / PIXEL_SIZE),
                                                                            (new_y_coord) * PIXEL_SIZE + PIXEL_SIZE + (mobile_y_subcoord / 255) // (1 / PIXEL_SIZE),
                                                                            fill=fill,
                                                                            outline=outline)
                        new_x_coord = (x_offset * cosine - y_offset * sine) + mobile_x_coord
                        new_y_coord = (x_offset * sine + y_offset * cosine) + mobile_y_coord
                        fill = ''
                        outline = '#996312'
                        mobile_outline_minos[index] = canvas.create_rectangle((new_x_coord) * PIXEL_SIZE,
                                                                              (new_y_coord) * PIXEL_SIZE,
                                                                              (new_x_coord) * PIXEL_SIZE + PIXEL_SIZE,
                                                                              (new_y_coord) * PIXEL_SIZE + PIXEL_SIZE,
                                                                              fill=fill,
                                                                              outline=outline)

        except Exception as error:
            print(error)

def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase verbosity')
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

    mainloop(mem, args.verbose)

if __name__ == "__main__":
    main()
