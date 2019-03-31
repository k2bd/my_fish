#!/usr/bin/env python3

import hex_coords

class Player:
    def __init__(self, pnum):
        self.pnum = pnum

    def get_move(self, initialState):

        orig = hex_coords.Hex(0, 0, 0)
        dest = hex_coords.Hex(0, 0, 0)
