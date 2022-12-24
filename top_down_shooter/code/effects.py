import os
from abc import ABC, abstractmethod
import pygame


class VisualEffect(ABC):

    def __init__(self, x, y, width, height, animation, loop=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.animation = animation
        self.islooping = loop

        self.animation_counter = 0
        self.current_frame = self.animation[0]

    def update(self, walls, dt, animations):
        if self.animation_counter == len(self.animation):
            if self.islooping:
                self.animation_counter = 0
            else:
                animations.remove(self)
        else:
            self.current_frame = self.animation[self.animation_counter]
        self.animation_counter += 1

    def render(self, surface, camera_scroll):
        surface.blit(self.current_frame,
                     (self.rect.x - camera_scroll[0], self.rect.y - camera_scroll[1]))


class ExplosionEffect(VisualEffect):
    def __init__(self, x, y):
        duration = 0.8
        animation_length = 10
        animation = load_animation('../images/effects/explosion1', [int(duration*60)//animation_length] * animation_length)
        super(ExplosionEffect, self).__init__(x, y, 10, 10, animation)


def load_animation(directory, frames_durations):
    animation = []
    dir_tree = os.listdir(directory)

    for idx, filename in enumerate(dir_tree):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            image = pygame.image.load(f'{directory}/{filename}').convert_alpha()
            for i in range(frames_durations[idx]):
                animation.append(image)
    return animation