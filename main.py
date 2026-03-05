import pygame
import cupy as np
import random

WIDTH, HEIGHT = 800, 600
CELL_SIZE = 4  # each "pixel" is a 4x4 block
TOOLBAR_HEIGHT = 40
selected_material = 1
COLS = WIDTH // CELL_SIZE
ROWS = (HEIGHT - TOOLBAR_HEIGHT) // CELL_SIZE

#Uncoulped Physics approach
physics_timer = 0

materials = {
    1: {'name': "Sand",  'color': (194, 178, 128)},
    2: {'name': "Water", 'color': (116, 204, 244)},
    3: {'name': "Lava",  'color': (207, 70,  16 )},
    4: {'name': "Stone", 'color': (128, 128, 128)},
}

grid = np.zeros((ROWS, COLS), dtype=int)  # 0 = empty, 1 = sand, 2 = water
reset_button = pygame.Rect(WIDTH-90,5,80,30)

lava_timer = 0
lava_speed = 5

particulate_nature = {
    'sand':.8,
}

def draw_toolbar(screen):
    pygame.draw.rect(screen, (50, 50, 50), (0, 0, WIDTH, TOOLBAR_HEIGHT))

    pygame.draw.rect(screen,(200, 50, 50), reset_button)
    font = pygame.font.SysFont(None,20)
    text = font.render("Reset",True,(255,255,255))
    screen.blit(text,(WIDTH-75,13))
    
    for i, (mat_id, mat) in enumerate(materials.items()):
        x = 10 + i * 100
        color = mat['color']
        
        # highlight selected
        if mat_id == selected_material:
            pygame.draw.rect(screen, (255, 255, 255), (x-2, 4, 84, 32))
        
        pygame.draw.rect(screen, color, (x, 6, 80, 28))
        
        font = pygame.font.SysFont(None, 20)
        text = font.render(mat['name'], True, (0, 0, 0))
        screen.blit(text, (x + 5, 13))

def update_sand():
    # iterate bottom to top so sand falls correctly
    for row in range(ROWS - 2, -1, -1):
        for col in range(COLS):
            if grid[row][col] == 1:  # it's sand

                if random.random() > particulate_nature['sand']:
                    continue

                if grid[row+1][col] == 0:
                    grid[row+1][col] = 1
                    grid[row][col] = 0

                elif grid[row+1][col] == 2:
                    grid[row+1][col] = 1
                    grid[row][col] = 2

                else:
                    # try diagonal
                    dirs = [-1, 1]
                    random.shuffle(dirs)
                    for d in dirs:
                        if 0 <= col+d < COLS and grid[row+1][col+d] == 0:
                            grid[row+1][col+d] = 1
                            grid[row][col] = 0
                            break

                        elif 0 <= col+d < COLS and grid[row+1][col+d] == 2:
                                grid[row+1][col+d] = 1
                                grid[row][col] = 2
                                break


def update_water():
    for row in range(ROWS - 2, -1, -1):  # bottom to top
        for col in range(COLS):
            if grid[row][col] == 2:
                
                # rule 1: fall down
                if grid[row+1][col] == 0:
                    grid[row+1][col] = 2
                    grid[row][col] = 0
                
                # rule 2: spread sideways (both directions, pick random)
                else:
                    left = col - 1 >= 0 and grid[row][col-1] == 0
                    right = col + 1 < COLS and grid[row][col+1] == 0
                    
                    if left and right:
                        if random.random() < 0.5:
                            grid[row][col-1] = 2
                        else:
                            grid[row][col+1] = 2
                        grid[row][col] = 0
                    elif left:
                        grid[row][col-1] = 2
                        grid[row][col] = 0
                    elif right:
                        grid[row][col+1] = 2
                        grid[row][col] = 0

def update_lava():

    for row in range(ROWS - 2, -1, -1):  # bottom to top
        for col in range(COLS):
            if grid[row][col] == 3:
                
                # rule 1: fall down
                if grid[row+1][col] == 0:
                    grid[row+1][col] = 3
                    grid[row][col] = 0                    
                
                # rule 2: spread sideways (both directions, pick random)
                else:
                    left = col - 1 >= 0 and grid[row][col-1] == 0
                    right = col + 1 < COLS and grid[row][col+1] == 0
                    
                    if left and right:
                        if random.random() < 0.5:
                            grid[row][col-1] = 3
                        else:
                            grid[row][col+1] = 3
                        grid[row][col] = 0
                    elif left:
                        grid[row][col-1] = 3
                        grid[row][col] = 0
                    elif right:
                        grid[row][col+1] = 3
                        grid[row][col] = 0

def lava_water_interaction():
    for row in range(ROWS):
        for col in range(COLS):
            if grid[row][col] == 3:  # its lava
                # check all 4 neighbors
                for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        if grid[nr][nc] == 2:  # neighbor is water
                            grid[row][col] = 0  # destroy lava
                            grid[nr][nc] = 0    # destroy water

def draw_grid(screen):
    screen.fill((30, 30, 30))
    for row in range(ROWS):
        for col in range(COLS):
            mat_id = grid[row][col]
            if mat_id != 0:
                color = materials[mat_id]['color']
                pygame.draw.rect(screen, color,
                    (col * CELL_SIZE, row * CELL_SIZE + TOOLBAR_HEIGHT, CELL_SIZE, CELL_SIZE))
                
    draw_toolbar(screen)



pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
fpsFont = pygame.font.SysFont(None, 24)
reset_button = pygame.Rect(WIDTH-90, 5, 80, 30)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if my < TOOLBAR_HEIGHT:
                for i, mat_id in enumerate(materials.keys()):
                    x = 10 + i * 100
                    if x <= mx <= x + 80:
                        selected_material = mat_id
            if reset_button.collidepoint(mx, my):
                grid[:] = 0

    # outside event loop
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        if my > TOOLBAR_HEIGHT:
            col, row = mx // CELL_SIZE, my // CELL_SIZE
            for i in range(-2, 3):
                for j in range(-2, 3):
                    nc, nr = col+i, row+j
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        grid[nr][nc] = selected_material

    dt = clock.tick(0) / 1000
    physics_timer += dt
    if physics_timer >= 1/60:
        lava_timer += 1
        if lava_timer >= lava_speed:
            update_lava()
            lava_timer = 0
        update_sand()
        update_water()
        lava_water_interaction()
        physics_timer = 0

    draw_grid(screen)

    # fps counter inside loop
    fps = int(clock.get_fps())
    fps_text = fpsFont.render(f'FPS: {fps}', True, (255, 255, 255))
    screen.blit(fps_text, (WIDTH - 80, 48))

    pygame.display.flip()

pygame.quit()