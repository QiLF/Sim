import tkinter as tk
from PIL import ImageTk
from database import *
from game_functions import *
import struct

title = "Welcome to Sim!"
rules = "1.Two players take turns coloring any uncolored lines.\nOne player colors in one color, " \
        "and the other colors in another color.\n 2.Each player should try to avoid the creation of a triangle made"\
        "solely of their color.\n" \
        "(only triangles with the dots as corners count;intersections of lines are"\
        "not relevant)\n"\
        "3.The player who completes such a triangle loses immediately."

master = tk.Tk()
master.title("Sim")
master.resizable(width=False, height=False)
img_play = ImageTk.PhotoImage(file="img/button1.jpg")
img_quit = ImageTk.PhotoImage(file="img/button2.jpg")
game_frame = tk.Frame(master)
canvas = tk.Canvas(game_frame,
                   width=800,
                   height=450)
title = tk.Label(game_frame,
                 justify="center",
                 font="Times 25 bold",
                 fg="purple",
                 text=title)
rules = tk.Label(game_frame,
                 justify="left",
                 padx=10,
                 font="Times 16 bold",
                 fg="blue",
                 text=rules)
pvp_button = tk.Button(game_frame,
                       justify="right",
                       compound="center",
                       font="Times",
                       text="PVP",
                       image=img_play,
                       command=game_start(canvas, mode="pvp"))
pve_button = tk.Button(game_frame,
                       justify="left",
                       compound="center",
                       font="Times",
                       text="PVE",
                       image=img_play,
                       command=game_start(canvas, mode="pve"))
quit_button = tk.Button(game_frame,
                        justify="left",
                        compound="center",
                        font="Times",
                        text="Quit",
                        image=img_quit,
                        command=master.quit)
hint_checkbox = tk.Checkbutton(game_frame,
                               text="Show Hints",
                               font="Times 16 bold",
                               command=manage_hints(canvas))
var_hint_checkbox = tk.Checkbutton
# p1name_text = tk.Text()
# p2name_text = tk.Text()


def window_init():
    game_frame.grid()
    title.grid(row=0, columnspan=3)
    rules.grid(row=1, columnspan=3)
    canvas.grid(row=2, columnspan=3)
    hint_checkbox.grid(row=3, columnspan=3)
    pvp_button.grid(row=4, column=0)
    pve_button.grid(row=4, column=1)
    quit_button.grid(row=4, column=2)
    draw_lines(canvas)


window_init()
events_bind(canvas)
master.mainloop()



