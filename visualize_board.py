import math
import tkinter as tk

board_width = 10
board_height = 20
pixel_size = 30
dimensions = (board_width*pixel_size, board_height*pixel_size)
data_path = "./bin/dump.data"
piece_colors = ["pink", "purple", "red", "green", "yellow", "cyan", "gray", "black"]
window = tk.Tk()
canvas = tk.Canvas(window, width=dimensions[0], height=dimensions[1])
canvas.pack(expand="yes", fill="both")
canvas.configure(bg="white")

game_board = [[7 for x in range(board_width)] for y in range(board_height)]

for index in range(board_width*board_height):
    x_coord = index % 10
    y_coord = math.floor(index/10)
    fill = "black"
    canvas.create_rectangle(x_coord*pixel_size, y_coord*pixel_size, x_coord*pixel_size+pixel_size, y_coord*pixel_size+pixel_size, fill=fill)

while True:
    window.update()
    window.update_idletasks()
    with open(data_path, mode="rb") as file:
        try:
            data = file.read()
            if len(data) > 0:
                for index in range(board_width*board_height):
                    start_address = index*16
                    cell = data[start_address:start_address+16]
                    x_coord = (index % 10 if cell[9] == 255 else cell[9])
                    y_coord = (math.floor(index/10) if cell[10] == 255 else cell[10])

                    if game_board[y_coord][x_coord] != cell[1]:
                        fill = piece_colors[cell[1]]
                        canvas.create_rectangle(x_coord*pixel_size, y_coord*pixel_size, x_coord*pixel_size+pixel_size, y_coord*pixel_size+pixel_size, fill=fill)
                        game_board[y_coord][x_coord] = cell[1]
        except Exception as error:
            print(error)