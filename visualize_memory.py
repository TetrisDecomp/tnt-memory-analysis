from PIL import Image, ImageTk
import tkinter as tk

dimensions = (256,512)
data_path = "./dump.data"

def image_from_data (data):
    image_size = (40,20) 
    image = Image.frombytes('RGBA', image_size, data, 'raw').resize(dimensions, Image.BOX)
    return image

window = tk.Tk()
canvas = tk.Canvas(window, width=dimensions[0], height=dimensions[1])
canvas.pack(expand="yes", fill="both")
canvas.configure(bg="black")

while True:
    window.update()
    window.update_idletasks()
    with open(data_path, mode="rb") as file:
        try:
            data = file.read()
            image = image_from_data(data)
            tk_image = ImageTk.PhotoImage(image=image)
            canvas.delete()
            canvas.create_image(0,0,anchor="nw",image=tk_image)
        except Exception as error:
            print(error)
