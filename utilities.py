#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools
import Actions
import time
from random import choice

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
    action_list = ["move_down", "move_up", "move_right", "move_left", "clean", "dead", "load", "stay"]
    for state in all_states:
        for t in range(T + 1):
            for action in action_list:
                q_value_function[str(state), t, action] = 0

    start_time = time.time()
    while time.time() - start_time < time_limit:
        print("q_learning iteration, elapsed time:", time.time() - start_time)
        for s_t in all_states:
            for t in range(T):
                # get possible action for s_t
                action_list_s_t = simulator.get_actions(s_t)
                # get all q_value, for s_t and all the possible action
                q_value_action_s_t = [q_value_function[str(s_t), t, action] for action in action_list_s_t]
                # get a_t, the action which maximize the q_value
                a_t = action_list_s_t[q_value_action_s_t.index(max(q_value_action_s_t))]

                # get s_t+1 and reward from simulator
                s_t_plus_1, reward = simulator.get(a_t, s_t)
                # get possible action for s_t+1 and find the maximum q_value for all these actions
                action_list_s_t_plus_1 = simulator.get_actions(s_t_plus_1)
                max_q_value_action_s_t_plus_1 = max([q_value_function[str(s_t_plus_1), t + 1, action]
                                                     for action in action_list_s_t_plus_1])

                # compute delta and update q_value
                delta = reward + max_q_value_action_s_t_plus_1 - q_value_function[str(s_t), t, a_t]
                q_value_function[str(s_t), t, a_t] += alpha * delta
                # prepare next event in the episode
                s_t = s_t_plus_1

    policy = dict()
    for state in all_states:
        q_value_action_list = [q_value_function[str(state), 0, action] for action in action_list]
        action_index = q_value_action_list.index(max(q_value_action_list))
        if action_list[action_index] == "move_down":
            print(state, q_value_action_list, action_list[action_index])
        policy[str(state), 1] = action_list[action_index]

    return policy


def epsilon_policy(q, epsilon, nb_action):
    policy = [1] * nb_action
    policy = [i * epsilon / nb_action for i in policy]
    policy[q.index(max(q))] += 1 - epsilon
    return policy


def monte_carlo(all_states, simulator, T, time_limit):
    # Initialisation de la politique et de la fonction de valeur
    q_value_function = dict()
    action_list = ["move_up", "move_down", "move_right", "move_left", "clean", "dead", "load", "stay"]
    for state in all_states:
        for t in range(T):
            for action in action_list:
                q_value_function[str(state), t, action] = 0
    pi = epsilon_policy(q_value_function, 0.5, len(q_value_function))

    start_time = time.time()
    while time.time() - start_time < time_limit:
        print("new iteration")
        # Génération d'épisode
        episode = []
        s0 = choice(all_states) #je pense qu'il faut utiliser "pi" pour trouver s0, mais je ne sais pas comment faire
        for t in range(T):
            a0 = choice(action_list)
            s1, r0 = simulator.get(a0, s0)
            episode.append([s0, a0, r0])
            s0 = s1

        g = 0
        c = 0
        for s, a in episode:
            for i in range(len(episode)):
                if episode[i][0] == s and episode[i][1] == a:
                    g += episode[i][2]
                    c += 1
            q_value_function[s, t, a] = g / c

        # Mise à jour de politiques
        pi = epsilon_policy(q_value_function, 0.5, len(q_value_function))
