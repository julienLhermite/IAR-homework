#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools
import Actions
import time
from random import randint

def get_possible_dirty_cells(grid_size, base_pos):
    """
    Etant donné une taille de grille et une position de la base dans la grille, retourne la liste de toutes les combinaisons
    de cellules salles possible
    :param grid_size: un tuple (x,y) représentant la taille de la grille
    :param base_pos: [x, y] la position de la base
    :return: 
    """
    possible_grid_list = [list(i) for i in itertools.product([0, 1], repeat=grid_size[0] * grid_size[1]) if
                          list(i)[base_pos[0] + base_pos[1] * grid_size[0]] == 0]

    possible_dirty_cells = list()
    for possible in possible_grid_list:
        l = list()
        for index, case in enumerate(possible):
            if case == 1:
                l.append([index % grid_size[0], index // grid_size[0]])
        possible_dirty_cells.append(l)

    return possible_dirty_cells


def get_all_states(max_battery_level, grid_size):
    states = list()
    coords = [[x, y] for x in range(grid_size[0]) for y in range(grid_size[1])]
    for level in range(max_battery_level + 1):
        for robot_pos in coords:
            for base_pos in coords:
                for dirty_cells in get_possible_dirty_cells(grid_size, base_pos):
                    state = {
                        "base_pos": base_pos,
                        "robot_pos": robot_pos,
                        "dirty_cells": sorted(dirty_cells),
                        "battery_level": level
                    }

                    states.append(state)

    return states


def dynamic_programming(all_states, simulator, T):
    """
    Implémentation de l'optimisation de la politique par dynamic programming
    :param all_states: la liste de tous les états
    :param simulator: le simulateur
    :param T: la longeur des épisodes
    :return policy: la politique optimale 
    """

    # Initialisation de la politique et de la fonction de valeur
    policy = dict()
    new_policy = dict()
    value_function = dict()
    for state in all_states:
        for t in range(1, T + 1):
            policy[str(state), t] = "move_up"
            value_function[str(state), t] = 0

    # Evaluation et optimisation de la politique
    while policy != new_policy:
        # copie profonde de la politique pour bypass le passage par référence
        new_policy = Actions.reasign(policy)
        print("policy updated")

        for t in range(T-1, 0, -1):
            for state in all_states:
                value = []
                action_list = simulator.get_actions(state)
                for action in action_list:
                    value_item = 0
                    # récupération depuis le simulateur de la récompense et des couples (proba, états futures) étant
                    # donnés une action et un état
                    reward, future = simulator.get_with_model(action, state)
                    value_item += reward
                    for proba, future_state in future:
                        value_item += proba * value_function[str(future_state), t + 1]
                    value.append(value_item)

                max_value = max(value)
                best_action = action_list[value.index(max_value)]
                value_function[str(state), t] = max_value
                policy[str(state), t] = best_action

    return policy


def q_learning(all_states, simulator, T, time_limit, alpha):
    """
    
    :param all_states: 
    :param simulator: 
    :param T: 
    :param time_limit: 
    :return: 
    """
    # Initialisation de la politique et de la fonction de valeur
    q_value_function = dict()
    action_list = ["move_up", "move_down", "move_right", "move_left", "clean", "dead", "load", "stay"]
    for state in all_states:
        for t in range(T):
            for action in action_list:
                q_value_function[str(state), t, action] = 0

    start_time = time.time()
    while time.time() - start_time < time_limit:
        print("new iteration")
        for s0 in all_states:
            # s0 = all_states[randint(0, len(all_states) - 1)]
            for t in range(T - 1):
                action_list_s0 = simulator.get_actions(s0)
                q_value_action_s0 = [q_value_function[str(s0), t, action] for action in action_list_s0]
                a0 = action_list_s0[q_value_action_s0.index(max(q_value_action_s0))]

                s1, reward = simulator.get(a0, s0 )
                action_list_s1 = simulator.get_actions(s1)
                max_q_value_action_s1 = max([q_value_function[str(s1), t + 1, action] for action in action_list_s1])

                delta = reward + max_q_value_action_s1 - q_value_function[str(s0), t, a0]
                q_value_function[str(s0), t, a0] += alpha * delta

    policy = dict()
    for state in all_states:
        q_value_action_list = [q_value_function[str(state), T - 2, action] for action in action_list]
        action_index = q_value_action_list.index(max(q_value_action_list))
        print(state, max(q_value_action_list), action_list[action_index])
        policy[str(state), 1] = action_list[action_index]

    return policy