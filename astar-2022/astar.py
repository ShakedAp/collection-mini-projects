import math
import random

BOARD_WIDTH, BOARD_HEIGHT = 90, 45


class Node:

    def __init__(self, pos):
        self.pos = pos
        self.parent = None

        self.heuristic = -1
        self.passable = True
        self.f_score = math.inf
        self.g_score = math.inf

    def calculate_heuristic(self, end_pos):
        self.heuristic = round(math.sqrt((end_pos[0] - self.pos[0]) ** 2 + (end_pos[1] - self.pos[1]) ** 2), 2)

    def reset_scores(self):
        self.f_score = math.inf
        self.g_score = math.inf


def reset_board():
    global board, start_pos, end_pos
    board = [[Node((i, j)) for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]
    start_pos, end_pos = (0, 0), (BOARD_HEIGHT - 1, BOARD_WIDTH - 1)


def shuffle_board():
    global board, start_pos, end_pos
    board = [[Node((i, j)) for j in range(BOARD_WIDTH)] for i in range(BOARD_HEIGHT)]
    start_pos = (random.randint(0, BOARD_HEIGHT - 1), random.randint(0, BOARD_WIDTH - 1))
    end_pos = (random.randint(0, BOARD_HEIGHT - 1), random.randint(0, BOARD_WIDTH - 1))

    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            if (i, j) != start_pos and (i, j) != end_pos:
                is_wall = random.randint(0, 10) % 3
                board[i][j].passable = is_wall


def add_wall(row, col):
    board[row][col].passable = False


def remove_wall(row, col):
    board[row][col].passable = True


def update_start(row, col):
    global start_pos
    start_pos = row, col
    remove_wall(row, col)


def update_end(row, col):
    global end_pos
    end_pos = row, col
    remove_wall(row, col)


def reconstruct_path(node):
    path = []
    while node is not None:
        path.append(node.pos)
        node = node.parent
    return path


def a_star():
    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            board[i][j].calculate_heuristic(end_pos)
            board[i][j].reset_scores()
            board[i][j].parent = None

    nodes_checked = []
    opened_nodes = [board[start_pos[0]][start_pos[1]]]
    opened_nodes[0].g_score = 0
    opened_nodes[0].f_score = opened_nodes[0].heuristic

    while opened_nodes:
        current_node = min(opened_nodes, key=lambda n: n.f_score)
        opened_nodes.remove(current_node)

        if current_node.pos == end_pos:
            nodes_checked_result = []
            for node in nodes_checked:
                nodes_checked_result.append({'pos': node.pos,
                                             'f_score': round(node.f_score),
                                             'g_score': round(node.g_score),
                                             'heuristic': round(node.heuristic)})
            return reconstruct_path(current_node), nodes_checked_result

        neighbors_indices = [(current_node.pos[0], current_node.pos[1] + 1),
                             (current_node.pos[0], current_node.pos[1] - 1),
                             (current_node.pos[0] + 1, current_node.pos[1]),
                             (current_node.pos[0] - 1, current_node.pos[1])]

        for index in neighbors_indices:
            if (index[0] >= BOARD_HEIGHT or index[0] < 0) or (index[1] >= BOARD_WIDTH or index[1] < 0):
                continue
            neighbor = board[index[0]][index[1]]
            if not neighbor.passable:
                continue
            val = 1 + current_node.g_score

            # Found a better way for this node. Updates it
            if val < neighbor.g_score:
                neighbor.parent = current_node
                neighbor.g_score = val
                neighbor.f_score = val + neighbor.heuristic
                if neighbor not in opened_nodes:
                    opened_nodes.append(neighbor)
                    nodes_checked.append(neighbor)
    return [], []


def a_star_generator():
    for i in range(BOARD_HEIGHT):
        for j in range(BOARD_WIDTH):
            board[i][j].calculate_heuristic(end_pos)
            board[i][j].reset_scores()
            board[i][j].parent = None

    nodes_checked = []
    opened_nodes = [board[start_pos[0]][start_pos[1]]]
    opened_nodes[0].g_score = 0
    opened_nodes[0].f_score = opened_nodes[0].heuristic

    while opened_nodes:

        nodes_checked_result = []
        for node in nodes_checked:
            nodes_checked_result.append({'pos': node.pos,
                                         'f_score': round(node.f_score),
                                         'g_score': round(node.g_score),
                                         'heuristic': round(node.heuristic)})
        yield [], nodes_checked_result, False

        current_node = min(opened_nodes, key=lambda n: n.f_score)
        opened_nodes.remove(current_node)

        if current_node.pos == end_pos:
            nodes_checked_result = []
            for node in nodes_checked:
                nodes_checked_result.append({'pos': node.pos,
                                             'f_score': round(node.f_score),
                                             'g_score': round(node.g_score),
                                             'heuristic': round(node.heuristic)})
            yield reconstruct_path(current_node), nodes_checked_result, True

        neighbors_indices = [(current_node.pos[0], current_node.pos[1] + 1),
                             (current_node.pos[0], current_node.pos[1] - 1),
                             (current_node.pos[0] + 1, current_node.pos[1]),
                             (current_node.pos[0] - 1, current_node.pos[1])]

        for index in neighbors_indices:
            if (index[0] >= BOARD_HEIGHT or index[0] < 0) or (index[1] >= BOARD_WIDTH or index[1] < 0):
                continue
            neighbor = board[index[0]][index[1]]
            if not neighbor.passable:
                continue
            val = 1 + current_node.g_score

            # Found a better way for this node. Updates it
            if val < neighbor.g_score:
                neighbor.parent = current_node
                neighbor.g_score = val
                neighbor.f_score = val + neighbor.heuristic
                if neighbor not in opened_nodes:
                    opened_nodes.append(neighbor)
                    nodes_checked.append(neighbor)

    yield [], [], True


board = []
start_pos, end_pos = (0, 0), (BOARD_HEIGHT - 1, BOARD_WIDTH - 1)
reset_board()
