"""
    *This is an old project. I am pretty sure that it was made somewhere around 2020.
    *I made sevral tic tac toes, but this is one of my favorites
    *Before making this one I created a version in the terminal using java, in one of our intro to cs classes.
"""

import pygame
import random

pygame.init()
pygame.font.init()


WINDOW_SIZE = 600
PAD = 30
FONT = pygame.font.SysFont('calibri', 20)


def check_win(board):
    """Checks if any player has one the game.
    If any player won the it's value will be returned. If there was a draw the 1.5 will be returned.
    Otherwise the -1 will be returned.

    :param board: the board board to be checked
    :return: the winner or game state
    :rtype: int
    """
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != 0:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != 0:
            return board[0][i]

    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != 0:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != 0:
        return board[0][2]

    is_draw = True
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                is_draw = False
    if is_draw:
        return 1.5

    return -1


def minimax(board, player):
    """Minimax algorithm to find the best move. If there are more than one best move, a random one will be returned.

    :param board: The board to find the best move on
    :param player: The player who's turn it is
    :return: Best move and score (x, y, score)
    """
    moves = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                board[i][j] = player
                win = check_win(board)

                if win == -1:
                    opponent_move = minimax(board, player % 2 + 1)
                    moves.append((i, j, opponent_move[2]))
                else:
                    moves.append((i, j, win))

                board[i][j] = 0

    if player == 2:
        return max(moves, key=lambda x: x[2]*10 + random.random())
    else:
        return min(moves, key=lambda x: x[2]*10 + random.random())


def reset_board(board):
    """Fills the given board with zeros."""
    for i in range(3):
        for j in range(3):
            board[i][j] = 0


# Graphics
def draw_outline(surface):
    """Draws the board outline on the given surface.

    :param surface: surface to draw the board outline on
    :return: None
    """
    color = (0, 0, 0)
    size = 5
    for i in range(1, 3):
        pygame.draw.rect(surface, color, (WINDOW_SIZE / 3 * i, PAD, size, WINDOW_SIZE - 2 * PAD))
        pygame.draw.rect(surface, color, (PAD, WINDOW_SIZE / 3 * i, WINDOW_SIZE - 2 * PAD, size))


def draw_sign(surface, pos, player):
    """Draws the correct sign at the given pos, on the given surface.

    :param surface: surface to draw the sign on
    :param pos: indices of where to draw the sign
    :param player: the number of the player. 1 for X, 2 for O
    :return: None
    """
    color = (0, 0, 0)
    size, width = WINDOW_SIZE / 3, 5
    if player == 1:
        pygame.draw.line(surface, color, (pos[0] * size + PAD, pos[1] * size + PAD),
                         ((pos[0] + 1) * size - PAD, (pos[1] + 1) * size - PAD), width)

        pygame.draw.line(surface, color, ((pos[0] + 1) * size - PAD, pos[1] * size + PAD),
                         (pos[0] * size + PAD, (pos[1] + 1) * size - PAD), width)
    else:
        pygame.draw.circle(surface, color,
                           (pos[0] * size + size / 2, pos[1] * size + size / 2), size / 2 - PAD, width)
    pygame.display.update()


def draw_title(surface, txt):
    """Draws a title at the top of the given surface.

    :param surface: The surface on which the title will be drawn
    :param txt: The title
    :return: None
    """
    surface.fill((255, 255, 255), (0, 0, WINDOW_SIZE, PAD))
    text_surface = FONT.render(txt, False, (0, 0, 0))
    surface.blit(text_surface, (WINDOW_SIZE / 2 - text_surface.get_width() / 2, 0))
    pygame.display.update((0, 0, WINDOW_SIZE, PAD))


def clear_graphics(surface):
    """Clears all of the surface and redraws the board on it. Keeps the title"""
    surface.fill((255, 255, 255), (0, PAD, WINDOW_SIZE, WINDOW_SIZE-PAD))
    draw_outline(surface)
    pygame.display.update()


def main():
    # 0 for empty, 1 for X, 2 for O
    board = [[0, 0, 0],
             [0, 0, 0],
             [0, 0, 0]]
    moves, winner = 0, -1
    mode = 1
    running = True
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

    clear_graphics(screen)
    draw_title(screen, "1: Player vs Player")

    while running:

        if (mode == 2 and moves % 2 == 1) or (mode == 3 and moves % 2 == 0) or (mode == 4):
            if winner == -1:
                player = moves % 2 + 1
                x, y, p = minimax(board, player)
                draw_sign(screen, (x, y), player)
                board[x][y] = player
                winner = check_win(board)
                moves += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 1
                    draw_title(screen, "1: Player vs Player")
                if event.key == pygame.K_2:
                    mode = 2
                    draw_title(screen, "2: Player vs AI")
                if event.key == pygame.K_3:
                    mode = 3
                    draw_title(screen, "3: AI vs Player")
                if event.key == pygame.K_4:
                    mode = 4
                    draw_title(screen, "4: AI vs AI")
                if event.key == pygame.K_r:
                    reset_board(board)
                    winner = -1
                    moves = 0
                    clear_graphics(screen)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if (mode == 1) or (mode == 2 and moves % 2 == 0) or (mode == 3 and moves % 2 == 1):
                    mouse_pos = pygame.mouse.get_pos()
                    x, y = int(mouse_pos[0] // (WINDOW_SIZE / 3)), int(mouse_pos[1] // (WINDOW_SIZE / 3))

                    if board[x][y] == 0 and winner == -1:
                        player = moves % 2 + 1
                        draw_sign(screen, (x, y), player)
                        board[x][y] = player
                        winner = check_win(board)
                        moves += 1


if __name__ == '__main__':
    main()
