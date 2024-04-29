import pygame as pg
from PlaneInSpace import Plane
from Maze3D import Maze
import sys
import numpy as np
import time
from PIL import Image

N = 3
SCALE = 10
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

def draw_pic(screen:pg.Surface, screen_array:np.ndarray, target:int, source_img:pg.Surface):
    draw_array = screen_array.copy()
    draw_array[draw_array == np.int16(target)] = 255
    draw_array[draw_array != np.int16(255)] = 0
    
    surf = pg.surfarray.make_surface(draw_array).convert_alpha()
    mask = pg.mask.from_threshold(surf, color=(255, 255, 255, 255), threshold=(1, 1, 1, 255))
    
    img = mask.to_surface(setsurface=source_img, unsetcolor=(0, 0, 0, 0)).convert_alpha()
    screen.blit(img, (0, 0))
    
    
def ScreenDraw(screen:pg.Surface, maze:Maze, plane:Plane, cPos:list, l:int, points:set):  
    screen.fill("#FFFFFF")
    screen_array = np.full((SCREEN_WIDTH, SCREEN_HEIGHT), fill_value=-1,dtype='int16')
    
    center = np.array(cPos[:2])
    
    for p in points:
        pos = np.array(p)
        vector = pos-center
        x = (vector[0]**2+vector[1]**2)**0.5
        
        if x == 0:
            pass
        
        if x > SCREEN_WIDTH//2: continue
        if plane.normal_vector[0]*vector[1]<plane.normal_vector[1]*vector[0]: x = -x
        x = SCREEN_WIDTH//2+int(x)
        
        for z in range(min(l, SCREEN_HEIGHT//SCALE)):
            pArray = (p[0]//SCALE, p[1]//SCALE, z)
            
            y = SCREEN_HEIGHT//2+int(z*SCALE-cPos[2])
            
            if (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
                screen_array[x, y:y+SCALE] = maze.array[pArray]
    
    draw_pic(screen, screen_array, 1, wall_img)
    draw_pic(screen, screen_array, 0, path_img)
    draw_pic(screen, screen_array, 2, start_img)
    draw_pic(screen, screen_array, 9, end_img)
    
def getRightVector(plane:Plane, step:int):
    v = np.cross((0, 0, 1), plane.normal_vector)
    v = v*step/np.sum(v**2)**0.5
    v =  v.astype(int)
    
    return v

def get_pic(filename:str):
    screen_ratio = SCREEN_HEIGHT/SCREEN_WIDTH
    pil_img = Image.open(fr"source/{filename}.png")
    img_ratio = pil_img.size[1]/pil_img.size[0]

    if screen_ratio > img_ratio:
        height = SCREEN_HEIGHT
        width = height/img_ratio
    else:
        width = SCREEN_WIDTH
        height = width*img_ratio
        
    width, height = int(width), int(height)
    pil_img = pil_img.resize((width, height))
    pil_img = pil_img.crop((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    pg_img = pg.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()
    return pg_img

# Pygame初始化
pg.init()
pg.display.set_caption("在二維上的三維迷宮")

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
screen.fill("#FFFFFF")
pg.display.update()
FPS = 30
CLOCK = pg.time.Clock()

# 遊戲物件初始化
l = N*6+1
maze = Maze(N)
cPos = np.array([3*SCALE, 3*SCALE, 3*SCALE])
plane = Plane(cPos, (10, -10, 0))
points = plane.get_points_on_plane(l*SCALE-1)

# 建立背景
wall_img = get_pic("brick_wall")
path_img = get_pic("dirt_path")
end_img = get_pic("diamond_block")
start_img = get_pic("emerald_block")

# 遊戲主體
run = True
while run:
    rotate = 0
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.MOUSEWHEEL:
            if event.y: rotate = event.y
            
    keys_pressed = pg.key.get_pressed()
    mouse_pressed = pg.mouse.get_pressed()
    w, a, s, d = keys_pressed[pg.K_w],keys_pressed[pg.K_a],keys_pressed[pg.K_s],keys_pressed[pg.K_d]
    
    if not rotate: 
        toUP = 0
        toRIGHT = 0
        if w: toUP -= 1
        if s: toUP += 1
        if d: toRIGHT += 1
        if a: toRIGHT -= 1
        
        if toUP or toRIGHT:
            step = 0
            while step < SCALE:
                last = next
                next = cPos+getRightVector(plane, step)*toRIGHT+(0, 0, step*toUP)
                
                direction = ((1, 0), (0, 1), (0, -1), (-1, 0))
                if tuple(next[:2]) not in points:
                    for d in direction:
                        if tuple(next[:2]+d) in points:
                            next[:2] = next[:2]+d
                            break
                    else:
                        next = last
                        break
                
                if maze.array[tuple(next//SCALE)] == 9:
                    run = False
                    break
                
                if maze.array[tuple(next//SCALE)] != 1:
                    step += 1
                    continue
                step -= 1
                next = last
                break
            if step:
                cPos = next
                
    
    if not any((w, a, s, d)):
        
        if rotate: 
            plane.rotateZ(2*rotate, cPos)
            points = plane.get_points_on_plane(l*SCALE-1)
    
    ScreenDraw(screen, maze, plane, cPos, l, points)
    pg.draw.rect(screen, "red", ((SCREEN_WIDTH-SCALE)//2, (SCREEN_HEIGHT-SCALE)//2, SCALE, SCALE))
    
    pg.display.update()
    CLOCK.tick(FPS)
    print("FPS:", round(CLOCK.get_fps()))