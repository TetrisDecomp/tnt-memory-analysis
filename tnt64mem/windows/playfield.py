import tkinter as tk
import struct
import time

BOARD_WIDTH = 10
BOARD_HEIGHT = 20
ABOVE_BOARD_HEIGHT = 3
CELL_SIZE = 24

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
    def __init__(self, root, procmem):
        self.root = root
        self.procmem = procmem

        self.root.title('Playfield')
        self.root.geometry(f'{BOARD_WIDTH * CELL_SIZE}x{(BOARD_HEIGHT + ABOVE_BOARD_HEIGHT) * CELL_SIZE}')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root_canvas = tk.Canvas(self.root)
        self.root_canvas.grid(column=0, row=0, sticky='wnes')

        cell_info = tk.Toplevel()
        cell_info.title('Cell Info')
        cell_info.rowconfigure(0, weight=1)
        cell_info.columnconfigure(0, weight=1)
        self.t = tk.Text(cell_info, width=24, height=10, wrap="none", padx=10, pady=10)
        self.t.grid(column=0, row=0, sticky='wnes')
        self.t['state'] = 'disabled'

        self.root_canvas.bind('<Motion>', self.update_cell_info)

        self.trig_data = struct.unpack('>8i', self.procmem.dump(TRIG_ADDRESS, TRIG_BUFFER_SIZE))
        self.game_board = [[bytes(16) for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]

        self.root.after_idle(self.update)

    def update_cell_info(self, event):
        canvas_x, canvas_y = int(self.root_canvas.canvasx(event.x)), int(self.root_canvas.canvasy(event.y))

        x = canvas_x // CELL_SIZE
        y = (canvas_y // CELL_SIZE) - ABOVE_BOARD_HEIGHT
        if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
            cell = self.game_board[y][x]
            if cell[1] >= len(PIECE_COLORS):
                piece_type = PIECE_COLORS[-1]
            else:
                piece_type = PIECE_COLORS[cell[1]]
            cell_bitfield = parse_int_bitfield(3, cell[0])

            lines = []
            lines.append(f'broken: {cell_bitfield[0]}')
            lines.append(f'empty: {cell_bitfield[1]}')
            lines.append(f'adjacent: {cell_bitfield[2]}')
            lines.append(f'piece type: {piece_type["name"]}')
            lines.append(f'02: {cell[2]}')
            lines.append(f'square number: {cell[3]}')
            lines.append(f'connected cell: {cell[4:8].hex()}')
            lines.append(f'memory id: {cell[8]}')
            lines.append(f'coordinates: {cell[9]}, {cell[10]}')
            lines.append(f'graphics ref: {cell[12:16].hex()}')

            save_state = self.t['state']
            self.t['state'] = 'normal'
            self.t.replace('1.0', 'end', '\n'.join(lines))
            self.t['state'] = save_state

    def update(self):
        # Update every 16 ms (target 60 FPS)
        self.root.after(16, self.update)

        self._update()

    def _update(self):
        board_address = self.procmem.deref(self.procmem.deref(BOARD_POINTERS))
        mobile_piece_address = self.procmem.deref(MOBILE_PIECE_POINTER)
        mobile_piece = self.procmem.dump(mobile_piece_address, MOBILE_PIECE_BUFFER_SIZE)
        board_data = self.procmem.dump(board_address, BOARD_BUFFER_SIZE)

        if len(board_data) > 0:
            for index in range(BOARD_WIDTH * BOARD_HEIGHT):
                start_address = index * 16
                cell = board_data[start_address : start_address + 16]
                x_coord = (index % 10 if cell[9] == 255 else cell[9])
                y_coord = (index // 10 if cell[10] == 255 else cell[10])

                if self.game_board[y_coord][x_coord] != cell:
                    fill = PIECE_COLORS[cell[1]]['color']
                    outline = '#303030'
                    self.root_canvas.delete(f'cell{cell[8]}')
                    self.root_canvas.create_rectangle(x_coord * CELL_SIZE, (y_coord + ABOVE_BOARD_HEIGHT) * CELL_SIZE, x_coord * CELL_SIZE + CELL_SIZE, (y_coord + ABOVE_BOARD_HEIGHT) * CELL_SIZE + CELL_SIZE, fill=fill, outline=outline, tags=f'cell{cell[8]}')
                    self.game_board[y_coord][x_coord] = cell

        if len(mobile_piece) > 0:
            is_mobile = mobile_piece[0]
            mobile_x_coord = mobile_piece[17]
            mobile_y_coord = int.from_bytes(mobile_piece[18:19], byteorder='big', signed=True)
            rendered_mobile_x_coord = mobile_piece[46]
            rendered_mobile_x_subcoord = mobile_piece[47]
            rendered_mobile_y_coord = int.from_bytes(mobile_piece[48:49], byteorder='big', signed=True)
            rendered_mobile_y_subcoord = mobile_piece[49]
            rotation_state = mobile_piece[10]
            if rotation_state >= 2 * len(self.trig_data):
                sine = self.trig_data[0]
                cosine = self.trig_data[0]
            else:
                sine = self.trig_data[rotation_state * 2]
                cosine = self.trig_data[rotation_state * 2 + 1]
            self.root_canvas.delete('mobile')
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
                    self.root_canvas.create_rectangle(
                        new_x_coord * CELL_SIZE + ((rendered_mobile_x_subcoord * CELL_SIZE) >> 8),
                        (new_y_coord + ABOVE_BOARD_HEIGHT) * CELL_SIZE + ((rendered_mobile_y_subcoord * CELL_SIZE) >> 8),
                        new_x_coord * CELL_SIZE + CELL_SIZE + ((rendered_mobile_x_subcoord * CELL_SIZE) >> 8),
                        (new_y_coord + ABOVE_BOARD_HEIGHT) * CELL_SIZE + CELL_SIZE + ((rendered_mobile_y_subcoord * CELL_SIZE) >> 8),
                        fill=fill,
                        outline=outline,
                        tags='mobile')
                    new_x_coord = (x_offset * cosine - y_offset * sine) + mobile_x_coord
                    new_y_coord = (x_offset * sine + y_offset * cosine) + mobile_y_coord
                    fill = ''
                    outline = '#996312'
                    self.root_canvas.create_rectangle(
                        new_x_coord * CELL_SIZE,
                        (new_y_coord + ABOVE_BOARD_HEIGHT) * CELL_SIZE,
                        new_x_coord * CELL_SIZE + CELL_SIZE,
                        (new_y_coord + ABOVE_BOARD_HEIGHT) * CELL_SIZE + CELL_SIZE,
                        fill=fill,
                        outline=outline,
                        tags='mobile')
