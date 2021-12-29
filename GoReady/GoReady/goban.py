import math
import pygame
import go
import random
from sys import exit
from pygame.locals import *

BACKGROUND = 'images/bg.png'
BOARD_SIZE = (820, 820)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Stone(go.Stone):
    def __init__(self, board, point, color):
        super(Stone, self).__init__(board, point, color)
        self.coords = (5 + self.point[0] * 40, 5 + self.point[1] * 40)
        self.draw()

    def draw(self):
        pygame.draw.circle(screen, self.color, self.coords, 20, 0)

        pygame.display.update()

    def remove(self):
        blit_coords = (self.coords[0] - 20, self.coords[1] - 20)
        area_rect = pygame.Rect(blit_coords, (40, 40))
        screen.blit(background, blit_coords, area_rect)
        pygame.display.update()
        super(Stone, self).remove()


class Board(go.Board):
    def __init__(self):
        super(Board, self).__init__()
        self.outline = pygame.Rect(45, 45, 720, 720)
        self.draw()


     #   self.blackScore=black
      #  self.whiteScore =white
    def draw(self):
        pygame.draw.rect(background, BLACK, self.outline, 3)
        # Outline is inflated here for future use as a collidebox for the mouse
        self.outline.inflate_ip(20, 20)
        for i in range(18):
            for j in range(18):
                rect = pygame.Rect(45 + (40 * i), 45 + (40 * j), 40, 40)
                pygame.draw.rect(background, BLACK, rect, 1)
        for i in range(3):
            for j in range(3):
                coords = (165 + (240 * i), 165 + (240 * j))
                pygame.draw.circle(background, BLACK, coords, 5, 0)
        screen.blit(background, (0, 0))

        pygame.display.update()


def main():
    default_font = pygame.font.get_default_font()
    font = pygame.font.Font(default_font, 32)
    while True:
        pygame.display.flip()
        pygame.time.wait(250)
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print(board.printPass())
                    exit()
                if event.key == pygame.K_p:
                    board.appendPass(1)
                    board.turn()
            empty = board.empty_intersections()
            stones = board.calc_stones()
            terras = board.calculate_territory(empty)
            finished = board.game_finished(stones, terras, empty)
            if finished[0]:
                print("Game Ended")
                print("Black Score:", finished[1])
                print("White Score:", finished[2])
                exit()
            if board.next == BLACK:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and board.outline.collidepoint(event.pos):
                        x = int(round(((event.pos[0] - 5) / 40.0), 0))
                        y = int(round(((event.pos[1] - 5) / 40.0), 0))
                        stone = board.search(point=(x, y))
                        board.appendPass(0)
                        if stone:
                            continue
                        else:
                            added_stone = Stone(board, (x, y), board.turn())

                        board.update_liberties(added_stone)
            else:

                point = board.miniMax_agent()
                added_stone = Stone(board, point[0], board.turn())
                board.update_liberties(added_stone)



if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    pygame.display.set_caption('MINIMAX GO AGENT')
    screen = pygame.display.set_mode(BOARD_SIZE, 0, 32)
    background = pygame.image.load(BACKGROUND).convert()

    board = Board()
    main()
