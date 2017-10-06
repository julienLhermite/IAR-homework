#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Simulator import Simulator
from State import *
from queue import Queue
import Actions

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
             "base_pos": (0, 0),
             "robot_pos": (1, 0),
             "dirty_cells": [(1, 0)],
             "battery_level": 2
            }
    print_state(GRID_SIZE, state)
    Actions.unload(state)
    print_state(GRID_SIZE, state)

    print(simulator.get_actions(state))

    # a = [0.2, 0.2, 0.2, 0.2, 0.2]
    # d = [0, 0, 0, 0, 0]
    # tirages = 10000000
    # for i in range(tirages):
    #     d[simulator.roll_dice(a)] += 1
    #
    # r = [i/tirages for i in d]
    # print(r)