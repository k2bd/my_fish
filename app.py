#!/usr/bin/env python3

import pygame
from pygame.locals import *
import math
from gameboard import GameBoard
import hex_coords
from hex_coords import Layout
import random

class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 640, 400

        self.hex_radius = 20
        self.hex_size = hex_coords.Point(self.hex_radius, self.hex_radius)

        self.piece_radius = 9

        self.layout = Layout(hex_coords.layout_flat, self.hex_size, hex_coords.Point(50,50))
        
        self.board = GameBoard(4)

        self.score_pos = (300,30)
        self.score_spacing = 30

        self.selected_piece = None
 
    def on_init(self):
        pygame.init()
        pygame.font.init()
        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._background = pygame.Surface(self._display_surf.get_size())
        self._background.fill((0,0,0))

        self._running = True

        self.font = pygame.font.SysFont("arial", 16)
 
    def on_event(self, event):
        mpos = pygame.mouse.get_pos()
        selected = hex_coords.hex_round(hex_coords.pixel_to_hex(self.layout, hex_coords.Point(mpos[0], mpos[1])))

        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            self.selected_piece = None
            if selected in self.board.board.keys():
                for i in range(self.board.pieces_per_player):
                    if self.board.players[self.board.current_player].pieces[i].pos.coords == selected:
                        self.selected_piece = self.board.players[self.board.current_player].pieces[i]
                        break
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]:
            if self.selected_piece is not None:
                if (self.selected_piece.pos.coords, selected) in self.board.getPossibleActions():
                    self.board = self.board.takeAction((self.selected_piece.pos.coords, selected))
                    self.selected_piece = None
    
    def on_loop(self):
        
        # Tile Highlighting
        for tile in self.board.board.values():
            tile.highlighted = False
        mpos = pygame.mouse.get_pos()
        selected = hex_coords.hex_round(hex_coords.pixel_to_hex(self.layout, hex_coords.Point(mpos[0], mpos[1])))
        if selected in self.board.board.keys():
            self.board.board[selected].highlighted = True

    def on_render(self):
        # Clear screen
        self._display_surf.blit(self._background, (0,0))

        # Draw all tiles
        for tile in self.board.board.values():
            self.draw_hex(tile.color, tile.coords)
            self.draw_hex(pygame.Color(0,0,0,255), tile.coords, width=2)
            if tile.occupant is not None:
                player = tile.occupant.owner
                self.draw_piece(player.color, tile.coords, self.piece_radius)

        # Add selection highlight
        for tile in self.board.board.values():
            if tile.highlighted:
                self.draw_hex(tile.color, tile.coords, width=5)

        # Draw a line to valid moves
        for orig, targ in self.board.getPossibleActions():
            if (self.selected_piece is not None) and \
               (self.selected_piece.pos.coords == orig) and \
               (targ in self.board.board.keys()):
                self.draw_line(self.board.players[self.board.current_player].color, orig, targ, width=3)

        # Draw scores
        for i in range(self.board.nplayers):
            player = self.board.players[i]

            pos = (self.score_pos[0], self.score_pos[1] + i*self.score_spacing)
            
            # Draw a square around it if it's their turn
            if self.board.current_player == i:
                pygame.draw.rect(self._display_surf, pygame.Color(255, 255, 255, 255),
                    pygame.Rect(pos[0] - self.piece_radius-2, pos[1] - self.piece_radius-2, 2*self.piece_radius+4, 2*self.piece_radius+4), 2)
            # Draw a game piece
            pygame.draw.circle(self._display_surf, player.color,
                pos, self.piece_radius)
            # Draw their score
            scoresurf = self.font.render("{}".format(player.points), True, (255,255,255))
            self._display_surf.blit(scoresurf,(pos[0] + 15, pos[1] - self.piece_radius))

        # Add debug rectangles if we want
        #for orig, targ in self.board.getPossibleActions():
        #    if targ in self.board.board.keys():
        #        self.draw_debug_square(pygame.Color(0,0,0,255), self.board.board[targ].coords)

        pygame.display.flip()

    def on_cleanup(self):
        pygame.font.quit()
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def draw_hex(self, color, h, width=0):
        return pygame.draw.polygon(self._display_surf,
            color,
            [(p.x, p.y) for p in hex_coords.polygon_corners(self.layout, h)],
            width)

    def draw_piece(self, color, h, radius):
        pixel = hex_coords.hex_to_pixel(self.layout, h)
        return pygame.draw.circle(self._display_surf,
            color,
            (int(pixel.x), int(pixel.y)),
            radius)

    def draw_debug_square(self, color, h, width=0):
        pixel = hex_coords.hex_to_pixel(self.layout, h)
        return pygame.draw.rect(self._display_surf,
            color,
            pygame.Rect(int(pixel.x)-10, int(pixel.y)-10, 10, 10),
            width)
 
    def draw_line(self, color, o, t, width=1):
        p_o = hex_coords.hex_to_pixel(self.layout, o)
        p_t = hex_coords.hex_to_pixel(self.layout, t)
        return pygame.draw.line(self._display_surf,
            color, 
            (int(p_o.x),int(p_o.y)), (int(p_t.x),int(p_t.y)),
            width)

if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
