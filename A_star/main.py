import time

import astar
import pygame

pygame.init()
pygame.font.init()


def get_mouse_board_pos():
    mouse_pos = pygame.mouse.get_pos()
    return int(mouse_pos[1] // SQUARE_SIZE), int(mouse_pos[0] // SQUARE_SIZE)


def draw_board(surface):
    screen.fill(BACKGROUND_COLOR)
    for i in range(astar.BOARD_WIDTH):
        pygame.draw.rect(surface, (255, 255, 255), (0, SQUARE_SIZE * i, BORDER_SIZE, SCREEN_HEIGHT))
    for i in range(astar.BOARD_HEIGHT):
        pygame.draw.rect(surface, (255, 255, 255), (SQUARE_SIZE * i, 0, SQUARE_SIZE, BORDER_SIZE))


def draw_existing_board(surface, board, start_pos, end_pos, path_result=None):
    draw_board(surface)
    draw_block(surface, start_pos[0], start_pos[1], block_type='start', update=False)
    draw_block(surface, end_pos[0], end_pos[1], block_type='end', update=False)

    for i in range(len(board)):
        for j in range(len(board[i])):
            if not board[i][j].passable:
                draw_block(screen, i, j, update=False)

    if path_result is not None:
        draw_path(screen, path_result[0], path_result[1], update=False)

    pygame.display.update()

def draw_block(surface, row, col, block_type='wall', intensity=1, update=True):
    types = {'wall': (51, 54, 82), 'start': (24, 165, 88), 'end': (223, 54, 45),
             'path': (250, 208, 44), 'check': (144, 173, 198), 'background': BACKGROUND_COLOR}
    intensity = min(intensity, 1)
    color = types.get(block_type, BACKGROUND_COLOR)
    color = color[0] * intensity, color[1] * intensity, color[2] * intensity
    pygame.draw.rect(surface, color, (col * SQUARE_SIZE + BORDER_SIZE, row * SQUARE_SIZE + BORDER_SIZE,
                                      SQUARE_SIZE - BORDER_SIZE, SQUARE_SIZE - BORDER_SIZE))
    if update:
        pygame.display.update()


def draw_path(surface, path_indices, checked_nodes_info, update=True):
    # Draw path
    for index in path_indices:
        if index != astar.start_pos and index != astar.end_pos:
            draw_block(surface, index[0], index[1], block_type='path', update=False)

    display_state = DISPLAY_OPTIONS[current_display]
    pygame.display.set_caption(TITLE + f": {display_state}")

    # Draw all checked nodes
    if display_state != 'none':
        max_value = -1
        if display_state != 'show':  # Find max value for heatmap
            max_value = max(checked_nodes_info, key=lambda n: n[display_state])[display_state]

        # Draw heatmap
        for node_info in checked_nodes_info:
            if node_info['pos'] not in path_indices:
                if display_state == 'show':
                    draw_block(surface, node_info['pos'][0], node_info['pos'][1],
                               block_type='check', update=False)
                else:
                    draw_block(surface, node_info['pos'][0], node_info['pos'][1],

                               block_type='check', intensity=node_info[display_state] / max_value, update=False)

            # Draw values if requested
            if show_values and display_state != 'show':
                i = 1 - node_info[display_state] / max_value
                i = round(i)
                if node_info['pos'] in path_indices:
                    i = 0

                text_surface = FONT.render(str(node_info[display_state]), False, (255 * i, 255 * i, 255 * i))
                screen.blit(text_surface, (2 + node_info['pos'][1] * SQUARE_SIZE, node_info['pos'][0] * SQUARE_SIZE))

    if update:
        pygame.display.update()


BACKGROUND_COLOR = (233, 234, 236)
SQUARE_SIZE = 18
SCREEN_WIDTH, SCREEN_HEIGHT = astar.BOARD_WIDTH * SQUARE_SIZE, astar.BOARD_HEIGHT * SQUARE_SIZE
BORDER_SIZE = 0
FONT = pygame.font.SysFont('arial', 9)
TITLE = "A* Visualisation"
DISPLAY_OPTIONS = ['show', 'heuristic', 'g_score', 'f_score', 'none']

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)

running = True
current_display = 0
move_start, move_end = False, False
show_values, show_search = False, False
display_change_made = True

show_search_timer, show_search_timer_limit = 0,  0.001
astar_gen = astar.a_star_generator()
last_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = get_mouse_board_pos()

            if pos == astar.start_pos:
                move_start = True
            if pos == astar.end_pos:
                move_end = True

        if event.type == pygame.MOUSEBUTTONUP:
            if move_start:
                move_start = False
            if move_end:
                move_end = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                show_values = not show_values
                if BORDER_SIZE == 1:
                    BORDER_SIZE = 0
                else:
                    BORDER_SIZE = 1
                display_change_made = True
            elif event.key == pygame.K_r:
                astar.reset_board()
                display_change_made = True
            elif event.key == pygame.K_d:
                astar.shuffle_board()
                display_change_made = True
            elif event.key == pygame.K_w:
                show_search = True
                current_display = 0
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                current_display += 1
                if current_display >= len(DISPLAY_OPTIONS):
                    current_display = 0
                display_change_made = True

    mouse_state = pygame.mouse.get_pressed()
    if move_start:
        show_search = True
        pos = get_mouse_board_pos()
        if pos != astar.end_pos:
            astar.update_start(pos[0], pos[1])
            display_change_made = True
    elif move_end:
        pos = get_mouse_board_pos()
        if pos != astar.start_pos:
            astar.update_end(pos[0], pos[1])
            display_change_made = True
    elif mouse_state[0]:  # Add wall
        pos = get_mouse_board_pos()
        if pos != astar.start_pos and pos != astar.end_pos:
            astar.add_wall(pos[0], pos[1])
            display_change_made = True
    elif mouse_state[2]:  # Remove wall
        pos = get_mouse_board_pos()
        if pos != astar.start_pos and pos != astar.end_pos:
            astar.remove_wall(pos[0], pos[1])
            display_change_made = True

    if display_change_made and show_search:
        show_search = False
        astar_gen = astar.a_star_generator()

    if show_search and show_search_timer >= show_search_timer_limit:
        show_search_timer = 0

        path, info, done = next(astar_gen)
        
        if done:
            show_search = False
            astar_gen = astar.a_star_generator()

        draw_existing_board(screen, astar.board, astar.start_pos, astar.end_pos, path_result=(path, info))
    else:
        show_search_timer += time.time() - last_time
        last_time = time.time()

    if display_change_made:
        display_change_made = False
        draw_existing_board(screen, astar.board, astar.start_pos, astar.end_pos, path_result=astar.a_star())