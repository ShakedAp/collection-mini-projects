import pygame
from copy import deepcopy
pygame.font.init()

BOARD_COLORS = [(180, 140, 100), (244, 220, 180)]
SELECTED_SQUARE_COLORS = [(100, 111, 64), (130, 151, 105)]
MOVE_COLORS = [(170, 162, 58), (205, 210, 106)]
PIECE_SIZE = 60


# Helper functions
def FEN_to_board(fen):
    board = []
    for row in fen.split('/'):
        row_arr = []
        for i in row:
            if i.isnumeric():
                row_arr.extend(list(int(i) * ' '))
            else:
                row_arr.append(i)
        board.append(row_arr)
    return board


def print_board(board):
    for i, row in enumerate(board):
        print(8 - i, ' '.join(row))


def load_images(folder):
    images = {'k': pygame.image.load(folder + 'black_king.png'),
              'K': pygame.image.load(folder + 'white_king.png'),
              'q': pygame.image.load(folder + 'black_queen.png'),
              'Q': pygame.image.load(folder + 'white_queen.png'),
              'r': pygame.image.load(folder + 'black_rook.png'),
              'R': pygame.image.load(folder + 'white_rook.png'),
              'b': pygame.image.load(folder + 'black_bishop.png'),
              'B': pygame.image.load(folder + 'white_bishop.png'),
              'n': pygame.image.load(folder + 'black_knight.png'),
              'N': pygame.image.load(folder + 'white_knight.png'),
              'p': pygame.image.load(folder + 'black_pawn.png'),
              'P': pygame.image.load(folder + 'white_pawn.png'),
              'check': pygame.image.load(folder + 'check.png')
              }
    return images


def get_piece(board, pos):
    if (7 >= pos[0] >= 0) and (7 >= pos[1] >= 0):
        return board[pos[0]][pos[1]]
    else:
        return ''


def is_white(board, pos):
    piece = get_piece(board, pos)
    if piece == ' ':
        return -1
    return int(piece.isupper())


def move_to_verbal(board, from_pos, to_pos):
    piece = get_piece(board, from_pos).upper()
    verbal_to_pos = f"{chr(97+to_pos[1])}{8-to_pos[0]}"
    if get_piece(board, from_pos).lower() == 'p':
        if get_piece(board, to_pos) == ' ':
            return verbal_to_pos
        else:
            return f"{chr(97+from_pos[1])}x{verbal_to_pos}"
    if get_piece(board, to_pos) == ' ':
        return f"{piece}{verbal_to_pos}"

    else:
        return f"{piece}x{verbal_to_pos}"


# Board methods
def get_legal_moves(board, pos):
    moves = []

    if get_piece(board, pos) == 'p':
        move = (pos[0] + 1, pos[1])
        if get_piece(board, move) == ' ':
            moves.append(move)
            move = (3, pos[1])
            if pos[0] == 1 and get_piece(board, move) == ' ':
                moves.append((3, pos[1]))
        for i in -1, 1:
            move = (pos[0] + 1, pos[1] + i)
            if get_piece(board, move) != ' ':
                moves.append(move)

    if get_piece(board, pos) == 'P':
        move = (pos[0] - 1, pos[1])
        if get_piece(board, move) == ' ':
            moves.append((pos[0] - 1, pos[1]))
            move = (4, pos[1])
            if pos[0] == 6 and get_piece(board, move) == ' ':
                moves.append((4, pos[1]))
        for i in -1, 1:
            move = (pos[0] - 1, pos[1] + i)
            if get_piece(board, move) != ' ':
                moves.append(move)

    if get_piece(board, pos).lower() == 'n':
        moves.append((pos[0] + 1, pos[1] + 2))
        moves.append((pos[0] - 1, pos[1] + 2))
        moves.append((pos[0] + 1, pos[1] - 2))
        moves.append((pos[0] - 1, pos[1] - 2))

        moves.append((pos[0] + 2, pos[1] + 1))
        moves.append((pos[0] - 2, pos[1] + 1))
        moves.append((pos[0] + 2, pos[1] - 1))
        moves.append((pos[0] - 2, pos[1] - 1))

    if get_piece(board, pos).lower() == 'b' or get_piece(board, pos).lower() == 'q':
        for i in range(1, 8):  # left up
            move = (pos[0] - i, pos[1] - i)
            moves.append(move)
            if get_piece(board, move) != ' ':
                break
        for i in range(1, 8):  # right up
            move = (pos[0] - i, pos[1] + i)
            moves.append(move)
            if get_piece(board, move) != ' ':
                break
        for i in range(1, 8):  # left down
            move = (pos[0] + i, pos[1] - i)
            moves.append(move)
            if get_piece(board, move) != ' ':
                break
        for i in range(1, 8):  # right down
            move = (pos[0] + i, pos[1] + i)
            moves.append(move)
            if get_piece(board, move) != ' ':
                break

    if get_piece(board, pos).lower() == 'r' or get_piece(board, pos).lower() == 'q':
        for i in range(1, pos[0] + 1):  # up
            move = (pos[0] - i, pos[1])
            moves.append(move)
            if get_piece(board, move) != ' ':
                break
        for i in range(1, 8 - pos[0]):  # down
            move = (pos[0] + i, pos[1])
            moves.append(move)
            if get_piece(board, move) != ' ':
                break
        for i in range(1, 8 - pos[1]):  # right
            move = (pos[0], pos[1] + i)
            moves.append(move)
            if get_piece(board, move) != ' ':
                break
        for i in range(1, pos[1] + 1):  # left
            move = (pos[0], pos[1] - i)
            moves.append(move)
            if get_piece(board, move) != ' ':
                break

    if get_piece(board, pos).lower() == 'k':
        for j in (-1, 0, 1):
            for i in (-1, 0, 1):
                moves.append((pos[0] + j, pos[1] + i))

    color = is_white(board, pos)
    for move in moves[:]:
        if (not 7 >= move[0] >= 0) or (not 7 >= move[1] >= 0):
            moves.remove(move)
        elif is_white(board, move) == color:
            moves.remove(move)

    return moves


