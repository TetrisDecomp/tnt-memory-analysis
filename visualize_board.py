import tkinter as tk
import ctypes
import win32api
from win32con import PROCESS_ALL_ACCESS
from ctypes import wintypes
import more_itertools
import wmi
import struct

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

def swap32(x):                                         
    return int.from_bytes(x, byteorder='little', signed=False).to_bytes(4, byteorder='big')

def swap_bytearray(bytes):
    return b''.join(map(swap32, more_itertools.chunked(bytes, 4)))

def parse_int_bitfield(amount, integer):
    result = []
    while amount > 0:
        result.append(integer & 1)
        integer >>= 1
        amount -= 1
    return result

def process_offset(address):
     return address - 0x80000000 + 0xDFE40000

def deref(address):
    buffer = ctypes.create_string_buffer(4) 
    rPM(process.handle,process_offset(address),buffer,4,ctypes.byref(bytes_read))
    cell_bytes = bytes(buffer)
    chunked = more_itertools.chunked(cell_bytes, 4)
    chunked_list = list(chunked)
    chunked_list[0].reverse()
    return int.from_bytes(bytes(chunked_list[0]), 'big')

win_mi = wmi.WMI()
processes = [process for process in win_mi.Win32_Process()]
pid = int(list(filter(lambda process : "Project64" in process.name, processes))[0].Handle)

process = win32api.OpenProcess(PROCESS_ALL_ACCESS,0,pid)

rPM = ctypes.WinDLL('kernel32',use_last_error=True).ReadProcessMemory
rPM.argtypes = [wintypes.HANDLE,ctypes.wintypes.LPCVOID,wintypes.LPVOID,ctypes.c_size_t,ctypes.POINTER(ctypes.c_size_t)]
rPM.restype = wintypes.BOOL
bytes_read = ctypes.c_size_t()

mobile_piece_address = deref(MOBILE_PIECE_POINTER)
offset_mobile_piece_address = process_offset(mobile_piece_address)
mobile_piece_buffer = ctypes.create_string_buffer(MOBILE_PIECE_BUFFER_SIZE) 

board_address = deref(deref(BOARD_POINTERS))
offset_board_address = process_offset(board_address)
board_buffer = ctypes.create_string_buffer(BOARD_BUFFER_SIZE)

trig_address = TRIG_ADDRESS
offset_trig_address = process_offset(trig_address)
trig_buffer = ctypes.create_string_buffer(TRIG_BUFFER_SIZE)

rPM(process.handle,offset_trig_address,trig_buffer,TRIG_BUFFER_SIZE,ctypes.byref(bytes_read))

trig_data = struct.unpack('<8i', trig_buffer)

game_board = [[[] for x in range(BOARD_WIDTH)] for y in range(BOARD_HEIGHT)]
mobile_piece = b''
mobile_x_coord = 0
x_offset = 0
rendered_mobile_y_coord = 0
y_offset = 0
mobile_piece_type = 7
mobile_piece_minos = [0, 0, 0, 0]
mobile_outline_minos = [0, 0, 0, 0]

piece_colors = [{"name": 'L', "color": '#c148cf'},
                {"name": 'J', "color": '#602b8f'}, 
                {"name": 'Z', "color": '#c41f1f'}, 
                {"name": 'S', "color": '#21bf3b'}, 
                {"name": 'T', "color": '#d7de1b'}, 
                {"name": 'I', "color": '#3fc1e8'}, 
                {"name": 'O', "color": '#b2b6b8'}, 
                {"name": 'empty', 'color': '#000000'}] 

board_window = tk.Tk()
board_window.title("board")
dimensions = (BOARD_WIDTH*PIXEL_SIZE, BOARD_HEIGHT*PIXEL_SIZE)
canvas = tk.Canvas(board_window, width=dimensions[0], height=dimensions[1]+TEXT_HEIGHT)

stats_window = tk.Tk()
stats_window.title("stats")
stats_canvas = tk.Canvas(stats_window, width=STATS_WIDTH, height=STATS_HEIGHT)
coordinates = stats_canvas.create_text(STATS_WIDTH/2, STATS_HEIGHT/2, text='', fill="black", font='24')

def get_mouse_position(e):
    x= e.x//PIXEL_SIZE
    y= e.y//PIXEL_SIZE
    if 0<=x<BOARD_WIDTH and 0<=y<BOARD_HEIGHT:
        cell = game_board[y][x]
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

