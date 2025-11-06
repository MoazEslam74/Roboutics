import pygame
import math
class Dynamic_obstacle:
    def __init__(self, x, y, width, height, path_points, speed):
        self.rect = pygame.Rect(x, y, width, height)
        self.path_points = path_points
        self.speed = speed
        self.current_point_index = 0
        self.direction = 1  # 1 for forward, -1 for backward

    def move(self):
        target_point = self.path_points[self.current_point_index]
        dx = target_point[0] - self.rect.x
        dy = target_point[1] - self.rect.y
        distance = math.hypot(dx, dy)

        if distance < self.speed:
            self.rect.x, self.rect.y = target_point
            self.current_point_index += self.direction
            if self.current_point_index >= len(self.path_points) or self.current_point_index < 0:
                self.direction *= -1
                self.current_point_index += self.direction * 2
        else:
            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed