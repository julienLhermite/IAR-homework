#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import copy
import Actions

class Simulator:

    def __init__(self, grid_size, max_battery_level, moving_proba, cleaning_proba, charging_proba,
                 moving_reward, cleaning_reward, goal_reward, dead_reward, charging_reward):
        """
        :param grid_size: un tuple (x,y) représentant la taille de la grille
        :param max_battery_level: 
        :param moving_proba: la probabilité de réussir à bouger dans la direction souhaitée si la case destination est libre
        :param cleaning_proba: la probabilité de réussir à nettoyer la case lors de l'action clean_cell
        :param charging_proba: la probabilité de réussir à charger la batterie 
        :param moving_reward: récompense recue lorsqu'on on fait un mouvement
        :param cleaning_reward: récompense recue lorsqu'on nettoie une cellule
        :param goal_reward: récompense recue lorsqu'on atteint l'objectif (eg tout est propre et robot sur base)
        :param dead_reward: récompense recue lorsqu'on est mort (batterie nulle hors de la base)
        :param charging_reward: récompense recue lorsqu'on charge le robot
        """
        self.max_battery_level = max_battery_level
        self.grid_size = grid_size
        self.moving_proba = moving_proba
        self.cleaning_proba = cleaning_proba
        self.charging_proba = charging_proba
        self.moving_reward = moving_reward
        self.cleaning_reward = cleaning_reward
        self.goal_reward = goal_reward
        self.dead_reward = dead_reward
        self.charging_reward = charging_reward

    def get_possible_mouvement(self, pos):
        """
        Etant donné une position pos renvoie la liste des mouvements possibles
        :param pos: un tuple (x,y)
        :return possible_actions: la liste des mouvements possibles
        """
        possible_actions = list()
        if pos[0] > 0:
            possible_actions.append("move_left")
        if pos[0] < self.grid_size[0] - 1:
            possible_actions.append("move_right")
        if pos[1] > 0:
            possible_actions.append("move_up")
        if pos[1] < self.grid_size[1] - 1:
            possible_actions.append("move_down")

        return possible_actions

    def roll_dice(self, probabilities):
        """
        Etant donnée une distribution de probabilité, détermine l'évenement qui arrive
        :param probabilities: la liste de probabilités de tous les tirages possibles
        :return: l'index de l'élement se produisant 
        """
        dice = random.random()
        treshold = 0
        for i, p in enumerate(probabilities):
            treshold += p
            if dice < treshold:
                return i

    def get_actions(self, state):
        """
        retourne la liste d'actions possibles étant donné l'état state
        :param state: l'état courant
        :return actions: la liste d'actions possibles 
        """
        actions = list()

        if state["robot_pos"] in state["dirty_cells"]:
            actions.append("clean")

        if state["robot_pos"] == state["base_pos"] and state["battery_level"] < self.max_battery_level:
            actions.append("load")

        if state["dirty_cells"] and state["battery_level"] > 0:
            actions += self.get_possible_mouvement(state["robot_pos"])

        if not state["dirty_cells"] and state["battery_level"] > 0 and state["robot_pos"] != state["base_pos"]:
            actions += self.get_possible_mouvement(state["robot_pos"])

        if not state["dirty_cells"] and state["robot_pos"] == state["base_pos"]:
            actions.append("stay")

        if state["battery_level"] == 0 and state["robot_pos"] != state["base_pos"]:
            actions.append("dead")

        return set(actions)

    def get(self, action, state):
        """
        Etant donné une action et un état, retourne l'état suivant une récompense
        :param action: un string représentant une action 
        :param state: un état du système
        :return state, reward: l'état suivant et une récompense 
        """
        new_state = copy.copy(state)

        if state["robot_pos"] in state["dirty_cells"] and action == "clean":
            if self.roll_dice([self.cleaning_proba, 1 - self.cleaning_proba]) == 0:
                Actions.clean(new_state)
                return new_state, self.cleaning_reward
            else:
                return new_state, self.cleaning_reward

        # if state["robot_pos"] == state["base_pos"] and state["battery_level"] < self.max_battery_level:
        #     actions.append("charge")
        #
        # if state["dirty_cells"] and state["battery_level"] > 0:
        #     actions += self.get_possible_mouvement(state["robot_pos"])
        #
        # if not state["dirty_cells"] and state["battery_level"] > 0 and state["robot_pos"] != state["base_pos"]:
        #     actions += self.get_possible_mouvement(state["robot_pos"])
        #
        # if not state["dirty_cells"] and state["robot_pos"] == state["base_pos"]:
        #     actions.append("stay")
        #
        # if state["battery_level"] == 0 and state["robot_pos"] != state["base_pos"]:
        #     actions.append("dead")
