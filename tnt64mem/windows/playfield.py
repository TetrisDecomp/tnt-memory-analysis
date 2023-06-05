import tkinter as tk
import struct
import time

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 30
CELL_INFO_WIDTH = 320
CELL_INFO_HEIGHT = 240

MOBILE_PIECE_POINTER = 0x8011FB70
MOBILE_PIECE_BUFFER_SIZE = 68
BOARD_POINTERS = 0x8011FBD0
BOARD_BUFFER_SIZE = 3200
ORIENTATION_DATA_BUFFER_SIZE = 32
TRIG_ADDRESS = 0x800D0260
TRIG_BUFFER_SIZE = 32

PIECE_COLORS = ({'name': 'L', 'color': '#c148cf'},
                {'name': 'J', 'color': '#602b8f'},
                {'name': 'Z', 'color': '#c41f1f'},
                {'name': 'S', 'color': '#21bf3b'},
                {'name': 'T', 'color': '#d7de1b'},
                {'name': 'I', 'color': '#3fc1e8'},
                {'name': 'O', 'color': '#b2b6b8'},
                {'name': 'empty', 'color': '#000000'})


def parse_int_bitfield(amount, integer):
    result = []
    while amount > 0:
        result.append(integer & 1)
        integer >>= 1
        amount -= 1
    return result


