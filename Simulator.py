#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import random
import copy
import Actions

class Simulator:

    def __init__(self, grid_size, max_battery_level, moving_proba, cleaning_proba, charging_proba,
                 moving_reward, cleaning_reward, goal_reward, dead_reward, charging_reward, bumping_reward,
                 moving_to_dirty_reward):
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
        :param bumping_reward: récompense recue lors d'une collision
        :param moving_to_dirty_reward: récompense recue lorsqu'on a une dirty cell dans le scope
        """
        self.max_battery_level = max_battery_level
        self.grid_size = grid_size
        self.moving_proba = moving_proba
        self.cleaning_proba = cleaning_proba
        self.charging_proba = charging_proba
        self.moving_reward = moving_reward
        self.moving_to_dirty_reward = moving_to_dirty_reward
        self.cleaning_reward = cleaning_reward
        self.goal_reward = goal_reward
        self.dead_reward = dead_reward
        self.charging_reward = charging_reward
        self.bumping_reward = bumping_reward

    def roll_dice(self, probabilities):
        """
        Etant donnée une probabilité de succès détermine si l'évenement a lieu
        :param probabilities: une probabilité de succès
        :return: un booléen 
        """
        dice = random.random()
        return dice < probabilities

    def get_actions(self, state):
        """
        retourne la liste d'actions possibles étant donné l'état state
        :param state: l'état courant
        :return actions: la liste d'actions possibles 
        """
        actions = list()

        if state["robot_pos"] in state["dirty_cells"] and state["battery_level"] > 0:
            actions.append("clean")

        if state["robot_pos"] == state["base_pos"] and state["battery_level"] < self.max_battery_level:
            actions.append("load")

        if state["battery_level"] > 0:
            actions += ["move_up", "move_down", "move_right", "move_left"]

        if not state["dirty_cells"] and state["robot_pos"] == state["base_pos"] and state["battery_level"] == self.max_battery_level:
            actions.append("stay")

        if state["battery_level"] == 0 and state["robot_pos"] != state["base_pos"]:
            actions.append("dead")

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
            return self.dead_reward,\
                   state

        proba = self.get_proba(action)
        if not state["dirty_cells"] and state["robot_pos"] == state["base_pos"]:
            return self.goal_reward,\
                   self.do_action(action, state) if self.roll_dice(proba) else Actions.unload(state)

        return self.moving_reward,\
               self.do_action(action, state) if self.roll_dice(proba) else Actions.unload(state)


        # if action == "clean":
        #     # si j'ai nettoyé
        #     if self.roll_dice(self.cleaning_proba):
        #         new_state = Actions.clean(state)
        #         return new_state, self.cleaning_reward
        #     # si j'ai pas réussi à nettoyer
        #     else:
        #         new_state = Actions.unload(state)
        #         return new_state, self.cleaning_reward
        #
        # if action == "load":
        #     # si j'ai chargé
        #     if self.roll_dice(self.charging_proba):
        #         new_state = Actions.load(state)
        #         return new_state, self.charging_reward
        #     # si j'ai par réussi à recharger
        #     else:
        #         return state, self.charging_reward
        #
        # if action == "move_up":
        #     if state["robot_pos"][1] == 0:
        #         return Actions.unload(state), self.bumping_reward
        #     else:
        #
        #         if state["robot_pos"][0] in [pos[0] for pos in state["dirty_cells"]]:
        #             return Actions.move_up(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_to_dirty_reward
        #         else:
        #             return Actions.move_up(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_reward
        #
        # if action == "move_down":
        #     if state["robot_pos"][1] == self.grid_size[1] - 1:
        #         return Actions.unload(state), self.bumping_reward
        #     else:
        #
        #         if state["robot_pos"][0] in [pos[0] for pos in state["dirty_cells"]]:
        #             return Actions.move_down(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_to_dirty_reward
        #         else:
        #             return Actions.move_down(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_reward
        #
        # if action == "move_right":
        #     if state["robot_pos"][0] == self.grid_size[0] - 1:
        #         return Actions.unload(state), self.bumping_reward
        #     else:
        #
        #         if state["robot_pos"][1] in [pos[1] for pos in state["dirty_cells"]]:
        #             return Actions.move_right(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_to_dirty_reward
        #         else:
        #             return Actions.move_right(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_reward
        #
        # if action == "move_left":
        #     if state["robot_pos"][0] == 0:
        #         return Actions.unload(state), self.bumping_reward
        #     else:
        #
        #         if state["robot_pos"][1] in [pos[1] for pos in state["dirty_cells"]]:
        #             return Actions.move_left(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_to_dirty_reward
        #         else:
        #             return Actions.move_left(state, self.grid_size) if self.roll_dice(self.moving_proba) else Actions.unload(state),\
        #                    self.moving_reward
        #
        # if action == "stay":
        #     return state, self.goal_reward
        #
        # if action == "dead":
        #     return state, self.dead_reward

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
        if state["battery_level"] == 0:
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
            return self.moving_reward, \
                   [(proba, self.do_action(action, state)), (1 - proba, Actions.unload(state))]
        #
        #
        #
        # if action == "clean":
        #     return self.cleaning_reward,\
        #            [(self.charging_proba, Actions.clean(state)), (1 - self.charging_proba, Actions.unload(state))]
        #
        # if action == "load":
        #     return self.charging_reward,\
        #            [(self.charging_proba, Actions.load(state)), (1 - self.charging_proba, state)]
        #
        # if action == "move_up":
        #     if state["robot_pos"][1] == 0:
        #         return self.bumping_reward, \
        #                [(self.moving_proba, Actions.unload(state)), (1 - self.moving_proba, Actions.unload(state))]
        #     else:
        #         if state["robot_pos"][0] in [pos[0] for pos in state["dirty_cells"]]:
        #             return self.moving_to_dirty_reward, \
        #                    [(self.moving_proba, Actions.move_up(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #         else:
        #             return self.moving_reward, \
        #                    [(self.moving_proba, Actions.move_up(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #
        # if action == "move_down":
        #     if state["robot_pos"][1] == self.grid_size[1] - 1:
        #         return self.bumping_reward, \
        #                [(self.moving_proba, Actions.unload(state)), (1 - self.moving_proba, Actions.unload(state))]
        #     else:
        #         if state["robot_pos"][0] in [pos[0] for pos in state["dirty_cells"]]:
        #             return self.moving_to_dirty_reward, \
        #                    [(self.moving_proba, Actions.move_down(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #         else:
        #             return self.moving_reward, \
        #                    [(self.moving_proba, Actions.move_down(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #
        # if action == "move_left":
        #     if state["robot_pos"][0] == 0:
        #         return self.bumping_reward, \
        #                [(self.moving_proba, Actions.unload(state)), (1 - self.moving_proba, Actions.unload(state))]
        #     else:
        #         if state["robot_pos"][1] in [pos[1] for pos in state["dirty_cells"]]:
        #             return self.moving_to_dirty_reward, \
        #                    [(self.moving_proba, Actions.move_left(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #         else:
        #             return self.moving_reward, \
        #                    [(self.moving_proba, Actions.move_left(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #
        # if action == "move_right":
        #     if state["robot_pos"][0] == self.grid_size[0] - 1:
        #         return self.bumping_reward, \
        #                [(self.moving_proba, Actions.unload(state)), (1 - self.moving_proba, Actions.unload(state))]
        #     else:
        #         if state["robot_pos"][1] in [pos[1] for pos in state["dirty_cells"]]:
        #             return self.moving_to_dirty_reward, \
        #                    [(self.moving_proba, Actions.move_right(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #         else:
        #             return self.moving_reward, \
        #                    [(self.moving_proba, Actions.move_right(state, self.grid_size)), (1 - self.moving_proba, Actions.unload(state))]
        #
        # if action == "stay":
        #     return self.goal_reward, [(1, state)]
        #
        # if action == "dead":
        #     return self.dead_reward, [(1, state)]