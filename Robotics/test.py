import pygame
import sys
import math
import random
import heapq
from collections import deque

from Robot import Robot
from Room_data import Room_data

# ---------------- window & colors ----------------
WIDTH, HEIGHT = 700, 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 30, 30)
BLUE = (30, 60, 220)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Hospital robot + Value Iteration (improved)")
clock = pygame.time.Clock()

# ---------------- room & sprites ----------------
BORDER_THICKNESS = 10
DOOR = 60

r1 = Room_data(WIDTH, BORDER_THICKNESS, HEIGHT, DOOR)
base_obstacles = r1.first_floor_struct
obj_obstacles_template = r1.obj_obstacles_first_floor

robot_imgs = Robot.robot_imgs
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

def draw_target(surface, x, y):
    pygame.draw.circle(surface, (255, 0, 0), (x + 20, y + 20), 10)

# ---------------- grid + VI params ----------------
CELL_SIZE = 45                 # حجم الخلية - غيّره لو تحب دقة أعلى/أقل
COLS = max(1, WIDTH // CELL_SIZE)
ROWS = max(1, HEIGHT // CELL_SIZE)

ACTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # up,right,down,left
GAMMA = 0.9
STEP_REWARD = -0.04
GOAL_REWARD = +1.0
OBSTACLE_REWARD = -1.0

# سرعة وحجم الروبوت
speed = 4
robot_size = 40

# parameters to tune (حلول المشاكل)
BIAS_ALPHA = 0.7           # وزن الـV مقابل البُعد للمسافة: alpha*V + (1-alpha)*(-dist)
VISITED_PENALTY = 0.10     # خصم صغير لقيمة الخلايا التي زُرت مؤخراً (لتقليل اللف)
VISITED_WINDOW = 30        # عدد النقاط الأخيرة التي نعتبرها "مُزارة مؤخراً"
RECOMPUTE_EVERY_FRAMES = 8 # كل كم فريم نعيد حساب VI
VI_ITERATIONS = 80         # iter في Value Iteration
STUCK_FRAMES_THRESHOLD = 18  # لو محبوس طول ده من الفريمات نشغّل A*

# ---------------- state variables ----------------
robot_x = WIDTH // 2
robot_y = HEIGHT // 2
start_pos = (robot_x, robot_y)

target_x = None
target_y = None

angle = 0

path_history = []       # مسار المرور (مراكز نقاط)
returning = False

# نستخدم زيارة خلايا لتجنب الدوران (recent visited)
recent_cells = deque(maxlen=VISITED_WINDOW)

# عداد للـ stuck detection (لو ما في تقدم)
frames_no_progress = 0
last_progress_pos = (robot_x, robot_y)

# ---------------- helpers ----------------
def build_obstacles():
    """نبني قائمة عوائق (Rect) من templates و base_obstacles"""
    obs = []
    for r in base_obstacles:
        obs.append(pygame.Rect(r.left, r.top, r.width, r.height))
    for i in range(len(obj_obstacles_template)):
        bed_img = obj_obstacles_template[i][0].convert_alpha()
        bed_img = pygame.transform.scale(bed_img, obj_obstacles_template[i][1])
        bed_x, bed_y = obj_obstacles_template[i][2]
        bed_rect = pygame.Rect(bed_x, bed_y, bed_img.get_width()-20, bed_img.get_height())
        obs.append(bed_rect)
    return obs

def pos_to_cell(x, y):
    c = int((x + robot_size/2) // CELL_SIZE)
    r = int((y + robot_size/2) // CELL_SIZE)
    c = max(0, min(COLS-1, c)); r = max(0, min(ROWS-1, r))
    return (c, r)

def cell_center(c, r):
    left = c * CELL_SIZE; top = r * CELL_SIZE
    return (int(left + CELL_SIZE/2), int(top + CELL_SIZE/2))

def is_cell_blocked_center(c, r, obstacles_list):
    """نستخدم اختبار مركز الخلية (أخف) بدل كامل الخلية لمنع حجب ممرات ضيقة"""
    cx, cy = cell_center(c, r)
    point_rect = pygame.Rect(cx-2, cy-2, 4, 4)
    for obs in obstacles_list:
        if point_rect.colliderect(obs):
            return True
    return False

# ---------------- Value Iteration ----------------
def value_iteration(obstacles_list, goal_cell, iterations=VI_ITERATIONS, tol=1e-4):
    blocked = [[False for _ in range(COLS)] for _ in range(ROWS)]
    V = [[0.0 for _ in range(COLS)] for _ in range(ROWS)]
    # علامة الخلايا المحجوبة
    for r in range(ROWS):
        for c in range(COLS):
            if is_cell_blocked_center(c, r, obstacles_list):
                blocked[r][c] = True
                V[r][c] = OBSTACLE_REWARD
    gx, gy = goal_cell
    if 0 <= gx < COLS and 0 <= gy < ROWS:
        V[gy][gx] = GOAL_REWARD

    for it in range(iterations):
        delta = 0.0
        newV = [row[:] for row in V]
        for r in range(ROWS):
            for c in range(COLS):
                if blocked[r][c]: continue
                if (c, r) == (gx, gy):
                    newV[r][c] = GOAL_REWARD; continue
                best = -1e9
                for (dx, dy) in ACTIONS:
                    nc, nr = c + dx, r + dy
                    if not (0 <= nc < COLS and 0 <= nr < ROWS):
                        val = STEP_REWARD + GAMMA * V[r][c]
                    else:
                        if blocked[nr][nc]:
                            val = STEP_REWARD + OBSTACLE_REWARD + GAMMA * V[nr][nc]
                        else:
                            val = STEP_REWARD + GAMMA * V[nr][nc]
                    if val > best: best = val
                newV[r][c] = best
                delta = max(delta, abs(newV[r][c] - V[r][c]))
        V = newV
        if delta < tol: break
    return V, blocked

# ---------------- collision & angular fallback ----------------
def will_collide(next_x, next_y, obstacles_list):
    robot_rect = pygame.Rect(int(next_x), int(next_y), robot_size-1, robot_size-1)
    for obs in obstacles_list:
        if robot_rect.colliderect(obs):
            return True
    return False

def get_path_angular(x, y, dx, dy, obstacles_list, attempts=12):
    base_angle = math.atan2(dy, dx)
    for i in range(1, attempts+1):
        for sign in [1, -1]:
            new_angle = base_angle + math.radians(sign * i * 15)
            new_dx = math.cos(new_angle); new_dy = math.sin(new_angle)
            new_x = x + new_dx * CELL_SIZE; new_y = y + new_dy * CELL_SIZE
            if not will_collide(new_x, new_y, obstacles_list):
                return new_x, new_y
    return x, y

# ---------------- A* on grid as strong fallback ----------------
def a_star_grid(start, goal, blocked):
    """A* returns list of cells from start to goal or None.
       blocked is 2D boolean blocked[r][c].
    """
    sx, sy = start; gx, gy = goal
    if blocked[sy][sx] or blocked[gy][gx]:
        return None
    open_heap = []
    heapq.heappush(open_heap, (0 + heuristic(start, goal), 0, start, None))
    came_from = {}
    gscore = {start: 0}
    while open_heap:
        f, g, current, parent = heapq.heappop(open_heap)
        if current in came_from: continue
        came_from[current] = parent
        if current == goal:
            # reconstruct
            path = []
            cur = current
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return path
        cx, cy = current
        for dx, dy in ACTIONS:
            nc, nr = cx + dx, cy + dy
            if not (0 <= nc < COLS and 0 <= nr < ROWS): continue
            if blocked[nr][nc]: continue
            tentative_g = g + 1
            ns = (nc, nr)
            if tentative_g < gscore.get(ns, 1e9):
                gscore[ns] = tentative_g
                fscore = tentative_g + heuristic(ns, goal)
                heapq.heappush(open_heap, (fscore, tentative_g, ns, current))
    return None

def heuristic(a, b):
    # Manhattan distance on grid (sufficient)
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ---------------- bookkeeping ----------------
frame_count = 0
last_obstacles_signature = None
current_V = None
current_blocked = None
forced_astar_path = None  # إذا وضعنا مسار A* سنتبعه

# ---------------- main loop ----------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_F11, pygame.K_m):
            # full screen toggle
            fullscreen = not pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
            if fullscreen:
                info = pygame.display.Info()
                screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            target_x, target_y = mx - robot_size//2, my - robot_size//2
            returning = False
            path_history = []
            recent_cells.clear()
            forced_astar_path = None
            current_V = None  # force recompute

    # build current obstacles list
    obstacles = build_obstacles()

    # draw background & obstacles
    screen.fill(WHITE)
    pygame.draw.circle(screen, (0, 255, 0), (356, 640), 20)
    for obs in obstacles:
        pygame.draw.rect(screen, BLACK, obs)
    # draw object sprites
    for i in range(len(obj_obstacles_template)):
        bed_img = obj_obstacles_template[i][0]
        bed_rect = bed_img.get_rect(topleft=(obj_obstacles_template[i][2]))
        screen.blit(bed_img, bed_rect)

    frame_count += 1
    recompute = False

    # decide whether recompute VI: if target exists
    if target_x is not None and target_y is not None:
        sig = tuple((o.left, o.top, o.width, o.height) for o in obstacles)
        if sig != last_obstacles_signature:
            recompute = True
            last_obstacles_signature = sig
        if current_V is None or (frame_count % RECOMPUTE_EVERY_FRAMES == 0):
            recompute = True
        if recompute:
            goal_cell = pos_to_cell(target_x, target_y)
            current_V, current_blocked = value_iteration(obstacles, goal_cell, iterations=VI_ITERATIONS)
            forced_astar_path = None  # reset
    else:
        current_V = None
        current_blocked = None
        last_obstacles_signature = None

    # ----- Movement logic -----
    frame_moved = False

    # If we have a forced A* path (fallback), follow it first
    if forced_astar_path and len(forced_astar_path) > 1:
        # get next waypoint cell
        next_cell = forced_astar_path[1]  # index 0 is current
        wx, wy = cell_center(next_cell[0], next_cell[1])
        dx = wx - (robot_x + robot_size/2); dy = wy - (robot_y + robot_size/2)
        dist = math.hypot(dx, dy)
        if dist > 0:
            stepx = (dx / dist) * speed; stepy = (dy / dist) * speed
            if not will_collide(robot_x + stepx, robot_y + stepy, obstacles):
                robot_x += stepx; robot_y += stepy; frame_moved = True
            else:
                # if blocked while following A*, drop forced path to allow replan
                forced_astar_path = None
        # if reached center of that cell, pop it
        if dist <= speed:
            forced_astar_path.pop(0)
            frame_moved = True

    # Normal VI-guided movement
    elif target_x is not None and target_y is not None and current_V is not None:
        cur_cell = pos_to_cell(robot_x, robot_y)
        cx, cy = cur_cell

        # Choose best neighbor using combined score:
        best = None; best_score = -1e9
        # compute direct vector to actual target center
        tx_center = target_x + robot_size/2; ty_center = target_y + robot_size/2
        for (dx_cell, dy_cell) in ACTIONS:
            nc, nr = cx + dx_cell, cy + dy_cell
            if not (0 <= nc < COLS and 0 <= nr < ROWS): continue
            if current_blocked and current_blocked[nr][nc]:
                continue
            Vval = current_V[nr][nc]
            # distance from candidate cell center to actual target (euclidean)
            ccx, ccy = cell_center(nc, nr)
            dist_to_goal = math.hypot(ccx - tx_center, ccy - ty_center)
            # visited penalty if this cell was visited recently
            visited_pen = 0.0
            if (nc, nr) in recent_cells:
                visited_pen = VISITED_PENALTY
            # Combined score (higher is better). tune BIAS_ALPHA
            score = BIAS_ALPHA * Vval + (1.0 - BIAS_ALPHA) * (-dist_to_goal / max(WIDTH, HEIGHT)) - visited_pen
            if score > best_score:
                best_score = score; best = (nc, nr)

        # if no best found (maybe all neighbors blocked), try A* from current cell to goal
        if best is None:
            start_cell = cur_cell
            goal_cell = pos_to_cell(target_x, target_y)
            # run A* on current_blocked grid
            if current_blocked is not None:
                path = a_star_grid(start_cell, goal_cell, current_blocked)
                if path:
                    forced_astar_path = path  # follow it next frames
                else:
                    # last fallback: direct angular movement (old method)
                    dx = target_x - robot_x; dy = target_y - robot_y
                    altx, alty = get_path_angular(robot_x, robot_y, dx, dy, obstacles)
                    if (altx, alty) != (robot_x, robot_y):
                        robot_x += (altx - robot_x) * 0.35; robot_y += (alty - robot_y) * 0.35
                        frame_moved = True
            else:
                # If no grid info, try angular fallback
                dx = target_x - robot_x; dy = target_y - robot_y
                altx, alty = get_path_angular(robot_x, robot_y, dx, dy, obstacles)
                if (altx, alty) != (robot_x, robot_y):
                    robot_x += (altx - robot_x) * 0.35; robot_y += (alty - robot_y) * 0.35
                    frame_moved = True
        else:
            # Move towards center of best cell (combine slightly with true target to avoid local loops)
            nx_center, ny_center = cell_center(best[0], best[1])
            dx = nx_center - (robot_x + robot_size/2); dy = ny_center - (robot_y + robot_size/2)
            # add small bias toward exact pixel-target to avoid unnatural detours
            bias_pixel = 0.18
            dx += bias_pixel * (target_x - robot_x); dy += bias_pixel * (target_y - robot_y)

            dist = math.hypot(dx, dy)
            if dist > 0:
                stepx = (dx / dist) * speed; stepy = (dy / dist) * speed
            else:
                stepx = stepy = 0
            next_x = robot_x + stepx; next_y = robot_y + stepy
            angle = (math.degrees(math.atan2(dy, dx)) + 360) % 360

            if not will_collide(next_x, next_y, obstacles):
                robot_x, robot_y = next_x, next_y
                frame_moved = True
                # record visited cell
                recent_cells.append((best[0], best[1]))
                # record pixel center to history
                path_history.append((int(robot_x + robot_size/2), int(robot_y + robot_size/2)))
            else:
                # collision: try angular fallback first
                altx, alty = get_path_angular(robot_x, robot_y, target_x - robot_x, target_y - robot_y, obstacles)
                if (altx, alty) != (robot_x, robot_y):
                    robot_x += (altx - robot_x) * 0.35; robot_y += (alty - robot_y) * 0.35
                    path_history.append((int(robot_x + robot_size/2), int(robot_y + robot_size/2)))
                    frame_moved = True
                else:
                    # if still stuck, run A* planning
                    start_cell = cur_cell
                    goal_cell = pos_to_cell(target_x, target_y)
                    if current_blocked is not None:
                        path = a_star_grid(start_cell, goal_cell, current_blocked)
                        if path:
                            forced_astar_path = path
                        # else remain in place this frame

        # check arrival
        if math.hypot((robot_x - target_x), (robot_y - target_y)) <= speed:
            path_history.append((int(target_x + robot_size/2), int(target_y + robot_size/2)))
            returning = True
            target_x, target_y = None, None
            forced_astar_path = None

    # ----- Returning along path_history (reverse) -----
    elif returning and len(path_history) > 0:
        next_pt = path_history[-1]
        dx = next_pt[0] - (robot_x + robot_size/2)
        dy = next_pt[1] - (robot_y + robot_size/2)
        dist = math.hypot(dx, dy)
        if dist > 0:
            stepx = (dx / dist) * speed; stepy = (dy / dist) * speed
            if not will_collide(robot_x + stepx, robot_y + stepy, obstacles):
                robot_x += stepx; robot_y += stepy
            else:
                altx, alty = get_path_angular(robot_x, robot_y, dx, dy, obstacles)
                if (altx, alty) != (robot_x, robot_y):
                    robot_x += (altx - robot_x) * 0.35; robot_y += (alty - robot_y) * 0.35
        if dist <= speed:
            path_history.pop()
        if len(path_history) == 0:
            returning = False
            robot_x, robot_y = start_pos

    # ----- stuck detection: إذا ما تقدّمش لفترة نشغّل A* -----
    if frame_moved:
        frames_no_progress = 0
        last_progress_pos = (robot_x, robot_y)
    else:
        frames_no_progress += 1
    if frames_no_progress >= STUCK_FRAMES_THRESHOLD and target_x is not None and current_blocked is not None:
        # force A* planning
        start_cell = pos_to_cell(robot_x, robot_y)
        goal_cell = pos_to_cell(target_x, target_y)
        path = a_star_grid(start_cell, goal_cell, current_blocked)
        if path:
            forced_astar_path = path
            frames_no_progress = 0
        else:
            # can't find path - maybe goal blocked; cancel target
            target_x, target_y = None, None
            returning = True

    # ----- draw path history (red) and optionally V heatmap small overlay -----
    if len(path_history) > 1:
        pygame.draw.lines(screen, RED, False, path_history, 3)
    # optionally: draw recent visited cell markers
    for ccell in recent_cells:
        cc = cell_center(ccell[0], ccell[1])
        pygame.draw.circle(screen, (200,200,0), cc, 3)

    # draw target & robot
    if target_x is not None and target_y is not None:
        draw_target(screen, int(target_x), int(target_y))
    draw_robot(screen, int(robot_x), int(robot_y), angle)

    # room change as original
    if robot_x >= 326 and robot_x <= 386 and robot_y >= 610 and robot_y <= 670:
        screen.fill(WHITE)
        base_obstacles = r1.emergency_floor_struct
        obj_obstacles_template = r1.obj_obstacles_emergency_floor
        robot_x = WIDTH - 150
        robot_y = HEIGHT - 150
        target_x, target_y = None, None
        path_history = []
        returning = False
        current_V = None
        last_obstacles_signature = None
        forced_astar_path = None

    pygame.display.update()
    clock.tick(30)
