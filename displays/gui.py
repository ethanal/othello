import tkinter
from .base import Display


class GraphicalDisplay(Display):

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("Reversi")
        self.root.geometry("500x500")
        self.root.resizable(width=False, height=False)
        # canvas = tkinter.Canvas(root,
        #                         width=width,
        #                         height=height,
        #                         highlightthickness=0)
        # canvas.pack()

        # add_image_to_canvas(total_gradient(I), canvas)

        # def click(event):
        #     max_y, max_x = canvas.np_img.shape[:2]
        #     if 0 < event.x < max_x and 0 < event.y < max_y:
        #         canvas.delete("all")
        #         canvas.np_img = resize(canvas.np_img, event.x, event.y)
        #         add_image_to_canvas(canvas.np_img, canvas)

        # root.bind("<Button-1>", click)
        self.root.bind("<q>", quit)
        self.root.mainloop()
