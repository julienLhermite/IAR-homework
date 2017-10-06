#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter.ttk import Progressbar
import threading
import time


def print_state(grid_size, state):
    """
    Représente l'état du système sous forme de string
    Une case sale est représenté par un S, le robot par un R et le base par un B
    """
    str_rep = [["" for i in range(grid_size[0])] for y in range(grid_size[1])]

    for row in range(grid_size[1]):
        for col in range(grid_size[0]):
            if state["base_pos"] == (col, row):
                str_rep[row][col] += "B"
            if state["robot_pos"] == (col, row):
                str_rep[row][col] += "R"
            if (col, row) in state["dirty_cells"]:
                str_rep[row][col] += "S"

    print("\n".join(["battery: " + str(state["battery_level"])] + [str(row) for row in str_rep]) + "\n")


class Display:
    def __init__(self, q, grid_size, maximum_battery, state):
        self.queue = q
        self.root = tkinter.Tk()
        self.grid_size = grid_size
        self.maximum_battery = maximum_battery
        self.state = state
        self.s_img =  tkinter.PhotoImage(file="img/S.gif")
        self.br_img = tkinter.PhotoImage(file="img/BR.gif")
        self.b_img = tkinter.PhotoImage(file="img/B.gif")
        self.sr_img = tkinter.PhotoImage(file="img/SR.gif")
        self.r_img = tkinter.PhotoImage(file="img/R.gif")
        self.default_img = tkinter.PhotoImage(file="img/default.gif")
        self.battery_img = tkinter.PhotoImage(file="img/battery.gif")
        self.l = tkinter.Label(self.root, image=self.battery_img)
        self.l.grid(row=0)

    def clear(self):
        for child in self.root.grid_slaves():
            child.grid_forget()

    def update(self):
        print("update")

        p = Progressbar(self.root, orient="horizontal", mode="determinate", maximum=self.maximum_battery,
                        value=self.state["battery_level"])
        p.grid(row=0, column=1, columnspan=self.grid_size[0] - 1)

        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                if self.state["base_pos"] == (col, row) and self.state["robot_pos"] == (col, row):
                    cell = tkinter.Label(self.root, image=self.br_img)
                    cell.grid(row=row + 1, column=col)
                elif self.state["base_pos"] == (col, row):
                    cell = tkinter.Label(self.root, image=self.b_img)
                    cell.grid(row=row + 1, column=col)
                elif self.state["robot_pos"] == (col, row) and (col, row) in self.state['dirty_cells']:
                    cell = tkinter.Label(self.root, image=self.sr_img)
                    cell.grid(row=row + 1, column=col)
                elif self.state["robot_pos"] == (col, row):
                    cell = tkinter.Label(self.root, image=self.r_img)
                    cell.grid(row=row + 1, column=col)
                elif (col, row) in self.state['dirty_cells']:
                    cell = tkinter.Label(self.root, image=self.s_img)
                    cell.grid(row=row + 1, column=col)
                else:
                    cell = tkinter.Label(self.root, image=self.default_img)
                    cell.grid(row=row + 1, column=col)

        self.root.after(500, self.update)

    def run(self):
        self.update()
        self.root.mainloop()

