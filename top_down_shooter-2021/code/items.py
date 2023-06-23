import os
from abc import ABC, abstractmethod
import bullets

import pygame
import random

class Item(ABC):

    def __init__(self, animation):
        self.animation = animation
        self.default_frame = animation[0]
        self.current_frame = self.default_frame


class Pickupable:
    def __init__(self, x, y, item, angle=0):
        self.item = item
        self.angle = angle

        self.img = item.default_frame
        if not (-90 <= angle <= 90):
            self.img = pygame.transform.flip(self.img, False, True)
        self.img, self.rect = rotate(self.img, [x, y], [0, self.img.get_height() / 2], angle)


    def update(self, dt):
        pass

    def render(self, surface, camera_scroll):
        surface.blit(self.img,
                     (self.rect.x - camera_scroll[0], self.rect.y - camera_scroll[1]))

    def is_collision(self, rect):
        return self.rect.colliderect(rect)


class Gun(Item, ABC):
    @abstractmethod
    def __init__(self, animation, name, damage, fire_rate, cost, shooting_pivot):
        super(Gun, self).__init__(animation)
        self.name = name
        self.damage = damage
        self.fire_rate = fire_rate
        self.cost = cost
        self.desc = ''

        self.shooting_pivot = shooting_pivot

    def shoot(self, bullets_list, pivot, angle): pass

    def reload(self): pass


class OldShotgun(Gun):
    def __init__(self):
        img = pygame.image.load('../images/guns/old_shotgun.png').convert_alpha()
        super(OldShotgun, self).__init__([img], "Old Shotgun", 1, 0.8, 3, (35, 0))
        self.desc = "Grandpa's good old gun."

    def shoot(self, bullets_list, pivot, angle):
        speed = 200
        for i in range(7):
            offset = random.uniform(-20, 20)
            decrease = random.uniform(-4, -3)
            bullets_list.append(bullets.ShellBullet(pivot[0], pivot[1], angle+offset, speed, decrease))


class SniperShotgun(Gun):
    def __init__(self):
        img = pygame.image.load('../images/guns/sniper_shotgun.png').convert_alpha()
        super(SniperShotgun, self).__init__([img], "Sniper Shotgun", 1, 0.8, 3, (35, 0))
        self.desc = " Is it a sniper? Well yes but actually no."

    def shoot(self, bullets_list, pivot, angle):
        speed = 250
        for i in range(4):
            offset = random.uniform(-5, 5)
            decrease = random.uniform(-3, -1.5)
            bullets_list.append(bullets.ShellBullet(pivot[0], pivot[1], angle + offset, speed, decrease))


class AssaultRifle(Gun):
    def __init__(self):
        img = pygame.image.load('../images/guns/assault_rifle.png').convert_alpha()
        super(AssaultRifle, self).__init__([img], "Assault Rifle", 1, 3, 1, (38, 2))
        self.desc = "Tear your enemies apart!"

    def shoot(self, bullets_list, pivot, angle):
        speed = 200
        offset = random.uniform(-2, 2)
        bullets_list.append(bullets.MediumBullet(pivot[0], pivot[1], angle + offset, speed))


class RPG(Gun):
    def __init__(self):
        animation = load_animation('../images/guns/RPG', [1, 1])
        super(RPG, self).__init__(animation, "Assault Rifle", 8, 0.4, 6, (38, 2))
        self.desc = "Control the motion of explosion!"

    def shoot(self, bullets_list, pivot, angle):
        self.current_frame = self.animation[1]
        speed = 250
        offset = 0
        bullets_list.append(bullets.RPGBullet(pivot[0], pivot[1], angle + offset, speed))

    def reload(self):
        self.current_frame = self.animation[0]


class UnoShotgun(Gun):
    def __init__(self):
        img = pygame.image.load('../images/guns/uno_shotgun.png').convert_alpha()
        super(UnoShotgun, self).__init__([img], "Uno Shotgun", 1, 0.8, 3, (35, 0))
        self.desc = "Uno Reverse."

    def shoot(self, bullets_list, pivot, angle):
        speed = 200
        for i in range(7):
            offset = random.uniform(-20, 20)
            decrease = random.uniform(-4, -3)
            bullets_list.append(bullets.UnoBullet(pivot[0], pivot[1], angle+offset, speed, decrease))



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