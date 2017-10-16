#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from Simulator import Simulator
from State import *
from utilities import *
import sys

# ---------------- Constantes --------------- #
# Système
GRID_SIZE = (2, 2)
MAX_BATTERY_LEVEL = 10
T = GRID_SIZE[0] * GRID_SIZE[1] * 4
TIME_LIMIT = 300  # en seconde
ALPHA = 0.01
EPSILON = 0.3
GAMMA = 0.95
# Proba
MOVING_PROBA = 1
CLEANING_PROBA = 1
CHARGING_PROBA = 1
# Reward
MOVING_REWARD = -5
GOAL_REWARD = 500
DEAD_REWARD = -100
CHARGING_REWARD = 0
# ------------------------------------------- #


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Vous devez passez en argument la méthode d'optimisation de votre choix:\n" +
              "./main.py dynamic_programming\n" +
              "./main.py monte_carlo\n" +
              "./main.py q_learning")
        sys.exit(-1)

    # Instantiate Simulator
    simulator = Simulator(grid_size=GRID_SIZE,
                          max_battery_level=MAX_BATTERY_LEVEL,
                          moving_proba=MOVING_PROBA,
                          cleaning_proba=CLEANING_PROBA,
                          charging_proba=CHARGING_PROBA,
                          moving_reward=MOVING_REWARD,
                          goal_reward=GOAL_REWARD,
                          dead_reward=DEAD_REWARD,
                          charging_reward=CHARGING_REWARD,
                          )

    # Instantiate states list
    all_states = get_all_states(MAX_BATTERY_LEVEL, GRID_SIZE)
    print("nombre d'états:", len(all_states))
    print("Time limit:", TIME_LIMIT)
    print("T:", T)

    initial_state = {
        "base_pos": [0, 0],
        "robot_pos": [0, 0],
        "dirty_cells": [[x, y] for x in range(GRID_SIZE[0]) for y in range(GRID_SIZE[1]) if [x, y] != [0, 0]],
        "battery_level": MAX_BATTERY_LEVEL
    }

    # Algo d'optimisation
    if sys.argv[1] == "dynamic_programming":
        title = "DP"
        policy = dynamic_programming(all_states, simulator, GAMMA, EPSILON)
        # policy = our_dynamic_programming(all_states, simulator, T)
    elif sys.argv[1] == "q_learning":
        #policy = our_q_learning(all_states, simulator, T, TIME_LIMIT, ALPHA,)
        title = "QL -> T: " + str(T) + ", time_limit: " + str(TIME_LIMIT)
        policy = q_learning(all_states, initial_state, simulator, TIME_LIMIT, GAMMA, EPSILON, ALPHA)
    elif sys.argv[1] == "monte_carlo":
        title = "MC -> T: " + str(T) + ", time_limit: " + str(TIME_LIMIT)
        policy = monte_carlo(all_states, simulator, TIME_LIMIT, T, GAMMA, EPSILON, ALPHA, initial_state)
    else:
        print("Argument invalide")
        sys.exit(-1)

    # Display
    display = Display(simulator, policy, GRID_SIZE, MAX_BATTERY_LEVEL, initial_state, title)
    display.run()
