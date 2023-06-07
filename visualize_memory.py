from PIL import Image, ImageTk
import tkinter as tk

dimensions = (512,512)
data_path = "./dump.data"

#TODO: dynamically adjust dimensions on window resize
def image_from_data(data):
    side = int((len(data)//4)**(1/2) // 1)
    image_size = (side,side)
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
