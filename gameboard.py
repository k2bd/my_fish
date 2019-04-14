#!/usr/bin/env python3
import sys
import hex_coords
import pygame
import random
from hex_coords import Hex, qoffset_to_cube, OffsetCoord
import copy

piece_palette = [
    pygame.Color('0x123ABC'),
    pygame.Color('0xABC123'),
    pygame.Color('0x1A2B3C'),
    pygame.Color('0xC3B2A1'),
]

tile_palette = [
    pygame.Color('0x2A3026'),
    pygame.Color('0xA3506E'),
    pygame.Color('0xBE783C'),
]

class GameBoard:
    def __init__(self, nplayers, cols=7, rows=17):
        self.board = {} # Coords : Tile
        self.offset = hex_coords.ODD

        self.cols = cols
        self.rows = rows

        self.prev_move = None

        self.nplayers = nplayers
        if self.nplayers == 2:
            self.pieces_per_player = 4
        elif self.nplayers == 3:
            self.pieces_per_player = 3
        elif self.nplayers == 4:
            self.pieces_per_player = 2
        else:
            sys.exit("Invalid # of players!")
        
        self.players = [Player(i) for i in range(nplayers)]
        self.current_player = random.randint(0, nplayers-1)

        self.PROTAGONIST = None # N.B. this is not used for game simulation, but is used in the reward function

        #fish_bank = [30,20,10]
        total_fish = ((rows//2) * cols) + ((rows % 2) * (cols//2 + 1))

        fish_bank = [0, total_fish//3, total_fish//6]
        fish_bank[0] = total_fish - sum(fish_bank)

        print("Setting up game with {} fish distributed as {}".format(total_fish, fish_bank))

        for col in range(cols):
            for row in range(rows//2):
                tile_value = random.randint(0,2)
                while fish_bank[tile_value] == 0:
                    tile_value = random.randint(0,2)
                fish_bank[tile_value] -= 1
                tile_value += 1

                coord = qoffset_to_cube(self.offset, OffsetCoord(col, row))
                self.board[coord] = GameTile(coord, tile_value)

        # Add the end of the board
        if rows % 2 == 1:
            for col in range(0,cols,2):
                tile_value = random.randint(0,2)
                while fish_bank[tile_value] == 0:
                    tile_value = random.randint(0,2)
                fish_bank[tile_value] -= 1
                tile_value += 1
                coord = qoffset_to_cube(hex_coords.EVEN, OffsetCoord(col, rows//2))
                self.board[coord] = GameTile(coord, tile_value)

        assert all(fish_bank[i] == 0 for i in range(len(fish_bank)))

        # Player piece placement, for now randomize
        for player in self.players:
            for _ in range(self.pieces_per_player):
                target = random.choice(list(self.board.values()))
                while target.occupant is not None:
                    target = random.choice(list(self.board.values()))
                piece = GamePiece(player, target)

                # N.B. store the same piece in two places, make sure to keep this consistent
                target.occupant = piece
                player.pieces.append(piece)

    # Action is a tuple of (origin, destination)
    def getPossibleActions(self, objects_to_consider = None):
        # objects_to_consider can be pieces, tiles, or coordinates

        if not isinstance(objects_to_consider, list):
            objects_to_consider = [objects_to_consider]

        if objects_to_consider[0] == None:
            # Default: run over current player's pieces
            coords_to_consider = [p.tile.coords for p in self.players[self.current_player].pieces]
        elif objects_to_consider[0].__str__().startswith("Hex"):
            pass
        elif isinstance(objects_to_consider[0], GameTile):
            coords_to_consider = [t.coords for t in objects_to_consider]
        elif isinstance(objects_to_consider[0], GamePiece):
            coords_to_consider = [p.tile.coords for p in objects_to_consider]
        else:
            raise ValueError("Did not recognised format of argument to gameboard.getPossibleActions")

        actions = []

        for coord in coords_to_consider:
            for direction in hex_coords.hex_directions:
                targ = hex_coords.hex_add(direction, coord) 
                while targ in self.board and self.board[targ].occupant is None:
                    actions.append((coord, targ))
                    targ = hex_coords.hex_add(direction, targ)
        
        return actions
    
    def takeAction(self, action):
        if action in self.getPossibleActions():
            dup = copy.deepcopy(self)
            orig, targ = action

            dup.players[dup.current_player].points += dup.board[orig].value
            dup.prev_move = (dup.current_player, (orig, targ))
            for piece in dup.players[dup.current_player].pieces:
                if piece.tile.coords == orig:
                    piece.tile = dup.board[targ]
                    dup.board[targ].occupant = piece
                    break
            else:
                sys.exit("Can't find current player's moved piece")
            
            _ = dup.board.pop(orig)
            dup.current_player = (dup.current_player + 1) % dup.nplayers

            return dup
        else:
            print("Invalid Move!")
            return self

    def isTerminal(self):
        if len(self.getPossibleActions()) == 0:
            return True
        else:
            return False
    
    def getReward(self):
        if not self.isTerminal():
            return False
        
        if all(self.players[self.PROTAGONIST].points > self.players[i].points for i in range(self.nplayers) if i != self.PROTAGONIST):
            return 1
        else:
            return -1

    def reachable(self, i_player, i_piece):
        # Finds the tiles and other pieces that are on the same "island" of tiles as this one
        piece = self.players[i_player].pieces[i_piece]

        tiles_to_check = set([piece.tile])
        checked_tiles = set([])
        reached_pieces = set([])

        while len(tiles_to_check) > 0:
            tile = tiles_to_check.pop()
            checked_tiles.add(tile)
            for i in range(6):
                # Loop over neighboring tiles
                neighboring_coords = hex_coords.hex_neighbor(tile.coords, i)
                if neighboring_coords not in self.board.keys():
                    # This coordinate is off the edge of the board
                    continue
                neighboring_tile = self.board[neighboring_coords]

                if neighboring_tile in checked_tiles or neighboring_tile in tiles_to_check:
                    # Ignore tiles we've reached previously
                    continue
                elif neighboring_tile.occupant is not None:
                    # Don't count tiles that are occupied
                    reached_pieces.add(neighboring_tile.occupant)
                else:
                    tiles_to_check.add(neighboring_tile)

        # Don't return my own tile within checked_tiles
        checked_tiles.remove(piece.tile)

        return checked_tiles, reached_pieces

class Player:
    def __init__(self, num): # TODO: controller, etc
        self.points = 0
        self.color = piece_palette[num]
        self.pieces = []

class GamePiece:
    def __init__(self, owner, tile):
        self.owner = owner
        self.tile = tile

class GameTile:

    def __init__(self, coord, value):
        self.value = value
        self.highlighted = False
        self.coords = coord
        self.occupant = None

        self.color = tile_palette[value-1]

if __name__ == "__main__":
    test_board = GameBoard()
    print(test_board.board)
