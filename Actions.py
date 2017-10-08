#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import copy


def reasign(s):
    """
    Deep copy of s to bypass the "passing by reference" done by python
    :param s: a state
    :param grid_size: un tuple (x,y) représentant la taille de la grille 
    :return new_state: la copie 
    """
    new_state = {}
    for key in s.keys():
        new_state[key] = copy.copy(s[key])

    return new_state


def move_up(s, grid_size):
    """
    Change la position du robot en décrementant la coordonnée y de 1
    :param s: un état
    :param grid_size: un tuple (x,y) représentant la taille de la grille 
    :return new_state: le nouvel état
    """
    new_state = unload(s)
    if new_state["robot_pos"][1] != 0:
        new_state["robot_pos"][1] -= 1
    return new_state


def move_down(s, grid_size):
    """
    Change la position du robot en incrémentant la coordonnée y de 1   
    :param s: un état 
    :param grid_size: un tuple (x,y) représentant la taille de la grille 
    :return new_state: le nouvel état
    """
    new_state = unload(s)
    if new_state["robot_pos"][1] != grid_size[1] - 1:
        new_state["robot_pos"][1] += 1
    return new_state


def move_left(s, grid_size):
    """
    Change la position du robot en décrémentant la coordonnée x de 1    
    :param s: un état
    :param grid_size: un tuple (x,y) représentant la taille de la grille 
    :return new_state: le nouvel état
    """
    new_state = unload(s)
    if new_state["robot_pos"][0] != 0:
        new_state["robot_pos"][0] -= 1
    return new_state


def move_right(s, grid_size):
    """
    Change la position du robot en incrémentant la coordonnée x de 1    
    :param s: un état
    :return new_state: le nouvel état
    """
    new_state = unload(s)
    if new_state["robot_pos"][0] != grid_size[0] - 1:
        new_state["robot_pos"][0] += 1
    return new_state


def clean(s):
    """
    Nettoie la case sur laquelle se trouve le robot    
    :param s: un état
    :return new_state: le nouvel état
    """
    new_state = unload(s)
    new_state["dirty_cells"].remove(s["robot_pos"])
    return new_state


def load(s):
    """
    Charge la batterie    
    :param s: un état
    :return new_state: le nouvel état
    """
    new_state = reasign(s)
    new_state["battery_level"] += 1
    return new_state


def unload(s):
    """
    décharge la batterie    
    :param s: un état
    """
    new_state = reasign(s)
    new_state["battery_level"] -= 1
    return new_state

