#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter
from tkinter.ttk import Progressbar, Style
import Actions
import os


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
    def __init__(self, simulator, p, grid_size, maximum_battery, state, title):
        self.simulator = simulator
        self.policy = p
        self.grid_size = grid_size
        self.maximum_battery = maximum_battery
        self.state = state
        self.init_state = state

        # tk object
        self.root = tkinter.Tk()
        self.root.title(title)
        dirname = os.path.dirname(os.path.abspath(__file__))
        self.s_img = tkinter.PhotoImage(file=dirname + "/img/S.gif")
        self.br_img = tkinter.PhotoImage(file=dirname + "/img/BR.gif")
        self.b_img = tkinter.PhotoImage(file=dirname + "/img/B.gif")
        self.sr_img = tkinter.PhotoImage(file=dirname + "/img/SR.gif")
        self.r_img = tkinter.PhotoImage(file=dirname + "/img/R.gif")
        self.default_img = tkinter.PhotoImage(file=dirname + "/img/default.gif")
        self.battery_img = tkinter.PhotoImage(file=dirname + "/img/battery.gif")
        self.battery_label = tkinter.Label(self.root, image=self.battery_img)

        self.robot_pos_label = tkinter.Label(self.root, text="robot_pos:")
        self.robot_pos_entry = tkinter.Entry(self.root)

        self.battery_level_label = tkinter.Label(self.root, text="battery_level:")
        self.battery_level_entry = tkinter.Entry(self.root)

        self.base_pos_label = tkinter.Label(self.root, text="base_pos:")
        self.base_pos_entry = tkinter.Entry(self.root)

        self.dirty_cell_label = tkinter.Label(self.root, text="dirty_cells:")
        self.dirty_cell_entry = tkinter.Entry(self.root)

        self.progess = Progressbar(self.root, orient="horizontal", mode="determinate", maximum=self.maximum_battery,
                                   value=self.state["battery_level"])

        self.restart_button = tkinter.Button(self.root, text="Restart", command=self.restart, font="Arial 10 bold",
                                             width=10)

        self.grid = [[None for _ in range(self.grid_size[0])] for _ in range(self.grid_size[1])]

        s = Style()
        s.theme_use('classic')

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
        try:
            action = self.policy[str(self.state)]
            print("action:", action)

            new_state = self.do_action(action)
            diffs = self.get_diff(new_state)

            if diffs:
                self.state = new_state
                print_state(self.grid_size, self.state)

            for diff in diffs:
                if diff == "battery_level":
                    self.progess.configure(value=self.state["battery_level"])
                else:
                    col, row = diff
                    self.grid[row][col].configure(image=self.get_img(row, col))
        except KeyError as e:
            print("La configuration est invalide, l'état est inconnu")
            print("KeyError", e)

        self.root.after(1000, self.update)

    def do_action(self, action):
        """
        Exécute l'action à l'aide du simulateur
        :param action: une action donnée par le politique
        :return : le nouvelle état après l'action
        """
        if action == "move_up":
            return Actions.move_up(self.state, self.grid_size) if self.simulator.roll_dice(self.simulator.moving_proba)\
                   else Actions.unload(self.state)
        elif action == "move_down":
            return Actions.move_down(self.state, self.grid_size) if self.simulator.roll_dice(self.simulator.moving_proba)\
                   else Actions.unload(self.state)
        elif action == "move_right":
            return Actions.move_right(self.state, self.grid_size) if self.simulator.roll_dice(self.simulator.moving_proba)\
                   else Actions.unload(self.state)
        elif action == "move_left":
            return Actions.move_left(self.state, self.grid_size) if self.simulator.roll_dice(self.simulator.moving_proba)\
                   else Actions.unload(self.state)
        elif action == "load":
            return Actions.load(self.state) if self.simulator.roll_dice(self.simulator.charging_proba)\
                   else self.state
        elif action == "clean":
            return Actions.clean(self.state) if self.simulator.roll_dice(self.simulator.cleaning_proba)\
                   else Actions.unload(self.state)
        elif action == "dead" or action == "stay":
            return self.state

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
        self.robot_pos_entry.insert(0, str(self.state["robot_pos"]))
        self.base_pos_entry.insert(0, str(self.state["base_pos"]))
        self.battery_level_entry.insert(0, str(self.state["battery_level"]))
        self.dirty_cell_entry.insert(0, str(self.state["dirty_cells"]))

        self.base_pos_label.grid(row=0, columnspan=2)
        self.base_pos_entry.grid(row=0, column=2, columnspan=self.grid_size[0] * 5)

        self.robot_pos_label.grid(row=1, columnspan=2)
        self.robot_pos_entry.grid(row=1, column=2, columnspan=self.grid_size[0] * 5)

        self.battery_level_label.grid(row=2, columnspan=2)
        self.battery_level_entry.grid(row=2, column=2, columnspan=self.grid_size[0] * 5)

        self.dirty_cell_label.grid(row=3, columnspan=2)
        self.dirty_cell_entry.grid(row=3, column=2, columnspan=self.grid_size[0] * 5)

        self.battery_label.grid(row=4)
        self.progess.grid(row=4, column=1, columnspan=2)
        self.restart_button.grid(row=4, column=3, columnspan=2)

        for row in range(self.grid_size[1]):
            for col in range(self.grid_size[0]):
                    cell = tkinter.Label(self.root, image=self.get_img(row, col))
                    cell.grid(row=row + 5, column=col, sticky="W")
                    self.grid[row][col] = cell

        print_state(self.grid_size, self.state)

    def restart(self):
        print("restart")
        self.init_state["robot_pos"] = [int(i) for i in self.robot_pos_entry.get() if i not in ["[", "]", " ", ","]]
        self.init_state["base_pos"] = [int(i) for i in self.base_pos_entry.get() if i not in ["[", "]", " ", ","]]
        self.init_state["battery_level"] = int(self.battery_level_entry.get())
        temp_list = self.dirty_cell_entry.get().replace("[", "").replace("]", "").split(', ')
        self.init_state["dirty_cells"] = sorted([[int(temp_list[i]), int(temp_list[i+1])] for i in range(0, len(temp_list) - 1, 2)])

        for elem in [self.battery_level_entry, self.base_pos_entry, self.robot_pos_entry, self.dirty_cell_entry]:
            elem.delete(0, "end")

        self.state = self.init_state
        self.clear_grid()
        self.init()

    def run(self):
        """
        Methode appelé pour lancer l'UI        
        """
        self.init()
        self.root.after(2000, self.update)
        self.root.attributes("-topmost", True)
        self.root.mainloop()

