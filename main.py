#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Simulator import Simulator
from State import *
from queue import Queue
from threading import Thread
import Actions
import copy

# ---------------- Constantes --------------- #
# Système
GRID_SIZE = (3, 3)
MAX_BATTERY_LEVEL = 10
# Proba
MOVING_PROBA = 0.9
CLEANING_PROBA = 0.9
CHARGING_PROBA = 0.9
# Reward
MOVING_REWARD= -5
CLEANING_REWARD = 10
GOAL_REWARD = 100
DEAD_REWARD = -500
CHARGING_REWARD = 1
# ------------------------------------------- #


if __name__ == "__main__":
    # Instantiate Simulator
    simulator = Simulator(grid_size=GRID_SIZE,
                          max_battery_level=MAX_BATTERY_LEVEL,
                          moving_proba=MOVING_PROBA,
                          cleaning_proba=CLEANING_PROBA,
                          charging_proba=CHARGING_PROBA,
                          moving_reward=MOVING_REWARD,
                          cleaning_reward=CLEANING_REWARD,
                          goal_reward=GOAL_REWARD,
                          dead_reward=DEAD_REWARD,
                          charging_reward=CHARGING_REWARD
                           )

    # Instantiate states list

    state = {
             "base_pos": [0, 0],
             "robot_pos": [2, 0],
             "dirty_cells": [[x, y] for x in range(GRID_SIZE[0]) for y in range(GRID_SIZE[1]) if [x, y] != [0, 0]],
             "battery_level": 4
            }
    print_state(GRID_SIZE, state)
    print(simulator.get_actions(state))

    # roll_dice POC
    # a = [0.2, 0.2, 0.2, 0.2, 0.2]
    # d = [0, 0, 0, 0, 0]
    # tirages = 10000000
    # for i in range(tirages):
    #     d[simulator.roll_dice(a)] += 1
    #
    # r = [i/tirages for i in d]
    # print(r)

    queue = Queue(100)
    new_state = Actions.clean(state)
    queue.put(new_state)
    new_state = Actions.move_left(new_state)
    queue.put(new_state)
    new_state = Actions.clean(new_state)
    queue.put(new_state)
    new_state = Actions.move_left(new_state)
    queue.put(new_state)
    new_state = Actions.load(new_state)
    queue.put(new_state)

    # Display POC
    display = Display(queue, GRID_SIZE, MAX_BATTERY_LEVEL, state)
    display.run()