class Playfield:
    def __init__(self, root, procmem, verbose=False):
        self.root = root
        self.procmem = procmem
        self.verbose = verbose

        self.root.title('Playfield')
        self.root.geometry(f'{BOARD_WIDTH * CELL_SIZE}x{BOARD_HEIGHT * CELL_SIZE}')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root_canvas = tk.Canvas(self.root)
        self.root_canvas.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))

        cell_info = tk.Toplevel()
        cell_info.title('Cell Info')
        cell_info.geometry(f'{CELL_INFO_WIDTH}x{CELL_INFO_HEIGHT}')
        cell_info.rowconfigure(0, weight=1)
        cell_info.columnconfigure(0, weight=1)
        self.cell_info_text = tk.StringVar()
        tk.Label(cell_info, textvariable=self.cell_info_text, font='courier -20', justify='left', padx=10, pady=10).grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))

        self.root_canvas.bind('<Motion>', self.update_cell_info)

        self.trig_data = struct.unpack('>8i', self.procmem.dump(TRIG_ADDRESS, TRIG_BUFFER_SIZE))
        self.game_board = [[bytes(16) for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]

        # TODO: can we use a canvas tag instead?
        self.mobile_piece_minos = [0, 0, 0, 0]
        self.mobile_outline_minos = [0, 0, 0, 0]

        # For FPS stat
        self.frame_count = 0
        self.last_time = time.time()

        self.root.after_idle(self.update)

    def update_cell_info(self, event):
        x = event.x // CELL_SIZE
        y = event.y // CELL_SIZE
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            cell = self.game_board[y][x]
            if cell[1] >= len(PIECE_COLORS):
                piece_type = PIECE_COLORS[-1]
            else:
                piece_type = PIECE_COLORS[cell[1]]
            cell_bitfield = parse_int_bitfield(3, cell[0])
            self.cell_info_text.set(
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
            self.cell_info_text.set('')

    def update(self):
        # Update every 16 ms (target 60 FPS)
        self.root.after(16, self.update)

        # For FPS stat
        current_time = time.time()
        self.frame_count += 1
        if (current_time - self.last_time) > 1:  # 1 second
            if self.verbose:
                print('FPS:', self.frame_count / (current_time - self.last_time))
            self.frame_count = 0
            self.last_time = current_time

        self._update()

    def _update(self):
        board_address = self.procmem.deref(self.procmem.deref(BOARD_POINTERS))
        mobile_piece_address = self.procmem.deref(MOBILE_PIECE_POINTER)
        mobile_piece = self.procmem.dump(mobile_piece_address, MOBILE_PIECE_BUFFER_SIZE)
        board_data = self.procmem.dump(board_address, BOARD_BUFFER_SIZE)

        try:
            if len(board_data) > 0:
                for index in range(BOARD_WIDTH * BOARD_HEIGHT):
                    start_address = index * 16
                    cell = board_data[start_address : start_address + 16]
                    x_coord = (index % 10 if cell[9] == 255 else cell[9])
                    y_coord = (index // 10 if cell[10] == 255 else cell[10])

                    if self.game_board[y_coord][x_coord] != cell:
                        fill = PIECE_COLORS[cell[1]]['color']
                        outline = '#303030'
                        # TODO: isn't this piling up rectangles?  how about we just change the cell color instead?
                        self.root_canvas.create_rectangle(x_coord * CELL_SIZE, y_coord * CELL_SIZE, x_coord * CELL_SIZE + CELL_SIZE, y_coord * CELL_SIZE + CELL_SIZE, fill=fill, outline=outline)
                        self.game_board[y_coord][x_coord] = cell

            if len(mobile_piece) > 0:
                is_mobile = mobile_piece[0]
                mobile_x_coord = mobile_piece[17]
                mobile_y_coord = mobile_piece[18]
                rendered_mobile_x_coord = mobile_piece[46]
                mobile_x_subcoord = mobile_piece[47]
                rendered_mobile_y_coord = mobile_piece[48]
                mobile_y_subcoord = mobile_piece[49]
                rotation_state = mobile_piece[10]
                if rotation_state >= 2 * len(self.trig_data):
                    sine = self.trig_data[0]
                    cosine = self.trig_data[0]
                else:
                    sine = self.trig_data[rotation_state * 2]
                    cosine = self.trig_data[rotation_state * 2 + 1]
                if self.mobile_piece_minos[0] != 0:
                    for mino in self.mobile_piece_minos:
                        self.root_canvas.delete(mino)
                    for mino in self.mobile_outline_minos:
                        self.root_canvas.delete(mino)
                mobile_piece_type = mobile_piece[19]
                if is_mobile == 1:
                    orientation_data_address = int.from_bytes(mobile_piece[36:40], byteorder='big')
                    orientation_data = self.procmem.dump(orientation_data_address, ORIENTATION_DATA_BUFFER_SIZE)

                    for index in range(4):
                        x_offset = orientation_data[index * 2 + 1] - mobile_piece[15]
                        y_offset = orientation_data[index * 2 + 2] - mobile_piece[16]
                        new_x_coord = (x_offset * cosine - y_offset * sine) + rendered_mobile_x_coord
                        new_y_coord = (x_offset * sine + y_offset * cosine) + rendered_mobile_y_coord
                        fill = PIECE_COLORS[mobile_piece[19]]['color']
                        outline = '#303030'
                        self.mobile_piece_minos[index] = self.root_canvas.create_rectangle(
                            new_x_coord * CELL_SIZE + ((mobile_x_subcoord * CELL_SIZE) >> 8),
                            new_y_coord * CELL_SIZE + ((mobile_y_subcoord * CELL_SIZE) >> 8),
                            new_x_coord * CELL_SIZE + CELL_SIZE + ((mobile_x_subcoord * CELL_SIZE) >> 8),
                            new_y_coord * CELL_SIZE + CELL_SIZE + ((mobile_y_subcoord * CELL_SIZE) >> 8),
                            fill=fill,
                            outline=outline)
                        new_x_coord = (x_offset * cosine - y_offset * sine) + mobile_x_coord
                        new_y_coord = (x_offset * sine + y_offset * cosine) + mobile_y_coord
                        fill = ''
                        outline = '#996312'
                        self.mobile_outline_minos[index] = self.root_canvas.create_rectangle(
                            new_x_coord * CELL_SIZE,
                            new_y_coord * CELL_SIZE,
                            new_x_coord * CELL_SIZE + CELL_SIZE,
                            new_y_coord * CELL_SIZE + CELL_SIZE,
                            fill=fill,
                            outline=outline)

        except Exception as error:
            print(error)
