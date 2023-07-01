import math

import pygame.draw


class Player:

    def __init__(self, x=0, y=0):
        self.image = pygame.image.load('snowman.png')
        self.crouch_image = pygame.image.load('snowman_crouch.png')
        self.color = (255, 0, 0)
        self.rect = pygame.Rect(x, y, 16, 16)
        self.turning_right = True

        self.LEFT_KEY, self.RIGHT_KEY = False, False
        self.is_jumping, self.is_crouching, self.on_ground = False, False, False
        self.gravity, self.friction = 0.35, -0.12
        self.max_velocity = 4
        self.position, self.velocity, = pygame.math.Vector2(x, y), pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

    def set_pos(self, x, y):
        self.position.x = x
        self.position.y = y
        self.rect.x = x
        self.rect.y = y

    def draw(self, surface, camera_scroll):
        draw_image = self.image
        if self.is_crouching:
            draw_image = self.crouch_image
        if not self.turning_right:
            draw_image = pygame.transform.flip(draw_image, True, False)
        surface.blit(draw_image, (self.rect.x - camera_scroll[0], self.rect.y - camera_scroll[1]))

    def update(self, dt, tiles):
        self.vertical_movement(dt, tiles)
        self.horizontal_movement(dt, tiles)

    def collision_test(self, tiles):
        hit_list = []
        for tile in tiles:
            if self.rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def vertical_movement(self, dt, tiles):
        self.velocity.y += self.acceleration.y * dt
        if self.velocity.y > 7: self.velocity.y = 7
        self.position.y += self.velocity.y * dt - 0.5 * self.acceleration.y * dt * dt
        self.rect.y = self.position.y
        hit_list = self.collision_test(tiles)
        for tile in hit_list:
            if self.velocity.y > 0:
                self.rect.bottom = tile.top
                self.on_ground = True
            elif self.velocity.y < 0:
                self.rect.top = tile.bottom
            self.velocity.y = 0
            self.position.y = self.rect.y
        if self.velocity.y > self.acceleration.y * 3:
            self.on_ground = False

    def horizontal_movement(self, dt, tiles):
        self.acceleration.x = 0
        if self.RIGHT_KEY:
            self.acceleration.x += 0.5
        if self.LEFT_KEY:
            self.acceleration.x -= 0.5
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.limit_velocity(self.max_velocity)
        self.position.x += self.velocity.x * dt - 0.5 * self.acceleration.x * dt * dt
        self.rect.x = self.position.x

        # Collision
        hit_list = self.collision_test(tiles)
        for tile in hit_list:
            if self.velocity.x > 0:
                self.rect.right = tile.left
            elif self.velocity.x < 0:
                self.rect.left = tile.right
            self.position.x = self.rect.x

    def limit_velocity(self, max_vel):
        self.velocity.x = max(-max_vel, min(max_vel, self.velocity.x))
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0

    def jump(self):
        if self.on_ground:
            self.on_ground = False
            self.is_jumping = True
            self.velocity.y = -8

    def crouch(self):
        self.is_crouching = True
        self.rect = pygame.Rect(self.rect.x, self.rect.y, 12, 12)
        self.friction /= 10
        self.max_velocity += 2

    def un_crouch(self):
        self.is_crouching = False
        self.rect = pygame.Rect(self.rect.x, self.rect.y, 16, 16)
        self.friction *= 10
        self.max_velocity -= 2