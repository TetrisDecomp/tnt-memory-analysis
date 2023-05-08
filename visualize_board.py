import tkinter as tk


board_width = 10
board_height = 20
pixel_size = 30
text_height = 25
dimensions = (board_width*pixel_size, board_height*pixel_size)

stats_width = 256
stats_height = 256

game_board = [[[] for x in range(board_width)] for y in range(board_height)]

data_path = "./bin/dump.data"
piece_colors = ["pink", "purple", "red", "green", "yellow", "cyan", "gray", "black"]
board_window = tk.Tk()
board_window.title("board")
canvas = tk.Canvas(board_window, width=dimensions[0], height=dimensions[1]+text_height)

stats_window = tk.Tk()
stats_window.title("stats")
stats_canvas = tk.Canvas(stats_window, width=stats_width, height=stats_height)
coordinates = stats_canvas.create_text(stats_width/2, stats_height/2, text='', fill="black", font='24')

def get_mouse_position(e):
    x= e.x//pixel_size
    y= e.y//pixel_size
    if 0<=x<board_width and 0<=y<board_height:
        cell = game_board[y][x]
        stats_canvas.itemconfigure(coordinates, text=
                                   f'00: {cell[0]}' +
                                   f'\npiece type: {piece_colors[cell[1]]}' +
                                   f'\n02: {cell[2]}' +
                                   f'\nsquare number: {cell[3]}' +
                                   f'\nconnected cell: {cell[4:7].hex()}' +
                                   f'\nmemory id: {cell[8]}' +
                                   f'\ncoordinates: {cell[9]}, {cell[10]}' +
                                   f'\n11: {cell[11]}' +
                                   f'\ngraphics ref: {cell[12:15].hex()}')
    else:
        stats_canvas.itemconfigure(coordinates, text='')

stats_canvas.pack(expand="yes", fill="both")

canvas.bind('<Motion>', get_mouse_position)

canvas.pack(expand="yes", fill="both")
canvas.configure(bg="white")


board_window.geometry(f'{dimensions[0]}x{dimensions[1]}')

for index in range(board_width*board_height):
    x_coord = index % 10
    y_coord = index // 10
    fill = "black"
    canvas.create_rectangle(x_coord*pixel_size, y_coord*pixel_size, x_coord*pixel_size+pixel_size, y_coord*pixel_size+pixel_size, fill=fill, outline="white")

while True:
    board_window.update()
    board_window.update_idletasks()
    with open(data_path, mode="rb") as file:
        try:
            data = file.read()
            if len(data) > 0:
                for index in range(board_width*board_height):
                    start_address = index*16
                    cell = data[start_address:start_address+16]
                    x_coord = (index%10 if cell[9] == 255 else cell[9])
                    y_coord = (index//10 if cell[10] == 255 else cell[10])

                    if game_board[y_coord][x_coord] != cell:
                        fill = piece_colors[cell[1]]
                        canvas.create_rectangle(x_coord*pixel_size, y_coord*pixel_size, x_coord*pixel_size+pixel_size, y_coord*pixel_size+pixel_size, fill=fill, outline="white")
                        game_board[y_coord][x_coord] = cell

        except Exception as error:
            print(error)