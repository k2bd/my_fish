#!/usr/bin/env python3

from gameboard import GameBoard
from hex_coords import Hex

import numpy as np
from math import floor

class PengWin:
    '''Wins at being a penguin.'''
    def __init__(self, pnum, time_lim_ms=5000):
        self.pnum = pnum
        self.time_lim_ms = time_lim_ms
        calc_time_ms = 0.18
        self.depths = [1000000, 1000000] \
                    + [floor(np.log(time_lim_ms/calc_time_ms)/np.log(x)) for x in range(2,100)]

    def get_move(self, initialState):
        net = Netwerk(initialState)
        max_num_neighbours = net.max_num_neighbours()
        depth = self.depths[max_num_neighbours]
        move,_,_ = next_move(net, depth, self.pnum)
        return (move[0].tile.coords, move[1].tile.coords)

class Node:
    '''A network node representing a tile, 
       with links to every tile which is one move away.'''
    def __init__(self,hex,tile):
        self.coord = [hex.q, hex.r, hex.s]
        
        # The original map tile. N.B. this is not updated as Node is updated.
        self.tile = tile
        
        # Neighbours with: [[=q&>r, =r&>s, =s&>q], [=q&<r, =r&<s, =s&<q]].
        self.neighbours = [[[],[],[]],[[],[],[]]]
        
        # Points to the occupant if occupied.
        self.occupant = None
        
        # True if the node is occupied or has been removed.
        self.used = False
    
    def get_neighbours(self):
        output = []
        for half in self.neighbours:
            for line in half:
                for node in line:
                    if node.used:
                        break
                    output.append(node)
        return output
    
    def sort_and_cut(self):
        '''Sort the inline links, and cut at the first impassable link.'''
        for i in range(2):
            for j in range(3):
                self.neighbours[i][j] = sorted(self.neighbours[i][j],
                                               key=lambda x:x.coord[j-1],
                                               reverse=i==1)
                for k,x in enumerate(self.neighbours[i][j]):
                    if (x.tile.occupant is not None) or \
                       (abs(x.coord[j-1]-self.coord[j-1])!=k+1):
                        self.neighbours[i][j] = self.neighbours[i][j][:k]
                        break
    
def link_if_inline(node1,node2):
    '''Check if two nodes are inline, and link them if they are.'''
    for i in range(3):
        if node2.coord[i]==node1.coord[i]:
            if node2.coord[i-1]>node1.coord[i-1]:
                node1.neighbours[0][i].append(node2)
                node2.neighbours[1][i].append(node1)
            else:
                node1.neighbours[1][i].append(node2)
                node2.neighbours[0][i].append(node1)

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
    
    def max_num_neighbours(self):
        return max([len(x.get_neighbours()) for x in self.nodes])

def hex(coord):
    return Hex(coord[0],coord[1],coord[2])

def next_move(net,depth,next_player):
    best_move = None
    best_heuristic = None
    best_score = None
    for piece in net.pieces[next_player]:
        for neighbour in piece.node.get_neighbours():
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
