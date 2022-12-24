import pygame
import chess
pygame.init()
print("All modules loaded successfully.")

selected_square = (-1, -1)
last_played_moves = ()
legal_moves = []
moves = 1
board = chess.FEN_to_board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")


IMAGES = chess.load_images('pieces/')
WIDTH, HEIGHT = (chess.PIECE_SIZE*8, chess.PIECE_SIZE*8)
WHITE, BLACK = 1, 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Chess')
screen.fill((255, 255, 255))
chess.draw_board(screen)
chess.draw_pieces(screen, board, IMAGES)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            drew_played_moves = False
            if pygame.mouse.get_pressed()[2]:
                chess.draw_board(screen)
                selected_square = (-1, -1)

            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                last_selected_square = selected_square
                selected_square = (mouse_pos[1]//chess.PIECE_SIZE, mouse_pos[0]//chess.PIECE_SIZE)

                if selected_square in legal_moves:
                    v = chess.move_to_verbal(board, last_selected_square, selected_square)
                    print(v)
                    chess.move_piece(board, last_selected_square, selected_square)
                    chess.draw_board(screen)

                    moves += 1
                    last_played_moves = last_selected_square, selected_square
                    selected_square = (-1, -1)
                    legal_moves = []

                    # Check mate
                    for color in WHITE, BLACK:
                        if chess.is_mate(board, color):
                            print(f"{color} has been mated!")
                elif selected_square == last_selected_square:
                    chess.draw_board(screen)
                    selected_square = (-1, -1)
                elif (chess.get_piece(board, selected_square) != ' ') and (chess.is_white(board, selected_square) == moves % 2):
                    chess.draw_board(screen, selected_square)
                    legal_moves = chess.get_legal_moves(board, selected_square)
                    chess.remove_illegal_moves(board, legal_moves, selected_square)

                    if last_played_moves:
                        chess.draw_played_move(screen, last_played_moves[0], last_played_moves[1])
                        drew_played_moves = True

                    chess.draw_legal_moves(screen, legal_moves, board)
                else:
                    legal_moves = []
                    chess.draw_board(screen)

            if last_played_moves and not drew_played_moves:
                chess.draw_played_move(screen, last_played_moves[0], last_played_moves[1])
            for color in WHITE, BLACK:
                in_check, king_pos = chess.is_check(board, color)
                if in_check:
                    chess.draw_check(screen, king_pos, IMAGES)
            chess.draw_pieces(screen, board, IMAGES)
            pygame.display.update()