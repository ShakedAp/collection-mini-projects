import math
import random
import pygame

pygame.init()

class DrawInfo:
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    BLACK = (0, 0, 0)
    DARK_GRAY = (64, 64, 64)
    BACKGROUND_COLOR = (255, 255, 255)
    SIDE_PADDING = 10
    TOP_PADDING = 150
    INSIDE_PADDING = 1

    SMALL_FONT = pygame.font.SysFont('david', 25)
    FONT = pygame.font.SysFont('david', 30)
    BIG_FONT = pygame.font.SysFont('david', 45)

    def __init__(self, width, height, lst):
        self.width = width
        self.height = height

        self.name = ''
        self.comparisons = 0

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('Sorting Visualizer')
        self.set_list(lst)



    def set_list(self, lst):
        self.lst = lst
        self.lst_len = len(lst)
        self.min_val = min(lst)
        self.max_val = max(lst)

        self.item_width = (self.width - self.SIDE_PADDING * 2) / self.lst_len - self.INSIDE_PADDING
        self.item_height = math.floor((self.height - self.TOP_PADDING) / self.max_val)
        self.len_display = self.lst_len
        self.add_comparison(-self.comparisons)

    def set_name(self, name):
        self.name = name

    def add_len_display(self, n=1):
        self.len_display += n

    def add_comparison(self, n=1):
        self.comparisons += n


def generate_list(length):
    lst = list(range(1, length + 1))
    random.shuffle(lst)
    return lst


def draw(draw_info, item_colors=None):
    draw_info.window.fill(draw_info.BACKGROUND_COLOR)

    title = draw_info.BIG_FONT.render(f"Algorithm: {draw_info.name}", 1, draw_info.BLACK)
    draw_info.window.blit(title, (draw_info.width / 2 - title.get_width() / 2, 0))

    controls = draw_info.FONT.render("Reset: R, Start Sorting: Space, Change Size: Arrows, Change Algorithm: Numbers",
                                     1,
                                     draw_info.DARK_GRAY)
    draw_info.window.blit(controls, (draw_info.width / 2 - controls.get_width() / 2, 40))

    amount = draw_info.SMALL_FONT.render(f"Amount: {draw_info.len_display:<3} | Comparisons: {draw_info.comparisons}", 1,
                                         draw_info.BLACK)
    draw_info.window.blit(amount, (10, 85))

    pygame.draw.rect(draw_info.window, draw_info.BLACK,
                     (0, 80, draw_info.width, 2))

    draw_lst(draw_info, item_colors)
    pygame.display.update()


def draw_lst(draw_info, item_colors=None):
    if item_colors is None:
        item_colors = {}
    lst = draw_info.lst

    for idx, value in enumerate(lst):
        x = draw_info.SIDE_PADDING + idx * (draw_info.item_width + draw_info.INSIDE_PADDING) + draw_info.INSIDE_PADDING
        y = draw_info.height - value * draw_info.item_height
        color = draw_info.BLACK

        if idx in item_colors:
            color = item_colors[idx]

        pygame.draw.rect(draw_info.window, color,
                         (x, y, draw_info.item_width, value * draw_info.item_height))


# Sorting Algorithms
def bubble_sort(draw_info):
    lst = draw_info.lst

    for i in range(draw_info.lst_len - 1):
        is_sorted = True

        for j in range(draw_info.lst_len - i - 1):
            if lst[j] > lst[j + 1]:
                lst[j], lst[j + 1] = lst[j + 1], lst[j]
                is_sorted = False

            draw_info.add_comparison()
            draw(draw_info, {j: draw_info.YELLOW, j + 1: draw_info.YELLOW})
            yield True

        if is_sorted:
            break
    return lst


def bidirectional_bubble_sort(draw_info):
    lst = draw_info.lst

    low_idx = 0
    high_idx = draw_info.lst_len - 1
    while low_idx < high_idx:
        is_sorted = True

        for i in range(low_idx, high_idx):
            if lst[i] > lst[i + 1]:
                lst[i], lst[i + 1] = lst[i + 1], lst[i]
                is_sorted = False

            draw_info.add_comparison()
            draw(draw_info, {i: draw_info.YELLOW, i + 1: draw_info.YELLOW})
            yield True

        high_idx -= 1
        if is_sorted:
            break
        is_sorted = True

        for i in range(high_idx, low_idx, -1):
            if lst[i] < lst[i - 1]:
                lst[i], lst[i - 1] = lst[i - 1], lst[i]
                is_sorted = False

            draw_info.add_comparison()
            draw(draw_info, {i: draw_info.YELLOW, i - 1: draw_info.YELLOW})
            yield True

        low_idx += 1
        draw_info.add_comparison()
        if is_sorted:
            break

    return lst


