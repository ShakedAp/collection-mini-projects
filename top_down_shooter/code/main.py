import math
import numpy as np
import time
import pygame
import sys
import pytmx
from pygame.locals import *
from entities import Player
from items import *
from bullets import *


clock = pygame.time.Clock()
pygame.init()

pygame.display.set_caption('Game')
WINDOW_SIZE = (900, 600)
last_time = time.time()
fps = 60

screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
display = pygame.Surface((450, 300))

true_scroll = [0, 0]
time_factor = 1

game_map = pytmx.load_pygame('../images/map.tmx')
TILEWIDTH, TILEHEIGHT = game_map.tilewidth, game_map.tileheight
player = Player(0, 0, 14, 17)
player.gun = OldShotgun()

# Loading map
walls = []
pickupables = []
bullets = []
for obj in game_map.objects:
    if obj.name == 'player':
        player.x = obj.x
        player.y = obj.y
    elif obj.name == 'gun':
        try:
            gun = globals()[obj.type]()
            pickupables.append(Pickupable(obj.x, obj.y, gun))
        except KeyError:
            print(f"Couldn't find class \"{obj.type}\", while loading map objects.")
    elif obj.name == 'wall':
        walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

# A bit buggy
# if "walls" in game_map.layernames:
#     for x, y, gid in game_map.get_layer_by_name("walls"):
#         if gid != 0:
#
#             tile = game_map.get_tile_image_by_gid(gid)
#             top, bottom = [TILEWIDTH-1, TILEHEIGHT-1], [0, 0]
#
#             for i in range(TILEWIDTH):
#                 for j in range(TILEHEIGHT):
#                     if tile.get_at((i, j))[3] != 0:
#                         if i * 16 + j < top[0]*TILEWIDTH + top[1]:
#                             top = [i, j]
#                         if i * 16 + j > top[0]*TILEWIDTH + top[1]:
#                             bottom = [i, j]
#
#             a = bottom[0] - top[0]+1, bottom[1] - top[1]+1
#             if sum(bottom)+sum(top) > TILEWIDTH+TILEHEIGHT:
#                 walls.append(pygame.Rect(x*TILEWIDTH + 16 - a[0], y*TILEHEIGHT + 16 - a[1], a[0], a[1]))
#             else:
#                 walls.append(pygame.Rect(x*TILEWIDTH, y*TILEHEIGHT, a[0], a[1]))
while True:
    clock.tick(fps)
    now = time.time()
    dt = (now - last_time) * time_factor
    last_time = now

    display.fill((28, 17, 23))
    # ------ Camera ------
    true_scroll[0] += (player.x - true_scroll[0] - 225-6) / 20
    true_scroll[1] += (player.y - true_scroll[1] - 158) / 20
    scroll = np.array(true_scroll, int)

    # ------ Calculating mouse angle ------
    mp = np.array(pygame.mouse.get_pos()) / 2
    pos = (player.x - true_scroll[0] + player.rect.width / 2,
           player.y - true_scroll[1] + player.rect.height / 2)
    mouse_angle = math.degrees(math.atan2((mp - pos)[1], (mp - pos)[0]))

    # ------ Game map ------
    lowest_tile = true_scroll[0]/TILEWIDTH - 1, true_scroll[1]/TILEHEIGHT - 1
    highest_tile = lowest_tile[0] + WINDOW_SIZE[0] // (TILEWIDTH*1.7), lowest_tile[1] + WINDOW_SIZE[1] // (TILEHEIGHT*1.7)

    for layer in game_map.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                if lowest_tile[0] < x < highest_tile[0] and lowest_tile[1] < y < highest_tile[1]:
                    tile = game_map.get_tile_image_by_gid(gid)
                    if tile:
                        display.blit(tile, (x * TILEWIDTH - scroll[0],
                                            y * TILEHEIGHT - scroll[1]))

    # ------ Game events------
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_d:
                player.moving_right = True
            if event.key == K_a:
                player.moving_left = True
            if event.key == K_s:
                player.moving_down = True
            if event.key == K_w:
                player.moving_up = True
            if event.key == K_SPACE:
                player.dash()
            if event.key == K_q:
                if player.gun:
                    pickupables.append(Pickupable(player.x,
                                                  player.y,
                                                  player.gun, angle=-mouse_angle))
                    player.gun = None
                else:
                    for p in pickupables:
                        if p.is_collision(player) and isinstance(p.item, Gun):
                            player.gun = p.item
                            pickupables.remove(p)
                            player.shooting_counter = 1/p.item.fire_rate
                            break
        if event.type == KEYUP:
            if event.key == K_d:
                player.moving_right = False
            if event.key == K_a:
                player.moving_left = False
            if event.key == K_s:
                player.moving_down = False
            if event.key == K_w:
                player.moving_up = False

    if pygame.mouse.get_pressed()[0]:
        if player.gun and player.shooting_counter >= 1/player.gun.fire_rate:
            pivot = player.get_gun_pivot(mouse_angle)
            player.gun.shoot(bullets, (pivot[0], pivot[1]), mouse_angle)
            player.shooting_counter = 0

    for p in pickupables:
        p.update(dt)
        p.render(display, scroll)
    for b in bullets:
        b.update(walls, dt, bullets)
        b.render(display, scroll)
    # print(bullets)

    player.update(walls, dt)
    player.render(display, true_scroll, -mouse_angle)

    screen.blit(pygame.transform.scale(display, WINDOW_SIZE), (0, 0))
    pygame.display.update()