def move_piece(board, from_pos, to_pos):
    board[to_pos[0]][to_pos[1]] = board[from_pos[0]][from_pos[1]]
    board[from_pos[0]][from_pos[1]] = ' '


def is_check(board, color):
    king_pos = (-1, -1)
    for j in range(8):
        for i in range(8):
            if color == 1 and get_piece(board, (j, i)) == 'K':
                king_pos = (j, i)
                break
            elif get_piece(board, (j, i)) == 'k':
                king_pos = (j, i)
                break

    for j in range(8):
        for i in range(8):
            pos = (j, i)
            if is_white(board, pos) != color:
                moves = get_legal_moves(board, pos)
                if king_pos in moves:
                    return True, king_pos

    return False, king_pos


def is_mate(board, color):
    for j in range(8):
        for i in range(8):
            pos = (j, i)
            if is_white(board, pos) == color:
                moves = get_legal_moves(board, pos)
                remove_illegal_moves(board, moves, pos)
                if moves:
                    return False

    return True


def remove_illegal_moves(board, moves, pos):
    color = is_white(board, pos)

    for move in moves[:]:
        new_board = deepcopy(board)
        move_piece(new_board, pos, move)

        if is_check(new_board, color)[0]:
            moves.remove(move)


# Display
def draw_legal_moves(surface, moves, board):
    for move in moves:
        selected_color = SELECTED_SQUARE_COLORS[move[1] % 2 == move[0] % 2]
        back_color = BOARD_COLORS[move[1] % 2 == move[0] % 2]
        if get_piece(board, move) == ' ':
            pygame.draw.circle(surface, selected_color,
                               (move[1] * PIECE_SIZE + PIECE_SIZE / 2, move[0] * PIECE_SIZE + PIECE_SIZE / 2),
                               PIECE_SIZE / 6)
        else:
            pygame.draw.rect(surface, selected_color,
                             (move[1] * PIECE_SIZE, move[0] * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))
            pygame.draw.circle(surface, back_color,
                               (move[1] * PIECE_SIZE + PIECE_SIZE / 2, move[0] * PIECE_SIZE + PIECE_SIZE / 2),
                               PIECE_SIZE / 2)


def draw_played_move(surface, from_pos, to_pos):
    for j, i in from_pos, to_pos:
        current_color = MOVE_COLORS[i % 2 == j % 2]
        pygame.draw.rect(surface, current_color,
                         (i * PIECE_SIZE, j * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))


def draw_board(surface, selected_square=None):
    for j in range(8):
        for i in range(8):
            # beginning with bright color if line number is even, dark otherwise.
            current_color = BOARD_COLORS[i % 2 == j % 2]
            pygame.draw.rect(surface, current_color,
                             (i * PIECE_SIZE, j * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))
            if selected_square is not None:
                if (j, i) == selected_square:
                    selected_color = SELECTED_SQUARE_COLORS[i % 2 == j % 2]
                    pygame.draw.rect(surface, selected_color,
                                     (i * PIECE_SIZE , j * PIECE_SIZE, PIECE_SIZE, PIECE_SIZE))


def draw_pieces(surface, board, images):
    for j, row in enumerate(board):
        for i, piece in enumerate(row):
            if piece != ' ':
                surface.blit(images[piece], (i * PIECE_SIZE, j * PIECE_SIZE))


def draw_check(surface, king_pos, images):
    surface.blit(images['check'], (king_pos[1] * PIECE_SIZE, king_pos[0] * PIECE_SIZE))

