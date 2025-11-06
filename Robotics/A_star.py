import pygame
import sys
import math

from Robot import Robot
from Room_data import Room_data
from PriorityQueue import PriorityQueue as priority_queue
#size of the window
WIDTH, HEIGHT = 700, 700

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BORDER_THICKNESS = 10
DOOR = 60
WALL_THICKNESS = 15

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hospital robot simulation")
clock = pygame.time.Clock()

fullscreen = False
robot_imgs = Robot.robot_imgs

r1 = Room_data(WIDTH, BORDER_THICKNESS, HEIGHT, DOOR)
obstacles = r1.first_floor_struct
obj_obstacles = r1.obj_obstacles_first_floor




for i in range(len(robot_imgs)):
    robot_imgs[i] = pygame.transform.scale(robot_imgs[i], (40, 40))

def draw_robot(surface, x, y, angle):
    if 22.5 < angle <= 67.5:
        surface.blit(robot_imgs[6], (x, y))
    elif 67.5 < angle <= 112.5:
        surface.blit(robot_imgs[1], (x, y))
    elif 112.5 < angle <= 157.5:
        surface.blit(robot_imgs[7], (x, y))
    elif 157.5 < angle <= 202.5:
        surface.blit(robot_imgs[2], (x, y))
    elif 202.5 < angle <= 247.5:
        surface.blit(robot_imgs[5], (x, y))
    elif 247.5 < angle <= 292.5:
        surface.blit(robot_imgs[0], (x, y))
    elif 292.5 < angle <= 337.5:
        surface.blit(robot_imgs[4], (x, y))
    else:
        surface.blit(robot_imgs[3], (x, y))

# Create obstacles


def draw_target(surface, x, y):
    pygame.draw.circle(surface, (255, 0, 0), (x + 20, y + 20), 10)

robot_x = WIDTH // 2
robot_y = HEIGHT // 2
target_x = None
target_y = None
angle = 0
speed = 4

def will_collide(next_x, next_y):
    robot_rect = pygame.Rect(next_x, next_y, 40, 40)
    for obs in obstacles:
        if robot_rect.colliderect(obs):
            return True
    return False


Goal = [[4, (637, 33)], [3, (47, 302)], [1, (646, 279)], [5, (57,52)], [0, (45, 528)], [2, (636, 513)]]

def AStar(Goal, start):
    open_set=priority_queue()
    
    for i in range(len(Goal)):
        open_set.push(Goal[i][1], Goal[i][0])
    robot_x, robot_y = start
    x,y=priority_queue.pop_lowest_f()
    GScore = distance(robot_x, robot_y, x, y)

def distance(robot_x, robot_y, x, y):
    return math.sqrt((robot_x - x) ** 2 + (robot_y - y) ** 2)


def move(start, goal, speed):
    directions = [[1, 0], [-1, 0], [0, 1], [0, -1]]
    neighbours = []
    min_heurstic=100000
    heurstic_x=0
    heurstic_y=0
    nextPosititon=start
    while nextPosititon!=(goal[0],goal[1]):
        for i in range(directions):
            position_x=nextPosititon[0]+(directions[i][0]*speed)
            position_y=nextPosititon[1]+(directions[i][1]*speed)
            if not will_collide(position_x,position_y):
                x,y=goal
                if distance(position_x, position_y,x,y)<min_heurstic:
                    min_heurstic = distance(position_x, position_y,x,y)
                    heurstic_x=position_x
                    heurstic_y=position_y
                    nextPosititon=(heurstic_x,heurstic_y)  
            neighbours.append([heurstic_x,heurstic_y])