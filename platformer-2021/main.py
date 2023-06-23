import pygame
import pytmx as pytmx

from player import Player

pygame.init()

WIDTH, HEIGHT = 1000, 700

running = True
background_color = (105, 191, 214)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
display = pygame.Surface((WIDTH/2, HEIGHT/2))

clock = pygame.time.Clock()
screen.fill(background_color)
pygame.display.flip()

player = Player()
game_map = pytmx.load_pygame('map.tmx')
real_camera_scroll = [0, 0]
camera_scroll = [0, 0]
walls = []

for obj in game_map.objects:
    if obj.name == 'player':
        player.set_pos(obj.x, obj.y)
    elif obj.name == 'wall':
        walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))


while running:
    dt = clock.tick(60) * 0.001 * 60
    display.fill(background_color)

    real_camera_scroll[0] += (player.rect.x + player.rect.width/2 - camera_scroll[0] - WIDTH / 4) / 10
    real_camera_scroll[1] += (player.rect.y + player.rect.height/2 - camera_scroll[1] - HEIGHT / 4) / 10
    camera_scroll[0] = int(real_camera_scroll[0])
    camera_scroll[1] = int(real_camera_scroll[1])

    player.draw(display, camera_scroll)
    # ------ Game map ------
    for layer in game_map.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = game_map.get_tile_image_by_gid(gid)
                if tile:
                    display.blit(tile, (x * game_map.tilewidth - camera_scroll[0],
                                        y * game_map.tileheight - camera_scroll[1]))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_d:
                player.RIGHT_KEY = True
                player.turning_right = True
            if event.key == pygame.K_a:
                player.LEFT_KEY = True
                player.turning_right = False
            if event.key == pygame.K_SPACE or event.key == pygame.K_w:
                player.jump()
            if event.key == pygame.K_s:
                player.crouch()


        if event.type == pygame.KEYUP:
            if event.key == pygame.K_d:
                player.RIGHT_KEY = False
            if event.key == pygame.K_a:
                player.LEFT_KEY = False
            if event.key == pygame.K_SPACE or  event.key == pygame.K_w:
                if player.is_jumping:
                    if player.velocity.y < 0:
                        player.velocity.y *= 0.25
                    player.is_jumping = False
            if event.key == pygame.K_s:
                player.un_crouch()

    player.update(dt, walls)

    screen.blit(pygame.transform.scale(display, (WIDTH, HEIGHT)), (0, 0))
    pygame.display.update()