for index in range(BOARD_WIDTH*BOARD_HEIGHT):
    x_coord = index % 10
    y_coord = index // 10
    canvas.create_rectangle(x_coord*PIXEL_SIZE, y_coord*PIXEL_SIZE, x_coord*PIXEL_SIZE+PIXEL_SIZE, y_coord*PIXEL_SIZE+PIXEL_SIZE, fill="black")

while True:
    board_window.update()
    board_window.update_idletasks()
    board_address = deref(deref(BOARD_POINTERS))
    offset_board_address = process_offset(board_address)
    rPM(process.handle,offset_board_address,board_buffer,BOARD_BUFFER_SIZE,ctypes.byref(bytes_read))
    mobile_piece_address = deref(MOBILE_PIECE_POINTER)
    offset_mobile_piece_address = process_offset(mobile_piece_address)
    rPM(process.handle,offset_mobile_piece_address,mobile_piece_buffer,MOBILE_PIECE_BUFFER_SIZE,ctypes.byref(bytes_read))

    try:
        mobile_piece = swap_bytearray(bytes(mobile_piece_buffer))
        board_data = swap_bytearray(bytes(board_buffer))
        if len(board_data) > 0:
            for index in range(BOARD_WIDTH*BOARD_HEIGHT):
                start_address = index*16
                cell = board_data[start_address:start_address+16]
                x_coord = (index%10 if cell[9] == 255 else cell[9])
                y_coord = (index//10 if cell[10] == 255 else cell[10])

                if game_board[y_coord][x_coord] != cell:
                    fill = piece_colors[cell[1]]["color"]
                    outline = '#404040'
                    canvas.create_rectangle(x_coord*PIXEL_SIZE, y_coord*PIXEL_SIZE, x_coord*PIXEL_SIZE+PIXEL_SIZE, y_coord*PIXEL_SIZE+PIXEL_SIZE, fill=fill, outline=outline)
                    game_board[y_coord][x_coord] = cell

        if len(mobile_piece) > 0:
            orientation_data_address = int.from_bytes(mobile_piece[36:40])
            offset_orientation_data_address = process_offset(orientation_data_address)
            orientation_data_buffer = ctypes.create_string_buffer(ORIENTATION_DATA_BUFFER_SIZE) 
            rPM(process.handle,offset_orientation_data_address,orientation_data_buffer,ORIENTATION_DATA_BUFFER_SIZE,ctypes.byref(bytes_read))
            orientation_data = swap_bytearray(bytes(orientation_data_buffer))

            
            mobile_x_coord = mobile_piece[17]
            mobile_y_coord = mobile_piece[18]
            rendered_mobile_y_coord = mobile_piece[48]
            mobile_y_subcoord = mobile_piece[49]
            rotation_state = mobile_piece[10] 
            sine = trig_data[rotation_state*2]
            cosine = trig_data[rotation_state*2+1]
            if mobile_piece_minos[0] != 0:
                for mino in mobile_piece_minos:
                    canvas.delete(mino)
                for mino in mobile_outline_minos:
                    canvas.delete(mino)
            mobile_piece_type = mobile_piece[19]
            for index in range(4):
                x_offset = orientation_data[index*2+1] - mobile_piece[15]
                y_offset = orientation_data[index*2+2] - mobile_piece[16]
                new_x_coord = (x_offset*cosine-y_offset*sine)+mobile_x_coord
                new_y_coord = (x_offset*sine+y_offset*cosine)+rendered_mobile_y_coord
                fill = piece_colors[mobile_piece[19]]["color"]
                outline = '#404040'
                mobile_piece_minos[index] = canvas.create_rectangle((new_x_coord)*PIXEL_SIZE,
                                        (new_y_coord)*PIXEL_SIZE + (mobile_y_subcoord / 255) // (1/PIXEL_SIZE),
                                        (new_x_coord)*PIXEL_SIZE+PIXEL_SIZE,
                                        (new_y_coord)*PIXEL_SIZE+PIXEL_SIZE + (mobile_y_subcoord / 255) // (1/PIXEL_SIZE), 
                                        fill=fill,
                                        outline=outline)
                new_y_coord = (x_offset*sine+y_offset*cosine)+mobile_y_coord
                fill = ''
                outline = 'orange'
                mobile_outline_minos[index] = canvas.create_rectangle((new_x_coord)*PIXEL_SIZE,
                                        (new_y_coord)*PIXEL_SIZE,
                                        (new_x_coord)*PIXEL_SIZE+PIXEL_SIZE,
                                        (new_y_coord)*PIXEL_SIZE+PIXEL_SIZE,
                                        fill=fill,
                                        outline=outline)

    except Exception as error:
        print(error)
