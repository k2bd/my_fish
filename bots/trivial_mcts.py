#!/usr/bin/env python3

from mcts import mcts

class MctsPlayer:
    def __init__(self, pnum, time_lim_ms=5000):
        self.pnum = pnum
        self.brain = mcts(timeLimit=time_lim_ms-100)

    def get_move(self, initialState):
        initialState.PROTAGONIST = self.pnum
        return self.brain.search(initialState=initialState)