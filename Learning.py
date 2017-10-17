#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools, os
import Actions
import time
import copy
import signal
from State import print_state
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from random import choice
from Debug import Debug

hasard_nb, policy_nb = 0, 0
interrupt_flag = False


def signal_handler(signal, frame):
        global interrupt_flag
        print('interrupt!')
        interrupt_flag = True


def get_possible_dirty_cells(grid_size, base_pos):
    """
    Etant donné une taille de grille et une position de la base dans la grille, retourne la liste de toutes les 
    combinaisons de cellules salles possible
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


def dynamic_programming(all_states, simulator, gamma, epsilon):
    """
    Implémentation de l'optimisation de la politique par dynamic programming
    :param all_states: la liste de tous les états
    :param simulator: le simulateur
    :param gamma:
    :param epsilon:
    :return policy: la politique optimale 
    """

    # Initialisation de la politique et de la fonction de valeur
    value_function = dict()
    value_function_bis = dict()
    policy = dict()
    for state in all_states:
        value_function[str(state)] = 0
        value_function_bis[str(state)] = 1
        policy[str(state)] = "stay"

    stop_criteria = max([abs(value_function[i] - value_function_bis[i]) for i in value_function.keys()])
    mean_values = [0.]
    x = [0]
    while stop_criteria > epsilon:
        value_function_bis = Actions.reasign(value_function)

        mean_value = 0.
        for state in all_states:
            to_maximize = []
            action_list = simulator.get_actions(state)
            for i, action in enumerate(action_list):
                reward, future = simulator.get_with_model(action, state)
                to_maximize.append(reward)

                for proba, future_state in future:
                    to_maximize[i] += gamma * proba * value_function[str(future_state)]

            value_function[str(state)] = max(to_maximize)
            mean_value += value_function[str(state)]

            opti_action = action_list[to_maximize.index(value_function[str(state)])]
            policy[str(state)] = opti_action

        stop_criteria = max([abs(value_function[i] - value_function_bis[i]) for i in value_function.keys()])
        print("dynamic programming iteration:", stop_criteria, "<", epsilon, "?")

        # for plotting
        x.append(x[-1] + 1)
        mean_value = mean_value / len(all_states)
        mean_values.append(mean_value)

    # plot
    dirname = os.path.dirname(os.path.abspath(__file__))
    # plt.figure()

    plt.plot(x, mean_values)

    title = 'DP, EPSILON=' + "{:3}".format(epsilon) + " GRID=" + "{:9}".format(str(simulator.grid_size)) + "BAT:" + str(
        simulator.max_battery_level) + " - mean_values of policy"
    plt.title(title)
    plt.ylabel('Mean value')
    plt.xlabel('Iteration')
    plt.draw()
    plt.savefig(dirname + "/plots/" + title + ".png")

    return policy


def a_epsilon_greedy(simulator, state, epsilon, policy):
    """
    Etant donnée un état, et un hyperparamètre epsilon retourne en fonction d'un tirage dépendant de epsilon
    une action pris au hasard dans la liste des actions possibles, ou celles prescrite par la politique
    :param simulator: le simulateur
    :param state: un état
    :param epsilon: un hyperparamètre
    :param policy: la politique
    :return: une action
    """
    global policy_nb, hasard_nb
    action_list = simulator.get_actions(state)
    if simulator.roll_dice(1 - epsilon + epsilon/len(action_list)):
        policy_nb += 1
        return policy[str(state)]
    else:
        hasard_nb += 1
        a = choice(action_list)
        return a


def q_epsilon_greedy(simulator, state, epsilon, action_list, q_function):
    """
    Fonction epsillon greedy qui renvoit l'action de la fonction de Qvaleur associée à un état
    :param simulator: Notre simulateur comprenant des focntionnalités de tirage aléatoire
    :param state: Etat du système actuel
    :param epsillon: Paramètre de convergence
    :param action_list: Liste des actions possibles pour l'état state
    :param q_function: Représentation de notre fonction de Qvaleur
    :return: l'action de la fonction de Qvaleur associée à un état selon la loie epsilon greedy
    """
    if simulator.roll_dice(1 - epsilon + epsilon/len(action_list)):
        q_action_list = [q_function[str(state), action] for action in action_list]
        action_index = q_action_list.index(max(q_action_list))
        # print(1 - epsilon + epsilon / len(action_list), "Qvaleur maximisée")
        return action_list[action_index]
    else:
        a = choice(action_list)
        # print(1 - epsilon + epsilon / len(action_list), "Qvaleur hasard")
        return a


def monte_carlo(all_states, simulator, time_limit, T, gamma, epsilon, alpha, initial_state, step=1):
    """
    Implémentation de l'optimisation de la politique par monte_carlo control
    :param all_states: la liste de tous les états
    :param simulator: le simulateur
    :param time_limit: la limite de temps en seconde
    :param T: la longueur des épisodes générés
    :param gamma: un hyperparamètre
    :param epsilon: un autre hyperparamètre 
    :param alpha: encore un
    :param initial_state: l'état initial
    :return policy: la politique 
    """
    global policy_nb, hasard_nb
    # Initialisation de la q_function et la policy
    q_function = dict()
    policy = dict()
    for state in all_states:
        possible_actions = simulator.get_actions(state)
        policy[str(state)] = choice(possible_actions)
        for action in possible_actions:
            q_function[str(state), action] = 0

    start_time = time.time()
    time_spent, count = 0, 1
    iter = 0
    mean_rewards, x = [], []
    v_s0 = []
    episode = []
    stop = True
    while time.time() - start_time < time_limit:
        s0 = Actions.reasign(initial_state)

        # on print toutes les 10 secondes pour ne pas polluer la console
        time_spent = time.time() - start_time
        if time_spent > step * count:
            count += 1
            action_list = simulator.get_actions(s0)
            q_values_s0 = [q_function[str(s0), action] for action in action_list]
            Debug("monte_carlo iteration, elapsed time", time.time() - start_time, v_s0=max(q_values_s0))
            # Debug(policy_nb=policy_nb, hasard_nb=hasard_nb, epsilon=epsilon,
            #       policy_proba=1 - epsilon + epsilon/len(action_list))

            # add value to vector for plot
            mean_reward = total_reward/T
            mean_rewards.append(mean_reward)
            v_s0.append(max(q_values_s0))
            x.append(step * count)

        # generation d'un episode
        episode = []
        policy_nb, hasard_nb = 0, 0
        for t in range(T + 1):
            a0 = a_epsilon_greedy(simulator, s0, epsilon, policy)
            # print(s0, a0)
            reward, future_state = simulator.get(a0, s0)
            episode.append((s0, a0, reward))
            s0 = future_state

        total_reward = 0
        for t, event in enumerate(episode):
            # calcul du retour
            retour = 0
            for k in range(t, T + 1):
                retour += (gamma ** (k - t)) * episode[k][2]
            total_reward += event[2]

            # maj q _value
            q_function[str(event[0]), event[1]] += alpha * (retour - q_function[str(event[0]), event[1]])

            # maj politique
            q_action_list = [q_function[str(event[0]), action] for action in simulator.get_actions(event[0])]
            action_index = q_action_list.index(max(q_action_list))
            policy[str(event[0])] = simulator.get_actions(event[0])[action_index]
        if epsilon > 0.1:
            epsilon /= 1.00001

        if interrupt_flag:
            break

    # Print final
    print("### FIN du calcul ###")
    print("actions en s0:", simulator.get_actions(initial_state))
    print("q_val associées:",
          ["{:05.2f}".format(q_function[str(initial_state), action]) for action in simulator.get_actions(initial_state)])
    print("monte_carlo iteration, elapsed time: {:05.2f},".format(time.time() - start_time),
          "v(s0) = {:6.2f}".format(max([q_function[str(initial_state), action] for action in simulator.get_actions(initial_state)])))

    dirname = os.path.dirname(os.path.abspath(__file__))
    # plt.figure()
    plt.plot(x, mean_rewards)
    title = 'MC, T=' + "{:3}".format(T) + " GRID=" + "{:9}".format(str(simulator.grid_size)) + "BAT:" + str(simulator.max_battery_level) + " T_LIMIT:" + "{:5}".format(time_limit) + " - mean_reward"
    plt.title(title)
    plt.ylabel('Récompense moyenne')
    plt.xlabel('Time(s)')
    plt.draw()

    plt.savefig(os.path.join(dirname, "/plots/" + str(title) + ".png"))

    plt.clf()
    plt.plot(x, v_s0)
    title = 'MC, T=' + "{:3}".format(T) + " GRID=" + "{:9}".format(str(simulator.grid_size)) + "BAT:" + str(simulator.max_battery_level) + " T_LIMIT:" + "{:5}".format(time_limit) + " - v_s0(t)"
    plt.ylabel('v(s0)')
    plt.xlabel('Time(s)')
    plt.draw()
    plt.savefig(os.path.join(dirname, "/plots/" + str(title) + ".png"))

    return policy


def q_learning(all_states, simulator, time_limit, gamma, epsilon, alpha, initial_state):

    # Initialisation de la q_function et la policy
    q_function = dict()
    policy = dict()
    for state in all_states:
        policy[str(state)] = choice(simulator.get_actions(state))
        for action in simulator.get_actions(state):
            q_function[str(state), action] = 0

    s0 = Actions.reasign(initial_state)
    a0 = a_epsilon_greedy(simulator, s0, epsilon, policy)

    # Algorithme de Q Learning
    start_time = time.time()
    count = 1
    q_values_s0, t = [], []
    while time.time() - start_time < time_limit:
        global interrupt_flag
        # print("q_Learning iteration, elapsed time:", time.time() - start_time)

        reward, future_state = simulator.get(a0, s0)
        future_action = q_epsilon_greedy(simulator, future_state, epsilon, simulator.get_actions(future_state), q_function)
        delta = reward + gamma * q_function[str(future_state), future_action] - q_function[str(s0), a0]

        # Maj q_value
        q_function[str(s0), a0] += alpha * delta
        s0 = future_state
        a0 = future_action

        # Maj politique
        action_list = simulator.get_actions(s0)
        q_action_list = [q_function[str(s0), action] for action in action_list]
        policy[str(s0)] = action_list[q_action_list.index(max(q_action_list))]

        if reward == simulator.dead_reward:
            s0 = Actions.reasign(initial_state)
            a0 = a_epsilon_greedy(simulator, initial_state, epsilon, policy)

        # Debug
        time_spent = time.time() - start_time
        if time_spent > 1 * count:
            count += 1
            t.append(time_spent)
            q_values = [q_function[str(initial_state), action] for action in simulator.get_actions(initial_state)]
            q_value_s0 = max(q_values)
            q_values_s0.append(q_value_s0)
            Debug("time spent", time_spent, q_value_s0=q_value_s0)

        if interrupt_flag:
            break

    # Plot
    dirname = os.path.dirname(os.path.abspath(__file__))
    plt.plot(t, q_values_s0)
    title = 'QL, GRID=' + "{:9}".format(str(simulator.grid_size)) + "BAT:" + str(simulator.max_battery_level) + " T_LIMIT:" + "{:5}".format(time_limit) + " - q_value_s0"
    plt.title(title)
    plt.ylabel('q_value_s0')
    plt.xlabel('Time(s)')
    plt.draw()
    plt.savefig(os.path.join(dirname, "plots", str(title) + ".png"))

    return policy
