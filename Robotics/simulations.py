import pygame
import sys
import math

#size of the window
WIDTH, HEIGHT = 700, 700

#colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
# create resizable window so OS maximize button works
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hospital robot simulation")
clock = pygame.time.Clock()

# track fullscreen state
fullscreen = False

#robot images
robot_img_up = pygame.image.load("images/up_robot.png")
robot_img_down = pygame.image.load("images/down_robot.png")
robot_img_left = pygame.image.load("images/left_robot.png")
robot_img_right = pygame.image.load("images/right_robot.png")
robot_img_up_right = pygame.image.load("images/up_right_robot.png")
robot_img_up_left = pygame.image.load("images/up_left_robot.png")
robot_img_down_right = pygame.image.load("images/down_right_robot.png")
robot_img_down_left = pygame.image.load("images/down_left_robot.png")

# Resize if needed
robot_imgs = [robot_img_up, robot_img_down, robot_img_left, robot_img_right,
              robot_img_up_right, robot_img_up_left, robot_img_down_right, robot_img_down_left]
for i in range(len(robot_imgs)):
    robot_imgs[i] = pygame.transform.scale(robot_imgs[i], (40, 40))

#robot drawing function
def draw_robot(surface, x, y, angle):
    if 22.5 < angle <= 67.5:
        surface.blit(robot_imgs[6], (x, y))  # down-right
    elif 67.5 < angle <= 112.5:
        surface.blit(robot_imgs[1], (x, y))  # down
    elif 112.5 < angle <= 157.5:
        surface.blit(robot_imgs[7], (x, y))  # down-left
    elif 157.5 < angle <= 202.5:
        surface.blit(robot_imgs[2], (x, y))  # left
    elif 202.5 < angle <= 247.5:
        surface.blit(robot_imgs[5], (x, y))  # up-left
    elif 247.5 < angle <= 292.5:
        surface.blit(robot_imgs[0], (x, y))  # up
    elif 292.5 < angle <= 337.5:
        surface.blit(robot_imgs[4], (x, y))  # up-right
    else:
        surface.blit(robot_imgs[3], (x, y))  # right

# Create obstacle rectangles for borders
BORDER_THICKNESS = 10
DOOR=60
WALL_THICKNESS=15
obstacles = [
    pygame.Rect(0, 0, WIDTH, BORDER_THICKNESS),  # Top
    pygame.Rect(0, 0, BORDER_THICKNESS, HEIGHT),  # Left
    pygame.Rect(0, HEIGHT - BORDER_THICKNESS, WIDTH, BORDER_THICKNESS),  # Bottom
    pygame.Rect(WIDTH - BORDER_THICKNESS, 0, BORDER_THICKNESS, HEIGHT), # Right
    pygame.Rect(WIDTH/4, 0, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH/4, HEIGHT/4 + DOOR, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH/4, HEIGHT/2 + 2*DOOR, BORDER_THICKNESS, HEIGHT/5), # wall vertical
    pygame.Rect(0, HEIGHT/4+DOOR, WIDTH/4, BORDER_THICKNESS), # wall horizontal
    pygame.Rect(0, 2*(HEIGHT/4+DOOR), WIDTH/4, BORDER_THICKNESS), # wall horizontal

    pygame.Rect(WIDTH*3/4,0, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH*3/4, HEIGHT/4 + DOOR, BORDER_THICKNESS, HEIGHT/4), # wall vertical
    pygame.Rect(WIDTH*3/4, HEIGHT/2 + 2*DOOR, BORDER_THICKNESS, HEIGHT/5), # wall vertical
    pygame.Rect(WIDTH*3/4, HEIGHT/4+DOOR, WIDTH/4, BORDER_THICKNESS), # wall horizontal
    pygame.Rect(WIDTH*3/4, 2*(HEIGHT/4+DOOR), WIDTH/4, BORDER_THICKNESS) # wall horizontal
]

#draw target
def draw_target(surface, x, y):
    pygame.draw.circle(surface, (255, 0, 0), (x + 20, y + 20), 10)

# Robot initial position
robot_x = WIDTH // 2
robot_y = HEIGHT // 2
target_x = None
target_y = None
angle = 0
speed = 4
# Collision detection
def will_collide(next_x, next_y):
    robot_rect = pygame.Rect(next_x, next_y, 40, 40)
    for obs in obstacles:
        if robot_rect.colliderect(obs):
            return True
    return False

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # toggle fullscreen / maximize
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

    # Draw obstacles (borders)
    for obs in obstacles:
        pygame.draw.rect(screen, BLACK, obs)

    # If we have a target, move step-by-step toward it
    if target_x is not None and target_y is not None:
        dx = (target_x) - robot_x
        dy = (target_y) - robot_y
        distance = math.hypot(dx, dy)
        if distance > 0:
            angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360

        if distance > speed:
            next_x = robot_x + dx / distance * speed
            next_y = robot_y + dy / distance * speed

            # check collision before moving
            if not will_collide(next_x, next_y):
                robot_x, robot_y = next_x, next_y
            else:
                # stop if hitting border
                target_x, target_y = None, None
        else:
            robot_x, robot_y = target_x, target_y
            target_x, target_y = None, None

        if target_x is not None:
            draw_target(screen, int(target_x), int(target_y))

    draw_robot(screen, int(robot_x), int(robot_y), angle)

    pygame.display.update()
    clock.tick(30)
