import math
import os
from abc import ABC, abstractmethod

import numpy as np
import pygame


class Entity(ABC):
    def __init__(self, x, y, width, height, hp):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, width, height)
        self.hp = hp

    @abstractmethod
    def update(self, dt):
        pass

    @abstractmethod
    def render(self, surface, camera_scroll):
        pass

    def collision_test(self, tiles):
        hit_list = []
        for tile in tiles:
            if self.rect.colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def move(self, movement, tiles):
        collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.rect.y = self.y
        self.rect.x = self.x
        # --- x ---
        self.rect.x += movement[0]
        hit_list = self.collision_test(tiles)[::-1]
        for tile in hit_list:
            if movement[0] > 0:
                self.rect.right = tile.left
                collision_types['right'] = True
            elif movement[0] < 0:
                self.rect.left = tile.right
                collision_types['left'] = True

        # --- y ---
        self.rect.y += movement[1]
        hit_list = self.collision_test(tiles)[::-1]
        for tile in hit_list:
            if movement[1] > 0:
                self.rect.bottom = tile.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                self.rect.top = tile.bottom
                collision_types['top'] = True
        self.y = self.rect.y
        self.x = self.rect.x
        return collision_types

    @staticmethod
    def load_animation(directory, frames_durations):
        animation = []
        dir_tree = os.listdir(directory)

        for idx, filename in enumerate(dir_tree):
            if filename.endswith('.png') or filename.endswith('.jpg'):
                image = pygame.image.load(f'{directory}/{filename}').convert_alpha()
                for i in range(frames_durations[idx]):
                    animation.append(image)
        return animation


class Player(Entity):

    def __init__(self, x, y, width, height):
        super(Player, self).__init__(x, y, width, height, 100)
        self.animations = {'running': Entity.load_animation('../images/run', [12, 12]),
                           'crouch': [pygame.image.load('../images/crouch.png').convert_alpha()],
                           'idle': [pygame.image.load('../images/run/run_0.png').convert_alpha()]}
        self.current_animation = self.animations['idle']
        self.current_frame = self.current_animation[0]
        self.animation_counter = 0

        self.moving_right, self.moving_left, self.moving_up, self.moving_down = False, False, False, False

        self.dash_wait, self.dash_last = 0.5, 0.1
        self.dash_counter = self.dash_wait

        self.gun = None
        self.shooting_counter = 0
        self.can_shoot = True

    def update(self, walls, dt):
        speed = 175
        player_movement = [0, 0]
        if self.moving_right:
            player_movement[0] += speed
        if self.moving_left:
            player_movement[0] -= speed
        if self.moving_up:
            player_movement[1] -= speed
        if self.moving_down:
            player_movement[1] += speed

        player_movement[0] = player_movement[0] * dt
        player_movement[1] = player_movement[1] * dt

        if self.dash_counter < self.dash_wait:
            if self.dash_counter < self.dash_last:
                player_movement[0] *= 3 - self.dash_counter
                player_movement[1] *= 3 - self.dash_counter
            self.dash_counter += dt

        collisions = self.move(player_movement, walls)

        # ---- animations ----
        if player_movement[0] == 0 and player_movement[1] == 0:
            if self.current_animation != self.animations['idle']:
                self.current_animation = self.animations['idle']
                self.animation_counter = 0
        else:
            if self.current_animation != self.animations['running']:
                self.current_animation = self.animations['running']
                self.animation_counter = 0

        self.animation_counter += 1
        if self.animation_counter == len(self.current_animation):
            self.animation_counter = 0
        self.current_frame = self.current_animation[self.animation_counter]

        # ---- shooting ----
        if self.gun:
            if self.shooting_counter < 1 / self.gun.fire_rate:
                self.shooting_counter += dt
            else:
                self.gun.reload()

    def render(self, surface, camera_scroll, angle):
        if self.gun:
            pos = (self.x - camera_scroll[0] + self.rect.width / 2, self.y - camera_scroll[1] + self.rect.height / 2)
            img = self.gun.current_frame
            if not (-90 <= angle <= 90):
                img = pygame.transform.flip(img, False, True)
            blitRotate(surface, img, pos, [0, img.get_height() / 2], angle)
        surface.blit(self.current_frame, (self.rect.x - camera_scroll[0], self.rect.y - camera_scroll[1]))

    def get_gun_pivot(self, angle):
        if self.gun:
            pivot = pygame.math.Vector2(self.gun.shooting_pivot)
            pivot = pivot.rotate(angle)
            return pivot[0] + self.x, pivot[1] + self.y
        else:
            return None

    def dash(self):
        if self.dash_counter >= self.dash_wait:
            self.dash_counter = 0


def blitRotate(surf, image, pos, originPos, angle):
    image_rect = image.get_rect(topleft=(pos[0] - originPos[0], pos[1] - originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    surf.blit(rotated_image, rotated_image_rect)
