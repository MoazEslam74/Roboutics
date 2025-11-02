import pygame

class Room_data:

    WIDTH=0
    BORDER_THICKNESS=0
    HEIGHT=0
    DOOR=0

    def __init__(self, width, border,height,door):
        self.WIDTH = width
        self.BORDER_THICKNESS = border
        self.HEIGHT=height
        self.DOOR=door
    first_floor_struct=[
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
