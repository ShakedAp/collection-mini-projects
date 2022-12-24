import math
import os
from abc import ABC, abstractmethod
import effects

import numpy as np
import pygame


class BulletEntity(ABC):

    def __init__(self, x, y, angle, width, height, velocity, animation, pivot_ratios):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.movement = np.array([0, 0])
        self.movement[0] = math.cos(math.radians(angle)) * velocity
        self.movement[1] = math.sin(math.radians(angle)) * velocity

        self.animation = []
        for frame in animation:
            if not (-90 <= angle <= 90):
                frame = pygame.transform.flip(frame, False, True)
            i = rotate(frame, [x, y], pivot_ratios * np.array(frame.get_size()), -angle)
            self.animation.append(i)

        self.current_frame = self.animation[0]
        self.animation_counter = 0

    def update(self, walls, dt, all_bullets):
        current_movement = self.movement*dt
        collision = self.collision_test(walls)
        if collision:
            self.kill(all_bullets)
            all_bullets.remove(self)
        else:
            self.x += current_movement[0]
            self.y += current_movement[1]

        # ---- animation ----
        self.animation_counter += 1
        if self.animation_counter == len(self.animation):
            self.animation_counter = 0
        self.current_frame = self.animation[self.animation_counter]

    def collision_test(self, tiles):
        hit_list = []
        for tile in tiles:
            if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(tile):
                hit_list.append(tile)
        return hit_list

    def render(self, surface, camera_scroll):
        surface.blit(self.current_frame[0],
                     (self.x - camera_scroll[0], self.y - camera_scroll[1]))

    def kill(self, all_bullets): pass


class LightBullet(BulletEntity):

    def __init__(self, x, y, angle, velocity):
        animation = load_animation('../images/bullets/light', [1, 1, 1, 1, 1])
        super(LightBullet, self).__init__(x, y, angle, 8, 8, velocity, animation, [0.5, 0.5])


class MediumBullet(BulletEntity):

    def __init__(self, x, y, angle, velocity):
        animation = load_animation('../images/bullets/medium', [5, 5, 5, 5])
        super(MediumBullet, self).__init__(x, y, angle, 16, 16, velocity, animation, [0.5, 0.5])


class ShellBullet(BulletEntity):

    def __init__(self, x, y, angle, velocity, velocity_increase):
        animation = load_animation('../images/bullets/light', [1, 1, 1, 1, 1])
        super(ShellBullet, self).__init__(x, y, angle, 8, 8, velocity, animation, [0.5, 0.5])

        self.velocity = velocity
        self.angle = angle
        self.velocity_increase = velocity_increase

    def update(self, walls, dt, all_bullets):
        current_movement = self.movement*dt
        collision = self.collision_test(walls)
        if collision or self.velocity <= 0:
            all_bullets.remove(self)
        else:
            self.x += current_movement[0]
            self.y += current_movement[1]

        self.velocity = self.velocity + self.velocity_increase
        self.movement[0] = math.cos(math.radians(self.angle)) * self.velocity
        self.movement[1] = math.sin(math.radians(self.angle)) * self.velocity

        # ---- animation ----
        self.animation_counter += 1
        if self.animation_counter == len(self.animation):
            self.animation_counter = 0
        self.current_frame = self.animation[self.animation_counter]


class UnoBullet(BulletEntity):

    def __init__(self, x, y, angle, velocity, velocity_increase):
        animation = load_animation('../images/bullets/light', [1, 1, 1, 1, 1])
        super(UnoBullet, self).__init__(x, y, angle, 8, 8, velocity, animation, [0.5, 0.5])

        self.velocity = velocity
        self.angle = angle
        self.velocity_increase = velocity_increase
        self.start_velocity = velocity

    def update(self, walls, dt, all_bullets):
        current_movement = self.movement*dt
        collision = self.collision_test(walls)
        if collision:
            all_bullets.remove(self)
        else:
            self.x += current_movement[0]
            self.y += current_movement[1]

        self.velocity = self.velocity + self.velocity_increase
        self.movement[0] = math.cos(math.radians(self.angle)) * self.velocity
        self.movement[1] = math.sin(math.radians(self.angle)) * self.velocity

        # ---- animation ----
        self.animation_counter += 1
        if self.animation_counter == len(self.animation):
            self.animation_counter = 0
        self.current_frame = self.animation[self.animation_counter]


class RPGBullet(BulletEntity):
    def __init__(self, x, y, angle, velocity):
        animation = load_animation('../images/bullets/rpg', [5]*4)
        super(RPGBullet, self).__init__(x, y, angle, 20, 10, velocity, animation, [0, 0.5])

    def kill(self, all_bullets):
        all_bullets.append(effects.ExplosionEffect(self.x, self.y))


def rotate(image, pos, originPos, angle):
    image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    return rotated_image, rotated_image_rect


def load_animation(directory, frames_durations):
    animation = []
    dir_tree = os.listdir(directory)

    for idx, filename in enumerate(dir_tree):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            image = pygame.image.load(f'{directory}/{filename}').convert_alpha()
            for i in range(frames_durations[idx]):
                animation.append(image)
    return animation
