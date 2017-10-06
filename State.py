#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Constantes import *


class State:
    """
    Classe correspondant à l'état de notre système
    """

    def __init__(self, grid_size, base_pos, robot_pos, battery_level, dirty_cells=[], check_parameter=True):
        """
        :param grid_size: un tuple (x,y) avec la taille de la grille
        :param base_pos: un tuple (x,y) avec la position de la base
        :param robot_pos: un tuple (x,y) avec la position du robot
        :param battery_level: un entier, le niveau de la battery compris en 0 et MAX_BATTERY_LEVEL
        :param dirty_cells: une liste de tuple contenant la position des cellules salles 
        """
        self.column_nb = grid_size[0]
        self.row_nb = grid_size[1]
        self.check_parameter = check_parameter

        # verifications des paramètres passés
        if check_parameter:
            self.positions = [(x,y) for x in range(self.column_nb) for y in range(self.row_nb)]

            for pos_to_test in [("base_pos", base_pos), ("robot_pos", robot_pos)] + \
                    [("dirty_cells", pos) for pos in dirty_cells]:
                if pos_to_test[1] not in self.positions:
                    raise ValueError("La position " + pos_to_test[0] + str(pos_to_test[1]) +
                                     " n'est pas admissible dans une grille de taille " + str(grid_size))

            if base_pos in dirty_cells:
                raise ValueError("La base ne peut pas etre sur une cellule sale")

            if battery_level > MAX_BATTERY_LEVEL:
                raise ValueError("Le niveau de batterie ne peut pas être supérieur à " + MAX_BATTERY_LEVEL)

        # si paramètres valides, initialisation des attributs
        self.base_pos = base_pos
        self.robot_pos = robot_pos
        self.battery_level = battery_level
        self.dirty_cells = dirty_cells

    def set_robot_pos(self, pos):
        if self.check_parameter:
            if pos not in self.positions:
                raise ValueError('set_robot_pos, value out of range')
        self.robot_pos = pos

    def set_battery(self, level):
        if self.check_parameter:
            if level > MAX_BATTERY_LEVEL:
                raise ValueError('set_battery, value out of range')
        self.battery_level = level

    def clean_cell(self, pos):
        try:
            self.dirty_cells.remove(pos)
        except ValueError:
            raise ValueError("Can' clean cell at" + pos + ". It's already clean")

    def __repr__(self):
        # on instantie une représentation de l'état sous forme de string
        str_rep = [["" for i in range(self.column_nb)] for y in range(self.row_nb)]
        for row in range(self.row_nb):
            for col in range(self.column_nb):
                if self.base_pos == (col, row):
                    str_rep[row][col] += BASE
                if self.robot_pos == (col, row):
                    str_rep[row][col] += ROBOT
                if (col, row) in self.dirty_cells:
                    str_rep[row][col] += CELLULE_SALE
        return "\n".join(["battery: " + str(self.battery_level)] + [str(row) for row in str_rep]) + "\n"






