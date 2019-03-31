#!/usr/bin/env python3
import random
import hex_coords

class Player:
    def __init__(self, pnum):
        self.pnum = pnum

    def get_move(self, initialState):
        return

#     def pieces_status(self, initialState):
#         # Work out the pieces which are still competing for tiles
#         competing_for_space = []
#         alone_but_with_space = []
#         for i_piece in range(initialState.pieces_per_player):
#             reachable_tiles, reachable_pieces = initialState.reachable(pnum, i_piece)
#             if any(p.owner != self.pnum for p in reachable_pieces):
#                 competing_for_space.append(i_piece)
#             elif len(reachable_tiles) > 0:
#                 alone_but_with_space.append(i_piece)
#         return competing_for_space, alone_but_with_space
# 
#     def get_sensible_actions(self, initialState):
#         # In order of precedence:
#         #   1) get pieces that are still competing with other teams' pieces for space
#         #   2) pieces that can still move
#         pieces_competing, pieces_alone = self.categorise_pieces(initialState)
# 
#         if len(pieces_competing) > 0:
#             pieces_to_consider = pieces_competing
#         elif len(pieces_alone) > 0:
#             pieces_to_consider = pieces_alone
#         else:
#             # No-one can move
#             return []
# 
#         return initialState.getPossibleActions(pieces_to_consider)
# 
#     def mcts(self, initialState):
# 
#     def greedy(self, depth):
#         
#     def metric_closeness_to_points(self, initialState):
# 
#         
#     def distance(self, start, initialState):
#         n_moves = {start : 0} # Maps tile to number of moves it is away
#         tiles_at_this_distance = set([neighbors_of_tile(start, initialState)])
#         tiles_at_next_distance = set([])
#         i_moves = 1
# 
#         while len(tiles_at_this_distance) > 0:
#             for tile in tiles_at_this_distance:
#                 n_moves[tile] = i_moves
#                 
#             for 
# 
#             i_moves += 1
#             tile = tiles_to_check.pop()
#             checked_tiles.add(tile)
#             for i in range(6):
#                 # Loop over neighboring tiles
#                 neighboring_coords = hex_coords.hex_neighbor(tile.coords, i)
#                 if neighboring_coords not in self.board.keys():
#                     # This coordinate is off the edge of the board
#                     continue
#                 neighboring_tile = self.board[neighboring_coords]
# 
#                 if neighboring_tile in checked_tiles or neighboring_tile in tiles_to_check:
#                     # Ignore tiles we've reached previously
#                     continue
#                 elif neighboring_tile.occupant is not None:
#                     # Don't count tiles that are occupied
#                     reached_pieces.add(neighboring_tile.occupant)
#                 else:
#                     tiles_to_check.add(neighboring_tile)
# 
#         # Don't return my own tile within checked_tiles
#         checked_tiles.remove(piece.tile)
# 
#         return checked_tiles, reached_pieces
#         
# def neighbors_of_tile(hex, initialState)
#     neighbors = []
#     for direction in hexcoords.hex_directions:
#         neighbors.append(hex_neighbor(hex, direction)
#     return [n for n in neighbors if n in initialState.board.keys()]
#     