def selection_sort(draw_info):
    lst = draw_info.lst

    for i in range(draw_info.lst_len):
        min_idx = i

        for j in range(i + 1, draw_info.lst_len):
            yield True

            if lst[j] < lst[min_idx]:
                min_idx = j
            draw_info.add_comparison()

            draw(draw_info, {min_idx: draw_info.RED, i: draw_info.YELLOW, j: draw_info.YELLOW})

        lst[i], lst[min_idx] = lst[min_idx], lst[i]
        yield True

    return lst


def insertion_sort(draw_info):
    lst = draw_info.lst

    for i in range(1, draw_info.lst_len):
        key = lst[i]

        j = i - 1
        while j >= 0 and key < lst[j]:
            lst[j + 1] = lst[j]
            draw(draw_info, {i: draw_info.RED, j: draw_info.YELLOW, j + 1: draw_info.YELLOW})
            draw_info.add_comparison()

            j -= 1
            yield True

        lst[j + 1] = key
        draw(draw_info, {i: draw_info.RED, j: draw_info.YELLOW, j + 1: draw_info.YELLOW})
        yield True


def bogo_sort(draw_info):
    lst = draw_info.lst

    while True:
        shuffle = False

        for i in range(draw_info.lst_len - 1):
            draw(draw_info, {i: draw_info.YELLOW, i + 1: draw_info.YELLOW})
            draw_info.add_comparison()

            if lst[i] > lst[i + 1]:
                shuffle = True
                break
            yield True

        if shuffle:
            random.shuffle(lst)
            yield True
            continue
        break
    return lst


def main():
    running = True
    limit_speed = True
    clock = pygame.time.Clock()

    lst_len = 50
    len_append = 0
    add_timer, add_counter = 0, 0
    draw_info = DrawInfo(1200, 700, generate_list(lst_len))
    sorting = False
    sorting_algorithm = bubble_sort
    sorting_algorithm_generator = None
    draw_info.set_name('Bubble Sort')

    while running:
        if limit_speed:
            clock.tick(60)

        if sorting:
            try:
                next(sorting_algorithm_generator)
            except StopIteration:
                sorting = False
        else:
            draw(draw_info)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not sorting:
                    sorting = True
                    sorting_algorithm_generator = sorting_algorithm(draw_info)
                if event.key == pygame.K_r:
                    sorting = False
                    lst = generate_list(lst_len)
                    draw_info.set_list(lst)
                if event.key == pygame.K_l:
                    limit_speed = not limit_speed
                if not sorting:
                    if event.key == pygame.K_DOWN:
                        len_append = -1
                    if event.key == pygame.K_UP:
                        len_append = 1

                    if event.key == pygame.K_1:
                        sorting_algorithm = bubble_sort
                        draw_info.set_name('Bubble Sort')
                    if event.key == pygame.K_2:
                        sorting_algorithm = bidirectional_bubble_sort
                        draw_info.set_name('Bidirectional Bubble Sort')
                    if event.key == pygame.K_3:
                        sorting_algorithm = selection_sort
                        draw_info.set_name('Selection Sort')
                    if event.key == pygame.K_4:
                        sorting_algorithm = insertion_sort
                        draw_info.set_name('Insertion Sort')
                    if event.key == pygame.K_5:
                        sorting_algorithm = bogo_sort
                        draw_info.set_name('Bogo Sort')
            if event.type == pygame.KEYUP:
                if not sorting:
                    if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                        len_append = 0
                        draw_info.set_list(generate_list(draw_info.len_display))

        if (len_append != 0 and 2 < lst_len < 300) or (lst_len == 2 and len_append > 0) or (lst_len == 300 and len_append < 0):
            if add_counter == 0:
                draw_info.add_len_display(len_append)
                lst_len += len_append

            add_counter += 1
            add_timer += 1

            if add_timer > 290 and add_counter > 1:
                add_counter = 0
                continue
            if add_timer > 210 and add_counter > 5:
                add_counter = 0
                continue
            elif add_timer > 120 and add_counter > 15:
                add_counter = 0
                continue
            if add_counter > 30:
                add_counter = 0
        else:
            add_timer, add_counter = 0, 0

    pygame.quit()


if __name__ == '__main__':
    main()
