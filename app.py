#!/usr/bin/env python3

import argparse
import copy
import random
from enum import Enum

import pygame
from pygame.locals import *

import hex_coords
from gameboard import GameBoard
from hex_coords import Layout


class PlayerType(Enum):
    RANDOM = 0
    HUMAN = 1
    TRIVIAL_MCTS = 2
    EBL_MCTS = 3
    K2BD_MCTS = 4
    MJ = 5
    WARIO = 6


class App:
    def __init__(
            self, players, display=True, bot_time_limit_ms=5000,
            disable_time_limit=False, pieces=None, cols=7, rows=17):
        self.display = display

        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 640, 400
        self.bot_time_limit = bot_time_limit_ms
        self.disable_time_limit = disable_time_limit

        self.hex_radius = 20
        self.hex_size = hex_coords.Point(self.hex_radius, self.hex_radius)

        self.piece_radius = 9

        self.layout = Layout(
            hex_coords.layout_flat, self.hex_size, hex_coords.Point(50, 50))

        self.controllers = []
        for i in range(len(players)):
            p = players[i]
            if p == PlayerType.HUMAN:
                self.controllers.append(None)
            elif p == PlayerType.RANDOM:
                from bots.randombot import RandomBot
                self.controllers.append(RandomBot())
            elif p == PlayerType.TRIVIAL_MCTS:
                from bots.trivial_mcts import MctsPlayer
                self.controllers.append(MctsPlayer(i, bot_time_limit_ms))
            elif p == PlayerType.EBL_MCTS:
                import bots.ebl_mcts as ebl_mcts
                self.controllers.append(ebl_mcts.Player(i))
            elif p == PlayerType.K2BD_MCTS:
                from bots.k2bd_mcts import KevBot
                self.controllers.append(KevBot(i, bot_time_limit_ms))
            elif p == PlayerType.MJ:
                from bots.mj import PengWin
                self.controllers.append(PengWin(i, bot_time_limit_ms))
            elif p == PlayerType.WARIO:
                from bots.wariobot import WarioBot
                self.controllers.append(WarioBot(i))

        self.board = GameBoard(
            len(players), pieces=pieces, cols=cols, rows=rows)

        self.pending_action = None

        self.score_pos = (300, 30)
        self.score_spacing = 30

        self.selected_piece = None

    def on_init(self):
        pygame.init()
        pygame.font.init()

        if self.display:
            self._display_surf = pygame.display.set_mode(
                self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
            self._background = pygame.Surface(self._display_surf.get_size())
            self._background.fill((0, 0, 0))

        self._running = True

        self.font = pygame.font.SysFont("arial", 16)

    def on_event(self, event):
        mpos = pygame.mouse.get_pos()
        sel_hex = hex_coords.pixel_to_hex(
            self.layout, hex_coords.Point(mpos[0], mpos[1]))
        selected = hex_coords.hex_round(sel_hex)

        if event.type == pygame.QUIT:
            self._running = False

        if self.controllers[self.board.current_player] is None:
            # Local player
            if (event.type == pygame.MOUSEBUTTONDOWN) \
                    and (self.selected_piece is None) \
                    and pygame.mouse.get_pressed()[0]:
                # Left click when there is no piece selected
                self.selected_piece = None
                if selected in self.board.board.keys():
                    for i in range(self.board.pieces_per_player):
                        player = self.board.players[self.board.current_player]
                        if player.pieces[i].tile.coords == selected:
                            self.selected_piece = player.pieces[i]
                            break
            elif event.type == pygame.MOUSEBUTTONDOWN \
                    and (self.selected_piece is not None) \
                    and any([pygame.mouse.get_pressed()[0],
                             pygame.mouse.get_pressed()[2]]):
                # If we have a piece selected, and we left or right click
                if self.selected_piece is not None:
                    action = (self.selected_piece.tile.coords, selected)
                    if action in self.board.getPossibleActions():
                        self.pending_action = action
                    elif pygame.mouse.get_pressed()[0]:
                        self.selected_piece = None

    def on_loop(self):
        # Player or AI moves
        if self.pending_action is not None:
            self.board = self.board.takeAction(self.pending_action)
            self.selected_piece = None
            self.pending_action = None
        elif self.controllers[self.board.current_player] is not None:
            self.selected_piece = None
            # Pass in a deep copy of the board in case the bot wants to make
            # any changes or monkey patch the reward function
            c_time = pygame.time.get_ticks()
            board = copy.deepcopy(self.board)
            new_board = self.board.takeAction(
                self.controllers[self.board.current_player].get_move(board))
            time_taken = pygame.time.get_ticks() - c_time
            if time_taken <= self.bot_time_limit:
                self.board = new_board
            else:
                msg = "Bot {} took too long by {} ms! Taking random action."
                print(msg.format(
                    self.board.current_player,
                    time_taken - self.bot_time_limit))
                if self.disable_time_limit:
                    self.board = new_board
                else:
                    self.board = self.board.takeAction(
                        random.choice(self.board.getPossibleActions()))

        # Tile Highlighting
        for tile in self.board.board.values():
            tile.highlighted = False
        mpos = pygame.mouse.get_pos()
        selected = hex_coords.hex_round(
            hex_coords.pixel_to_hex(
                self.layout, hex_coords.Point(mpos[0], mpos[1])))
        if selected in self.board.board.keys():
            self.board.board[selected].highlighted = True

        orig_player = self.board.current_player
        while len(self.board.getPossibleActions()) == 0:
            self.board.current_player = (
                self.board.current_player + 1) % self.board.nplayers
            if self.board.current_player == orig_player:
                for i in range(len(self.board.players)):
                    player = self.board.players[i]
                    # Add all the player's current piece tiles to their score
                    for piece in player.pieces:
                        player.points += piece.tile.value
                    print(i, player.points)
                self._running = False
                break

    def on_render(self):
        if not self.display:
            return
        # Clear screen
        self._display_surf.blit(self._background, (0, 0))

        # Draw all tiles
        for tile in self.board.board.values():
            self.draw_hex(tile.color, tile.coords)
            self.draw_hex(pygame.Color(0, 0, 0, 255), tile.coords, width=2)
            if tile.occupant is not None:
                player = tile.occupant.owner
                self.draw_piece(player.color, tile.coords, self.piece_radius)

        # Add selection highlight
        for tile in self.board.board.values():
            if tile.highlighted:
                self.draw_hex(tile.color, tile.coords, width=5)

        # Draw previous move
        if self.board.prev_move is not None:
            self.draw_line(
                self.board.players[self.board.prev_move[0]].color,
                self.board.prev_move[1][0],
                self.board.prev_move[1][1], width=2)

        # Draw a line to valid moves
        for orig, targ in self.board.getPossibleActions():
            if (self.selected_piece is not None) and \
               (self.selected_piece.tile.coords == orig) and \
               (targ in self.board.board.keys()):
                self.draw_line(
                    self.board.players[self.board.current_player].color,
                    orig, targ, width=3)

        # Draw scores
        for i in range(self.board.nplayers):
            player = self.board.players[i]

            pos = (self.score_pos[0], self.score_pos[1] + i*self.score_spacing)

            # Draw a square around it if it's their turn
            if self.board.current_player == i:
                pygame.draw.rect(
                    self._display_surf, pygame.Color(255, 255, 255, 255),
                    pygame.Rect(
                        pos[0] - self.piece_radius-2,
                        pos[1] - self.piece_radius-2,
                        2*self.piece_radius+4,
                        2*self.piece_radius+4), 2)
            # Draw a game piece
            pygame.draw.circle(
                self._display_surf, player.color,
                pos, self.piece_radius)
            # Draw their score
            scoresurf = self.font.render(
                "{}".format(player.points), True, (255, 255, 255))
            self._display_surf.blit(
                scoresurf, (pos[0] + 15, pos[1] - self.piece_radius))

        # Add debug rectangles if we want
        # for orig, targ in self.board.getPossibleActions():
        #     if targ in self.board.board.keys():
        #         self.draw_debug_square(
        #            pygame.Color(0,0,0,255), self.board.board[targ].coords)

        pygame.display.flip()

    def on_cleanup(self):
        self.font = None
        pygame.font.quit()
        pygame.quit()

    def on_execute(self):
        self.on_init()
        self.on_render()
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def draw_hex(self, color, h, width=0):
        return pygame.draw.polygon(
            self._display_surf,
            color,
            [(p.x, p.y) for p in hex_coords.polygon_corners(self.layout, h)],
            width)

    def draw_piece(self, color, h, radius):
        pixel = hex_coords.hex_to_pixel(self.layout, h)
        return pygame.draw.circle(
            self._display_surf,
            color,
            (int(pixel.x), int(pixel.y)),
            radius)

    def draw_debug_square(self, color, h, width=0):
        pixel = hex_coords.hex_to_pixel(self.layout, h)
        return pygame.draw.rect(
            self._display_surf,
            color,
            pygame.Rect(int(pixel.x)-10, int(pixel.y)-10, 10, 10),
            width)

    def draw_line(self, color, o, t, width=1):
        p_o = hex_coords.hex_to_pixel(self.layout, o)
        p_t = hex_coords.hex_to_pixel(self.layout, t)
        return pygame.draw.line(
            self._display_surf,
            color,
            (int(p_o.x), int(p_o.y)), (int(p_t.x), int(p_t.y)),
            width)


if __name__ == "__main__":

    # Set up argparse.
    parser = argparse.ArgumentParser(description='To fish the very best.')
    parser.add_argument('-p',
                        '--players',
                        nargs='+',
                        choices=[x.name.lower() for x in PlayerType],
                        default=['human', 'random'],
                        help='Players.')
    args = parser.parse_args()

    # Parse players and start app.
    players = [PlayerType[x.upper()] for x in args.players]
    theApp = App(players, bot_time_limit_ms=5000)  # , cols=5, rows=5)
    theApp.on_execute()
