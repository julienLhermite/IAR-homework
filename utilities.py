#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import itertools
import Actions
import time
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from State import print_state
from random import choice


def get_possible_dirty_cells(grid_size, base_pos):
    """
    Etant donné une taille de grille et une position de la base dans la grille, retourne la liste de toutes les
    combinaisons
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


def our_dynamic_programming(all_states, simulator, T):
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
    while stop_criteria > epsilon:
        value_function_bis = Actions.reasign(value_function)

        for state in all_states:
            to_maximize = []
            action_list = simulator.get_actions(state)
            for i, action in enumerate(action_list):
                reward, future = simulator.get_with_model(action, state)
                to_maximize.append(reward)

                for proba, future_state in future:
                    to_maximize[i] += gamma * proba * value_function[str(future_state)]

            value_function[str(state)] = max(to_maximize)
            opti_action = action_list[to_maximize.index(value_function[str(state)])]
            policy[str(state)] = opti_action

        stop_criteria = max([abs(value_function[i] - value_function_bis[i]) for i in value_function.keys()])
        print("dynamic programming iteration:", stop_criteria, "<", epsilon, "?")

    return policy


def our_q_learning(all_states, simulator, T, time_limit, alpha):
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


def a_epsilon_greedy(simulator, state, epsilon, action_list, policy):
    if simulator.roll_dice(1 - epsilon + epsilon/len(action_list)):
        # print(1 - epsilon + epsilon / len(action_list), "politique")
        return policy[str(state)]
    else:
        a = choice(action_list)
        # print(1 - epsilon + epsilon / len(action_list), "hasard:", a)
        return a


def get_all_max(my_list):
    """
    Fonction permettant de récupérer la valeur maximale d'une liste ainsi que l'ensemble des indices des valeurs max
    :param my_list: Une liste de nombres
    :return: Un couple max_value et une liste d'index
    """
    max_value = max(my_list)
    indexes = [index for index, value in enumerate(my_list) if value == max_value]
    return max_value, indexes


def q_epsilon_greedy(simulator, state, epsilon, action_list, q_function):
    """
    Fonction epsillon greedy qui renvoit l'action de la fonction de Qvaleur associée à un état
    :param simulator: Notre simulateur comprenant des focntionnalités de tirage aléatoire
    :param state: Etat du système actuel
    :param epsilon: Paramètre de convergence
    :param action_list: Liste des actions possibles pour l'état state
    :param q_function: Représentation de notre fonction de Qvaleur
    :return: l'action de la fonction de Qvaleur associée à un état selon la loie epsilon greedy
    """
    if simulator.roll_dice(1 - epsilon + epsilon/len(action_list)):
        q_action_list = [q_function[str(state), action] for action in action_list]
        action_index = choice(get_all_max(q_action_list)[1])
        # print(1 - epsilon + epsilon / len(action_list), "Qvaleur maximisée")
        return action_list[action_index]
    else:
        a = choice(action_list)
        # print(1 - epsilon + epsilon / len(action_list), "Qvaleur hasard")
        return a


def monte_carlo(all_states, simulator, time_limit, T, gamma, epsilon, alpha, initial_state):
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
    while time.time() - start_time < time_limit:
        if epsilon > 0.1:
            epsilon /= 1.00001

        s0 = Actions.reasign(initial_state)

        # on print toutes les 10 secondes pour ne pas polluer la console
        time_spent = time.time() - start_time
        if time_spent > 5 * count:
            count += 1
            q_values_s0 = [q_function[str(s0), action] for action in simulator.get_actions(s0)]
            print("## monte_carlo iteration, elapsed time: {:05.2f}s |".format(time.time() - start_time),
                  "v(s0) = {:06.2f}".format(max(q_values_s0)),
                  "  ##")
            print("actions en s0:", simulator.get_actions(s0))
            print("q_val associées:",
                  ["{:05.2f}".format(q_function[str(s0), action]) for action in simulator.get_actions(s0)], "\n")
            mean_reward = total_reward/T
            mean_rewards.append(mean_reward)
            v_s0.append(max(q_values_s0))
            x.append(iter)
            iter += 1


        # generation d'un episode
        episode = []

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
                retour += (gamma ** (t -k)) * episode[k][2]
            total_reward += event[2]

            # maj q _value
            q_function[str(event[0]), event[1]] += alpha * (retour - q_function[str(event[0]), event[1]])

            # maj politique
            q_action_list = [q_function[str(event[0]), action] for action in simulator.get_actions(event[0])]
            action_index = q_action_list.index(max(q_action_list))
            policy[str(event[0])] = simulator.get_actions(event[0])[action_index]



    # Print final
    print("### FIN du calcul ###")
    print("actions en s0:", simulator.get_actions(initial_state))
    print("q_val associées:",
          ["{:05.2f}".format(q_function[str(initial_state), action]) for action in simulator.get_actions(initial_state)])
    print("monte_carlo iteration, elapsed time: {:05.2f},".format(time.time() - start_time),
          "v(s0) = {:6.2f}".format(max([q_function[str(initial_state), action] for action in simulator.get_actions(initial_state)])))

    dirname = os.path.dirname(os.path.abspath(__file__))
    print(dirname)
    # plt.figure()
    plt.plot(x, mean_rewards)
    plt.title('Récompense moyenne par épisode - Monte-Carlo. T=' + str(T))
    plt.ylabel('Récompense moyenne')
    plt.xlabel('MC iteration')
    plt.draw()

    plt.savefig(dirname + "/MC_mean_reward_by_episode.png")

    plt.clf()
    plt.plot(x, v_s0)
    plt.title('v(s0) - Monte-Carlo. T=' + str(T))
    plt.ylabel('v(s0à')
    plt.xlabel('MC iteration')
    plt.draw()
    plt.savefig(dirname + "/MC_v(s0).png")

    return policy


def q_learning(all_states, initial_state, simulator, time_limit, gamma, epsilon, alpha):
    """
    Fonction implémentant l'algorithme qLearning
    :param all_states: Ensemble des états possibles du système
    :param initial_state: Etat de départ pour notre robot
    :param simulator: Classe proposant un ensemble de fonction permettant de simuler le comportement du robt et son
    environnement
    :param time_limit: Durée de l'apprentissage de l'algorithme
    :param gamma: paramètre de calcul
    :param epsilon: paramètre de convergeance
    :param alpha: paramètre de calcul
    :return: Une politique et un couple (time_limit, max(Q(s0, ai)) pour évaluer la performance de l'agorithme
    """
    # Initialisation de la q_function
    q_function = dict()
    for state in all_states:
        possible_action = simulator.get_actions(state)
        for action in possible_action:
            q_function[str(state), action] = 0

    s0 = Actions.reasign(initial_state)
    a0 = choice(simulator.get_actions(s0))

    # Algorithme de Q Learning
    start_time = time.time()
    iteration = 0
    while time.time() - start_time < time_limit:
        # print("q_Learning iteration, elapsed time:", time.time() - start_time)
        reward, future_state = simulator.get(a0, s0)
        future_action = q_epsilon_greedy(simulator, future_state, epsilon, simulator.get_actions(future_state), q_function)
        delta = reward + gamma * q_function[str(future_state), future_action] - q_function[str(s0), a0]
        q_function[str(s0), a0] += alpha*delta
        s0 = future_state
        a0 = future_action
        # Decreasing Episilon parameter
        iteration += 1
        if iteration // 100 == 0:
            iteration = 0
            epsilon /= 2

    # Mise à jour de la politique
    policy = dict()
    for state in all_states:
        action_list = simulator.get_actions(state)
        q_values_list = [q_function[str(state), action] for action in action_list]
        action_index = q_values_list.index(max(q_values_list))
        # if state["robot_pos"] == [1, 0]:
        #     print(action_list)
        #     print(q_action_list)
        policy[str(state)] = action_list[action_index]

    # Display
    # evaluation de performance v(s0) = max Q(s0,a)
    action_list = simulator.get_actions(initial_state)
    q_values_list = [q_function[str(initial_state), action] for action in action_list]
    eval_perf = (time_limit, max(q_values_list))

    return policy, eval_perf
