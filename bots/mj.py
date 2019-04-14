#!/usr/bin/env python3

from gameboard import GameBoard
from hex_coords import Hex

import random

class PengWin:
    '''Wins at being a penguin.'''
    def __init__(self, pnum, time_lim_ms=5000):
        self.pnum = pnum
        random.seed()

    def get_move(self, initialState):
        net = Netwerk(initialState.board, initialState.players[self.pnum])
        
        best_move = None
        best_score = None
        for minion in net.minions:
            for neighbour in minion.node.neighbours():
                move = (minion.node.tile.coords,
                        neighbour.tile.coords)
                score = neighbour.tile.value
                if best_score is None or score>best_score:
                    best_move = move
                    best_score = score
        print(best_move)
        return best_move

class Node:
    '''A network node representing a tile, 
       with links to every tile which is one move away.'''
    def __init__(self,hex,tile):
        self.id = id
        self.coord = [hex.q, hex.r, hex.s]
        self.tile = tile
        self.plus = [[],[],[]]
        self.minus = [[],[],[]]
        self.occupant = None
    
    def neighbours(self):
        return [x for z in [self.plus,self.minus] for y in z for x in y]
    
    def sort_and_cut(self):
        '''Sort the inline links, and cut at the first impassable link.'''
        for i in range(3):
            self.plus[i] = sorted(self.plus[i],
                                  key=lambda x:x.coord[i-1])
            for j,x in enumerate(self.plus[i]):
                if (x.tile.occupant is not None) or \
                   (x.coord[i-1]!=self.coord[i-1]+j+1):
                    self.plus[i] = self.plus[i][:j]
                    break
            self.minus[i] = sorted(self.minus[i],
                                   key=lambda x:x.coord[i-1],
                                   reverse=True)
            for j,x in enumerate(self.minus[i]):
                if (x.tile.occupant is not None) or \
                   (x.coord[i-1]!=self.coord[i-1]-j-1):
                    self.minus[i] = self.minus[i][:j]
                    break
    
def link_if_inline(node1,node2):
    '''Check if two nodes are inline, and link them if they are.'''
    for i in range(3):
        if node2.coord[i]==node1.coord[i]:
            if node2.coord[i-1]>node1.coord[i-1]:
                node1.plus[i].append(node2)
                node2.minus[i].append(node1)
            else:
                node1.minus[i].append(node2)
                node2.minus[i].append(node1)

class Piece:
    '''Effectively a GamePiece, with reference to a node.'''
    def __init__(self,node,owned,friendly):
        self.node = node
        self.node.occupant = self
        self.owned = owned
        self.friendly = friendly

class Netwerk:
    def __init__(self,board,player):
        self.nodes = [Node(x,y) for x,y in board.items()]
        self.minions = []
        self.friends = []
        self.enemies = []
        for node in self.nodes:
            if node.tile.occupant is not None:
                if node.tile.occupant.owner is player:
                    self.minions.append(Piece(node,True,True))
                else:
                    self.enemies.append(Piece(node,False,False))
        
        for i,node1 in enumerate(self.nodes):
            for node2 in self.nodes[:i]:
                link_if_inline(node1,node2)
        
        for node in self.nodes:
            node.sort_and_cut()

def hex(coord):
    return Hex(coord[0],coord[1],coord[2])
