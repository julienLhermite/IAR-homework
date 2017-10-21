#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import copy
import Actions
from Debug import Debug
from State import print_state

class Simulator:

    def __init__(self, grid_size, max_battery_level, moving_proba, cleaning_proba, charging_proba,
                 moving_reward,goal_reward, dead_reward, charging_reward):
        """
        :param grid_size: un tuple (x,y) représentant la taille de la grille
        :param max_battery_level: 
        :param moving_proba: la probabilité de réussir à bouger dans la direction souhaitée si la case destination est libre
        :param cleaning_proba: la probabilité de réussir à nettoyer la case lors de l'action clean_cell
        :param charging_proba: la probabilité de réussir à charger la batterie 
        :param moving_reward: récompense recue lorsqu'on on fait un mouvement
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
        self.goal_reward = goal_reward
        self.dead_reward = dead_reward
        self.charging_reward = charging_reward

    def roll_dice(self, probabilities):
        """
        Etant donnée une probabilité de succès détermine si l'évenement a lieu
        :param probabilities: une probabilité de succès
        :return: un booléen 
        """
        dice = random.random()
        return dice < probabilities

    def get_actions(self, state, DEBUG=False):
        """
        retourne la liste d'actions possibles étant donné l'état state
        :param state: l'état courant
        :return actions: la liste d'actions possibles 
        """
        actions = []
        if state["robot_pos"] in state["dirty_cells"] and state["battery_level"] > 0:
            actions.append("clean")

        if state["robot_pos"] == state["base_pos"] and state["battery_level"] < self.max_battery_level:
            actions.append("load")

        if state["battery_level"] > 0:
            x, y = state['robot_pos']
            if self.grid_size[0] != 1:
                if x != 0:
                    actions.append("move_left")
                if x != self.grid_size[0] - 1:
                    actions.append("move_right")
            if self.grid_size[1] != 1:
                if y != 0:
                    actions.append("move_up")
                if y != self.grid_size[0] - 1:
                    actions.append("move_down")

        if not state["dirty_cells"] and state["robot_pos"] == state["base_pos"] and state["battery_level"] == self.max_battery_level:
            actions.append("stay")

        if state["battery_level"] == 0 and state["robot_pos"] != state["base_pos"]:
            actions.append("dead")

        DEBUG and Debug(state=state, actions=actions)
        return actions


    def do_action(self, action, state):
        """
        Etant donné une action retourne l'état suivant
        :param action: 
        :param state: 
        :return: 
        """
        if action == "move_up":
            return Actions.move_up(state, self.grid_size)
        elif action == "move_down":
            return Actions.move_down(state, self.grid_size)
        elif action == "move_right":
            return Actions.move_right(state, self.grid_size)
        elif action == "move_left":
            return Actions.move_left(state, self.grid_size)
        elif action == "load":
            return Actions.load(state)
        elif action == "clean":
            return Actions.clean(state)
        elif action == "dead":
            return state
        elif action == "stay":
            return state

    def get_proba(self, action):
        """
        Etant donné une action retourne la probabilité de succès
        :param action: 
        :return: 
        """
        if action == "move_up":
            return self.moving_proba
        elif action == "move_down":
            return self.moving_proba
        elif action == "move_right":
            return self.moving_proba
        elif action == "move_left":
            return self.moving_proba
        elif action == "load":
            return self.charging_proba
        elif action == "clean":
            return self.cleaning_proba
        else:
            return 1

    def get(self, action, state):
        """
        Etant donné une action et un état, retourne l'état suivant et une récompense
        :param action: un string représentant une action 
        :param state: un état du système
        :return state, reward: l'état suivant et une récompense 
        """
        # état dead,  pour tt action --> -100
        # état final pour toute action --> 100
        # tout les autres --> -0.5

        if state["battery_level"] == 0:
            # print("##### dead reward ! #####")
            return self.dead_reward,\
                   state

        proba = self.get_proba(action)
        if not state["dirty_cells"] and state["robot_pos"] == state["base_pos"]:
            # print("##### goal reward ! #####")
            return self.goal_reward,\
                   self.do_action(action, state) if self.roll_dice(proba) else Actions.unload(state)

        if action == "load" or action == "stay":
            return self.charging_reward,\
                   self.do_action(action, state) if self.roll_dice(proba) else state
        else:
            #self.do_action(action, state) if self.roll_dice(proba) else Actions.unload(state)
            return self.moving_reward,\
                   self.do_action(action, state) if self.roll_dice(proba) else Actions.unload(state)

    def get_with_model(self, action, state):
        """
        Etant donné une action et un état, retourne l'état suivant une récompense
        :param action: un string représentant une action 
        :param state: un état du système
        :return reward, [(proba state 1, state1), (proba state2, state 2)]: une récompense et la distribution d'état suivant
        """
        # état dead,  pour tt action --> -100 dead_reward
        # état final pour toute action --> goal_reward
        # tout les autres --> moving_reward

        if state["battery_level"] == 0 and state["robot_pos"] != state["base_pos"]:
            return self.dead_reward,\
                   [(1, state)]

        proba = self.get_proba(action)
        if not state["dirty_cells"] and state["robot_pos"] == state["base_pos"] and state["battery_level"] == self.max_battery_level:
            if proba == 1:
                return self.goal_reward,\
                       [(1, self.do_action(action, state))]
            else:
                return self.goal_reward,\
                       [(proba, self.do_action(action, state)), (1 - proba, Actions.unload(state))]

        if proba == 1:
            return self.moving_reward, \
                   [(1, self.do_action(action, state))]
        else:
            if action == "load":
                return self.charging_reward, \
                       [(proba, self.do_action(action, state)), (1 - proba, state)]
            else:
                return self.moving_reward, \
                       [(proba, self.do_action(action, state)), (1 - proba, Actions.unload(state))]
