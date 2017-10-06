#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from State import State
from Constantes import *

s = State(grid_size=GRID_SIZE, base_pos=(0, 0), robot_pos=(1, 0), dirty_cells=[(1, 0)], battery_level=2)
print(s)

s.clean_cell((1,0))
s.set_battery(1)
s.set_robot_pos((2,0))
print(s)
