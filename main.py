#!/usr/bin/env python3.9
import logging
import random
import sys

import pygame
from pygame.locals import *

SCREEN_WIDTH = SCREEN_HEIGHT = 100*8

TILE_SIZE = SCREEN_HEIGHT // 8

# colours
BLACK = pygame.color.Color((0, 0, 0))

GREY1 = pygame.color.Color((100, 100, 100))

WHITE = pygame.color.Color((255, 255, 255))

COLOURS = (WHITE, GREY1)

ARGS = sys.argv
REVERSE = True if 'reverse' in ARGS else False
ESCAPING = True if 'escape' in ARGS else False
INF = True if 'inf' in ARGS else False
RANDOMISE = True if 'rand' in ARGS else False


class VoidList(list):
    def __init__(self, seq=()):
        super(VoidList, self).__init__(seq)

    def __getitem__(self, item):
        if 0 <= item < len(self):
            return list.__getitem__(self, item)
        else:
            return VoidEntity()

    def __setitem__(self, key, value):
        if 0 <= key < len(self):
            list.__setitem__(self, key, value)
        else:
            pass


class VoidEntity:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return VoidEntity()

    def __getattribute__(self, item):
        return VoidEntity()

    def __setattr__(self, key, value):
        pass

    def __getitem__(self, item):
        return VoidEntity()

    def __setitem__(self, key, value):
        pass

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return False


