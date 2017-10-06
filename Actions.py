#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def move_up(s):
    """
    Change la position du robot en décrementant la coordonnée y de 1
    :param s: un état
    """
    s["robot_pos"][1] -= 1
    unload(s)


def move_down(s):
    """
    Change la position du robot en incrémentant la coordonnée y de 1   
    :param s: un état 
    """
    s["robot_pos"][1] += 1
    unload(s)


def move_left(s):
    """
    Change la position du robot en décrémentant la coordonnée x de 1    
    :param s: un état
    """
    s["robot_pos"][0] -= 1
    unload(s)


def move_right(s):
    """
    Change la position du robot en incrémentant la coordonnée x de 1    
    :param s: un état
    """
    s["robot_pos"][0] += 1
    unload(s)


def clean(s):
    """
    Nettoie la case sur laquelle se trouve le robot    
    :param s: un état
    """
    s["dirty_cells"].remove(s["robot_pos"])
    unload(s)


def load(s):
    """
    Charge la batterie    
    :param s: un état
    """
    s["battery_level"] += 1


def unload(s):
    """
    décharge la batterie    
    :param s: un état
    """
    s["battery_level"] -= 1

