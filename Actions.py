#!/usr/bin/env python3
# -*- coding: utf-8 -*-


def move_up(s):
    """
    Change la position du robot en décrementant la coordonnée y de 1
    :param s: un état
    """
    s.set_robot_pos((s.robot_pos[0], s.robot_pos[1] - 1))
    s.set_battery(s.battery_level - 1)


def move_down(s):
    """
    Change la position du robot en incrémentant la coordonnée y de 1   
    :param s: un état 
    """
    s.set_robot_pos((s.robot_pos[0], s.robot_pos[1] + 1))
    s.set_battery(s.battery_level - 1)


def move_left(s):
    """
    Change la position du robot en décrémentant la coordonnée x de 1    
    :param s: un état
    """
    s.set_robot_pos((s.robot_pos[0] - 1, s.robot_pos[1]))
    s.set_battery(s.battery_level - 1)


def move_right(s):
    """
    Change la position du robot en incrémentant la coordonnée x de 1    
    :param s: un état
    """
    s.set_robot_pos((s.robot_pos[0] + 1, s.robot_pos[1]))
    s.set_battery(s.battery_level - 1)


def clean(s):
    """
    Nettoie la case sur laquelle se trouve le robot    
    :param s: un état
    """
    s.clean_cell(s.robot_pos)


def charge(s):
    """
    Charge la batterie    
    :param s: un état
    """
    s.set_battery(s.battery_level + 1)