class Board:
    def __init__(self):
        self.tiles = VoidList((
            VoidList(([Rook(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), Rook(0)])),
            VoidList(([Knight(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), Knight(0)])),
            VoidList(([Bishop(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), Bishop(0)])),
            VoidList(([Queen(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), Queen(0)])),
            VoidList(([King(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), King(0)])),
            VoidList(([Bishop(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), Bishop(0)])),
            VoidList(([Knight(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), Knight(0)])),
            VoidList(([Rook(1), Pawn(1), NoPiece(), NoPiece(), NoPiece(), NoPiece(), Pawn(0), Rook(0)]))
        ))
        if RANDOMISE:
            random.shuffle(self.tiles)
            for v in self.tiles:
                random.shuffle(v)
        self.bin = []
        self.kings = [(7, 4), (0, 4)]
        self.assign_pos()
        self.selected = NoPiece()
        self.player = 0
        # self.kings = [(7, 4), (0, 4)]

    def assign_pos(self):

        for i in range(64):
            if isinstance(self.tiles[i // 8][i % 8], King):
                self.kings[self.tiles[i // 8][i % 8].player] = (i // 8, i % 8)
            self.tiles[i // 8][i % 8].pos = (i // 8, i % 8)

    def reverse(self):
        for v in self.tiles:
            v.reverse()
        self.tiles.reverse()
        for v in self.tiles:
            for w in v:
                w.reversed = not w.reversed
        self.assign_pos()

    def draw(self, surface):
        for rank in range(8):
            for file in range(8):
                colour = COLOURS[((rank % 2) + file) % 2]
                pygame.draw.rect(surface, colour, (rank * TILE_SIZE, file * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        for v in self.tiles:
            for w in v:
                w.draw(surface)

    def select(self, pos):
        x, y = pos
        tile = self.tiles[x][y]
        if isinstance(tile, NoPiece) and isinstance(self.selected, NoPiece):
            pass
        elif isinstance(tile, NoPiece) or (tile.player != self.player and not isinstance(self.selected, NoPiece)):
            ability = 0
            if (x, y) in self.selected.get_free_moves(self.tiles):
                ability = 1
            if (x, y) in self.selected.get_take_moves(self.tiles):
                ability = 2
            # ability = self.selected.get_valid_moves(self.selected.pos, (x, y), self.tiles)  # ability is it's ability to move
            if ability == 2:
                logging.info("taking piece")
                self.bin.append(self.tiles[x][y])
                self.tiles[x][y] = NoPiece()
            if ability != 0:
                self.tiles[self.selected.pos[0]][self.selected.pos[1]].new = False
                self.tiles[self.selected.pos[0]][self.selected.pos[1]], self.tiles[x][y] = \
                    self.tiles[x][y], self.tiles[self.selected.pos[0]][self.selected.pos[1]]
                if REVERSE:
                    self.reverse()

                self.assign_pos()
                self.selected.selected = False
                self.selected = NoPiece()
                if not INF:
                    self.player = int(not self.player)

                for n in self.tiles:
                    for m in n:

                        if self.kings[self.player] in m.get_take_moves(self.tiles):
                            print(f"{'dark' if self.player else 'light'} is in check")

        elif tile.player != self.player and isinstance(self.selected, NoPiece):
            pass
        elif self.selected is tile:
            self.selected.selected = False
            self.selected = NoPiece()
        else:
            self.selected.selected = False
            self.selected = tile
            self.selected.selected = True


class Piece:
    """do not call, inherit only"""

    def __init__(self, player, image_direct=None, pos=None):
        self.player = player  # player = {0: 'white', 1: 'black'}
        if image_direct is not None:
            img = pygame.image.load(image_direct)
            img = pygame.transform.scale(img, (60, 60))
            self.image = img
        self.rel_pos = 0
        self.selected = False
        self.pos = pos
        self.new = True
        self.reversed = False

    def draw(self, surface):
        if not isinstance(self, NoPiece):
            rect = self.image.get_rect()
            rect.center = tuple(i * TILE_SIZE + TILE_SIZE//2 for i in self.pos)
            rect.move_ip(-rect.width//2, -rect.height//2)
            if self.selected:
                rect.move_ip(0, -25)

            surface.blit(self.image, rect.center)

    def get_valid_moves(self, tiles, o):
        """{cannot move: 0, move: 1, take: 2}"""
        return []

    def direction(self, num):
        r = 1
        if self.player == 0:
            r *= -1
        if self.reversed:
            r *= -1
        return r * num

    def get_free_moves(self, tiles):
        """returns all valid moves where it does not take a piece"""
        return self.get_valid_moves(tiles, 0)

    def get_take_moves(self, tiles):
        """returns all moves that end in a taking"""
        return self.get_valid_moves(tiles, 1)


class NoPiece(Piece):
    def __init__(self):
        super(NoPiece, self).__init__(-1)


class Pawn(Piece):
    def __init__(self, player):
        super().__init__(player, f"images/pawn{player}.png")

    def get_valid_moves(self, tiles, o):
        x, y = self.pos
        valid_list = []
        take_list = []
        if tiles[x][y+self.direction(1)].player == -1:
            valid_list.append((x, y+self.direction(1)))
        if self.new and tiles[x][y+self.direction(1)].player == -1 and tiles[x][y+self.direction(2)].player == -1:
            valid_list.append((x, y+self.direction(2)))
        if tiles[x-1][y+self.direction(1)].player == (not self.player):
            take_list.append((x-1, y+self.direction(1)))
        if tiles[x+1][y+self.direction(1)].player == (not self.player):
            take_list.append((x+1, y+self.direction(1)))

        return valid_list if o == 0 else take_list


class Rook(Piece):
    def __init__(self, player):
        super().__init__(player, f"images/rook{player}.png")

    def get_valid_moves(self, tiles, o):
        """{cannot move: 0, move: 1, take: 2}"""
        x, y = self.pos
        valid_list = []
        take_list = []
        for loop in range(y, 0, -1):  # up
            if tiles[x][loop-1].player == -1:
                valid_list.append((x, loop-1))
            elif tiles[x][loop-1].player != self.player:
                take_list.append((x, loop-1))
                break
            else:
                break
        for loop in range(x, 0, -1):  # right
            if tiles[loop-1][y].player == -1:
                valid_list.append((loop-1, y))
            elif tiles[loop-1][y].player != self.player:
                take_list.append((loop-1, y))
                break
            else:
                break
        for loop in range(y, 7):  # down
            if tiles[x][loop+1].player == -1:
                valid_list.append((x, loop+1))
            elif tiles[x][loop+1].player != self.player:
                take_list.append((x, loop+1))
                break
            else:
                break
        for loop in range(x, 7):  # left
            if tiles[loop+1][y].player == -1:
                valid_list.append((loop+1, y))
            elif tiles[loop+1][y].player != self.player:
                take_list.append((loop+1, y))
                break
            else:
                break

        return valid_list if o == 0 else take_list


class Knight(Piece):
    def __init__(self, player):
        super().__init__(player, f"images/knight{player}.png")

    def get_valid_moves(self, tiles, o):
        x, y = self.pos
        valid_list = []
        take_list = []
        options = [(1, 2), (-1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, 1), (-2, -1)]
        for m, n in options:
            if isinstance(tiles[x+m][y+n], NoPiece):
                valid_list.append((x+m, y+n))
            elif tiles[x+m][y+n].player != self.player:
                take_list.append((x+m, y+n))

        return valid_list if o == 0 else take_list


class Bishop(Piece):
    def __init__(self, player):
        super().__init__(player, f"images/bishop{player}.png")

    def get_valid_moves(self, tiles, o):
        x, y = self.pos
        valid_list = []
        take_list = []

        for loop in range(1, 8):  # left-up
            if tiles[x-loop][y-loop].player == -1:
                valid_list.append((x-loop, y-loop))
            elif tiles[x-loop][y-loop].player != self.player:
                take_list.append((x-loop, y-loop))
                break
            else:
                break

        for loop in range(1, 8):  # left-up
            if tiles[x+loop][y-loop].player == -1:
                valid_list.append((x+loop, y-loop))
            elif tiles[x+loop][y-loop].player != self.player:
                take_list.append((x+loop, y-loop))
                break
            else:
                break

        for loop in range(1, 8):
            if tiles[x-loop][y+loop].player == -1:
                valid_list.append((x-loop, y+loop))
            elif tiles[x-loop][y+loop].player != self.player:
                take_list.append((x-loop, y+loop))
                break
            else:
                break

        for loop in range(1, 8):
            if tiles[x+loop][y+loop].player == -1:
                valid_list.append((x+loop, y+loop))
            elif tiles[x+loop][y+loop].player != self.player:
                take_list.append((x+loop, y+loop))
                break
            else:
                break

        return valid_list if o == 0 else take_list


class Queen(Piece):
    def __init__(self, player):
        super().__init__(player, f"images/queen{player}.png")

    def get_valid_moves(self, tiles, o):
        x, y = self.pos
        valid_list = []
        take_list = []

        for loop in range(1, 8):  # left-up
            if tiles[x-loop][y-loop].player == -1:
                valid_list.append((x-loop, y-loop))
            elif tiles[x-loop][y-loop].player != self.player:
                take_list.append((x-loop, y-loop))
                break
            else:
                break

        for loop in range(1, 8):  # left-up
            if tiles[x+loop][y-loop].player == -1:
                valid_list.append((x+loop, y-loop))
            elif tiles[x+loop][y-loop].player != self.player:
                take_list.append((x+loop, y-loop))
                break
            else:
                break

        for loop in range(1, 8):
            if tiles[x-loop][y+loop].player == -1:
                valid_list.append((x-loop, y+loop))
            elif tiles[x-loop][y+loop].player != self.player:
                take_list.append((x-loop, y+loop))
                break
            else:
                break

        for loop in range(1, 8):
            if tiles[x+loop][y+loop].player == -1:
                valid_list.append((x+loop, y+loop))
            elif tiles[x+loop][y+loop].player != self.player:
                take_list.append((x+loop, y+loop))
                break
            else:
                break

        for loop in range(y, 0, -1):  # up
            if tiles[x][loop-1].player == -1:
                valid_list.append((x, loop-1))
            elif tiles[x][loop-1].player != self.player:
                take_list.append((x, loop-1))
                break
            else:
                break
        for loop in range(x, 0, -1):  # right
            if tiles[loop-1][y].player == -1:
                valid_list.append((loop-1, y))
            elif tiles[loop-1][y].player != self.player:
                take_list.append((loop-1, y))
                break
            else:
                break
        for loop in range(y, 7):  # down
            if tiles[x][loop+1].player == -1:
                valid_list.append((x, loop+1))
            elif tiles[x][loop+1].player != self.player:
                take_list.append((x, loop+1))
                break
            else:
                break
        for loop in range(x, 7):  # left
            if tiles[loop+1][y].player == -1:
                valid_list.append((loop+1, y))
            elif tiles[loop+1][y].player != self.player:
                take_list.append((loop+1, y))
                break
            else:
                break

        return valid_list if o == 0 else take_list


class King(Piece):
    def __init__(self, player):
        super().__init__(player, f"images/king{player}.png")

    def get_valid_moves(self, tiles, o):
        x, y = self.pos
        valid_list = []
        take_list = []
        options = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for m, n in options:
            if isinstance(tiles[x+m][y+n], NoPiece):
                valid_list.append((x+m, y+n))
            if tiles[x+m][y+n].player != self.player:
                take_list.append((x+m, y+n))

        return valid_list if o == 0 else take_list


def convert_to_cn(pos):
    x_dict = {0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8'}
    y_dict = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}


def main():
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("chess")
    board = Board()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                x, y = int(x / TILE_SIZE), int(y / TILE_SIZE)
                board.select((x, y))
            if event.type == KEYDOWN and event.key == K_ESCAPE and ESCAPING:
                running = False

        board.draw(surf)
        pygame.display.update()


if __name__ == '__main__':
    logging.basicConfig(level=logging.NOTSET, format="[%(levelname)s] -> %(message)s")
    main()
    logging.info("closing")
    pygame.quit()
    sys.exit()
