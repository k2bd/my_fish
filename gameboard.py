#!/usr/bin/env python3
import sys
import hex_coords
import pygame
import random
from hex_coords import Hex, qoffset_to_cube, OffsetCoord

piece_palette = [
    pygame.Color('0x123ABC'),
    pygame.Color('0xABC123'),
    pygame.Color('0x1A2B3C'),
    pygame.Color('0xC3B2A1'),
]

class GameBoard:
    
    def __init__(self, nplayers):
        self.board = {} # Coords : Tile
        self.offset = hex_coords.ODD

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
        self.current_player = 0

        fish_bank = [30,20,10]

        for col in range(7):
            for row in range(8):
                tile_value = random.randint(0,2)
                while fish_bank[tile_value] == 0:
                    tile_value = random.randint(0,2)
                fish_bank[tile_value] -= 1
                tile_value += 1

                coord = qoffset_to_cube(self.offset, OffsetCoord(col, row))
                self.board[coord] = GameTile(coord, tile_value)

        # Add the end of the board
        for col in range(0,8,2):
            tile_value = random.randint(0,2)
            while fish_bank[tile_value] == 0:
                tile_value = random.randint(0,2)
            fish_bank[tile_value] -= 1
            tile_value += 1
            coord = qoffset_to_cube(hex_coords.EVEN, OffsetCoord(col, 8))
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

        # TEMP:
        print(self.getPossibleActions())

#class GameState:
#    def __init__(self):
#        self.pieces = [] # [(player, coord)]
#        

    # Action is a tuple of (origin, destination)
    def getPossibleActions(self):
        actions = []

        for piece in self.players[self.current_player].pieces:
            tile = piece.pos
            for direction in hex_coords.hex_directions:
                targ = hex_coords.hex_add(direction, tile.coords) 
                while targ in self.board and self.board[targ].occupant is None:
                    actions.append((tile.coords, targ))
                    targ = hex_coords.hex_add(direction, targ)
        
        return actions
    
    def takeAction(self, action):
        if action in self.getPossibleActions():

    
    def isTerminal(self):
        pass
    
    def getReward(self):
        pass

class Player:
    def __init__(self, num): # TODO: controller, etc
        self.points = 0
        self.color = piece_palette[num]
        self.pieces = []

class GamePiece:
    def __init__(self, owner, pos):
        self.owner = owner
        self.pos = pos

class GameTile:

    def __init__(self, coord, value):
        self.value = value
        self.highlighted = False
        self.coords = coord
        self.occupant = None

        if self.value == 1:
            self.color = pygame.Color(255, 0, 0, 255)
        elif self.value == 2:
            self.color = pygame.Color(0, 255, 0, 255)
        elif self.value == 3:
            self.color = pygame.Color(0, 0, 255, 255)

if __name__ == "__main__":
    test_board = GameBoard()
    print(test_board.board)