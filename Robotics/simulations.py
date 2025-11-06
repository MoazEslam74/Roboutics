import pygame
import sys
import math

from Robot import Robot
from Room_data import Room_data

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
    print("Target drawn at:", x, y)

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

def get_path(x, y, dx, dy, attempts=10):
    step_angle = 30  #look at every 30 degrees
    for i in range(attempts):
        # rotate right
        angle_r = math.atan2(dy, dx) - math.radians(step_angle * (i + 1))
        new_dx = math.cos(angle_r)
        new_dy = math.sin(angle_r)
        new_x = x + new_dx * 40
        new_y = y + new_dy * 40
        if not will_collide(new_x, new_y):
            return new_x, new_y
        # rotate left
        angle_l = math.atan2(dy, dx) + math.radians(step_angle * (i + 1))
        new_dx = math.cos(angle_l)
        new_dy = math.sin(angle_l)
        new_x = x + new_dx * 40
        new_y = y + new_dy * 40
        if not will_collide(new_x, new_y):
            return new_x, new_y
    return x, y  # no alternative path found yet

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_F11, pygame.K_m):
            fullscreen = not fullscreen
            if fullscreen:
                info = pygame.display.Info()
                screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            target_x, target_y = mx - 20, my - 20
    
    screen.fill(WHITE)
    pygame.draw.circle(screen, (0, 255, 0), (356, 640), 20)
    

    for obs in obstacles:
        pygame.draw.rect(screen, BLACK, obs)

    for i in range(len(obj_obstacles)):
        bed_img = obj_obstacles[i][0].convert_alpha()
        bed_img = pygame.transform.scale(bed_img, obj_obstacles[i][1])

    #position of the obstacle
        bed_x, bed_y = obj_obstacles[i][2]
        bed_rect = pygame.Rect(bed_x, bed_y, bed_img.get_width()-20, bed_img.get_height())
        obstacles.append(bed_rect)
    
    for i in range(len(obj_obstacles)):
        bed_img = obj_obstacles[i][0]
        bed_rect = bed_img.get_rect(topleft=(obj_obstacles[i][2]))
        screen.blit(bed_img, bed_rect)

    if target_x is not None and target_y is not None:
        dx = (target_x) - robot_x
        dy = (target_y) - robot_y
        distance = math.hypot(dx, dy)

        if distance > 0:
            angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360

        if distance > speed:
            next_x = robot_x + dx / distance * speed
            next_y = robot_y + dy / distance * speed

            if not will_collide(next_x, next_y):
                robot_x, robot_y = next_x, next_y
            else:
                # Obstacle detected, try to find alternative path
                new_x, new_y = get_path(robot_x, robot_y, dx, dy)
                if (new_x, new_y) != (robot_x, robot_y):
                    robot_x, robot_y = new_x, new_y
        else:
            robot_x, robot_y = target_x, target_y
            target_x, target_y = None, None

        if target_x is not None:
            draw_target(screen, int(target_x), int(target_y))

    draw_robot(screen, int(robot_x), int(robot_y), angle)
    if robot_x >=326 and robot_x <=386 and robot_y >=610 and robot_y <=670:
        screen.fill(WHITE)
        obstacles= r1.emergency_floor_struct
        obj_obstacles= r1.obj_obstacles_emergency_floor
        robot_x = WIDTH -150
        robot_y = HEIGHT -150
        target_x = None
        target_y = None


    pygame.display.update()
    clock.tick(30)
