#!/usr/bin/env python3

from mcts import mcts
from gameboard import GameBoard

def getReward(self):
    if not self.isTerminal():
        return False

    scorediff = min(self.players[self.PROTAGONIST].points - self.players[i].points for i in range(self.nplayers) if i != self.PROTAGONIST)

    return scorediff

class KevBot:
    def __init__(self, pnum, time_lim_ms=5000):
        self.pnum = pnum
        self.brain = mcts(timeLimit=time_lim_ms-100)

    def get_move(self, initialState):
        initialState.PROTAGONIST = self.pnum
        initialState.getReward = getReward.__get__(initialState, GameBoard)
        return self.brain.search(initialState=initialState)