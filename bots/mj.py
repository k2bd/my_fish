#!/usr/bin/env python3

from gameboard import GameBoard
from hex_coords import Hex

import random
from copy import deepcopy

class PengWin:
    '''Wins at being a penguin.'''
    def __init__(self, pnum, time_lim_ms=5000):
        self.pnum = pnum
        random.seed()

    def get_move(self, initialState):
        net = Netwerk(initialState)
        move,_,_ = next_move(net, 3, self.pnum)
        return (move[0].tile.coords, move[1].tile.coords)

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
        self.used = False
    
    def neighbours(self):
        output = []
        for i in range(3):
            for node in self.plus[i]:
                if node.used:
                    break
                output.append(node)
            for node in self.minus[i]:
                if node.used:
                    break
                output.append(node)
        return output
    
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
                node2.plus[i].append(node1)

class Piece:
    '''Effectively a GamePiece, with reference to a node.'''
    def __init__(self,player_id,node):
        self.player_id = player_id
        self.node = node
        self.node.occupant = self
        self.node.used = True

class Netwerk:
    def __init__(self,state):
        self.nodes = [Node(x,y) for x,y in state.board.items()]
        self.pieces = [[] for _ in state.players]
        for node in self.nodes:
            if node.tile.occupant is not None:
                player_id = state.players.index(node.tile.occupant.owner)
                self.pieces[player_id].append(Piece(player_id,node))
        
        for i,node1 in enumerate(self.nodes):
            for node2 in self.nodes[:i]:
                link_if_inline(node1,node2)
        
        for node in self.nodes:
            node.sort_and_cut()
    
    def make_move(self,move):
        move[1].occupant = move[0].occupant
        move[0].occupant = None
        move[1].occupant.node = move[1]
        move[1].used = True
    
    def unmake_move(self,move):
        move[0].occupant = move[1].occupant
        move[1].occupant = None
        move[0].occupant.node = move[0]
        move[1].used = False

def hex(coord):
    return Hex(coord[0],coord[1],coord[2])

def next_move(net,depth,next_player):
    best_move = None
    best_heuristic = None
    best_score = None
    for piece in net.pieces[next_player]:
        for neighbour in piece.node.neighbours():
            move = (piece.node, neighbour)
            net.make_move(move)
            heuristic = get_heuristic(net, depth-1, next_player)
            net.unmake_move(move)
            heuristic[next_player] += neighbour.tile.value
            score = get_score(heuristic, next_player)
            if best_score is None or score>best_score:
                best_move = move
                best_heuristic = heuristic
                best_score = score
    return best_move, best_heuristic, best_score

def get_heuristic(net,depth,next_player):
    if depth>0:
        _, heuristic, _ = next_move(net,depth,(next_player+1)%len(net.pieces))
        if heuristic is not None:
            return heuristic
    return [0 for _ in net.pieces]

def get_score(heuristic,player):
    return 2*heuristic[player] - sum(heuristic)
