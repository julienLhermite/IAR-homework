#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter.ttk import Progressbar
import itertools
import Actions
from threading import Thread


def print_state(grid_size, state):
    """
    Représente l'état du système sous forme de string
    Une case sale est représenté par un S, le robot par un R et le base par un B
    """
    str_rep = [["" for i in range(grid_size[0])] for y in range(grid_size[1])]

    for row in range(grid_size[1]):
        for col in range(grid_size[0]):
            if state["base_pos"] == [col, row]:
                str_rep[row][col] += "B"
            if state["robot_pos"] == [col, row]:
                str_rep[row][col] += "R"
            if [col, row] in state["dirty_cells"]:
                str_rep[row][col] += "S"

    print("\n".join(["battery: " + str(state["battery_level"])] + [str(row) for row in str_rep]) + "\n")


class Display:
    """
    Class affichant l'état du système à l'aide de tkinter 
    """
    def __init__(self, p, grid_size, maximum_battery, state):
        self.policy = p
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
        self.label = tkinter.Label(self.root, image=self.battery_img)
        self.progess = Progressbar(self.root, orient="horizontal", mode="determinate", maximum=self.maximum_battery,
                                   value=self.state["battery_level"])

    def get_diff(self, new_state):
        """
        Etant donné l'ancien état et le nouveau retourne une liste spécifiant les éléments à mettre à jour dans l'UI
        :param new_state: le nouvel état
        :return diffs: la liste d'élément à mettre à jour 
        """
        diffs = list()
        for key in new_state.keys():
            if new_state[key] != self.state[key]:
                if key == "battery_level":
                    diffs.append(key)
                elif key == "dirty_cells":
                    diffs += [pos for pos in self.state[key] if pos not in new_state[key]]
                else:
                    diffs += [self.state[key], new_state[key]]

        return diffs

    def update(self):
        """
        Méthode mettant à jour régulièrement l'UI
        """
        self.clear_grid()
        action = self.policy[str(self.state), 1]
        self.do_action(action)
        self.progess.configure(value=self.state["battery_level"])
        print(action)
        print_state(self.grid_size, self.state)
        self.init()

        self.root.after(800, self.update)

    def do_action(self, action):

        if action == "move_up":
            self.state = Actions.move_up(self.state, self.grid_size)
        elif action == "move_down":
            self.state = Actions.move_down(self.state, self.grid_size)
        elif action == "move_right":
            self.state = Actions.move_right(self.state, self.grid_size)
        elif action == "move_left":
            self.state = Actions.move_left(self.state, self.grid_size)
        elif action == "load":
            self.state = Actions.load(self.state)
        elif action == "clean":
            self.state = Actions.clean(self.state)


    def clear_grid(self):
        """
        clear the tk grid
        """
        for child in self.root.grid_slaves():
            child.grid_forget()

    def get_img(self, row, col):
        """
        Etant donné une ligne et une colonne détermine l'image à afficher à cette position      
        :return img: l'image à afficher
        """
        if self.state["base_pos"] == [col, row] and self.state["robot_pos"] == [col, row]:
            return self.br_img
        elif self.state["base_pos"] == [col, row]:
            return self.b_img
        elif self.state["robot_pos"] == [col, row] and [col, row] in self.state['dirty_cells']:
            return self.sr_img
        elif self.state["robot_pos"] == [col, row]:
            return self.r_img
        elif [col, row] in self.state['dirty_cells']:
            return self.s_img
        else:
            return self.default_img

    def init(self):
        """
        Initialise l'affichage de l'UI
        """
        self.label.grid(row=0)
        self.progess.grid(row=0, column=1, columnspan=self.grid_size[0] - 1)
        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                    cell = tkinter.Label(self.root, image=self.get_img(row, col))
                    cell.grid(row=row + 1, column=col)

    def run(self):
        """
        Methode appelé pour lancer l'UI        
        """
        self.init()
        self.update()
        self.root.mainloop()

