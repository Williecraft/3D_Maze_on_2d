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


pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

screen.fill("grey")
pg.display.update()
FPS = 30
CLOCK = pg.time.Clock()


# 遊戲物件初始化
l = N*6+1
maze = Maze(N)
cPos = np.array([3*SCALE, 3*SCALE, 3*SCALE])
plane = Plane(cPos, (10, -10, 0))
points = plane.get_points_on_plane(l*SCALE-1)

screen_array = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT), dtype=int)
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

draw_array = np.zeros((SCREEN_WIDTH, SCREEN_HEIGHT, 4), dtype=int)
draw_array[screen_array == 1] = (255, 255, 255, 0)
draw_array[screen_array != 1] = (0, 0, 0, 0)

surf = pg.surfarray.make_surface(draw_array).convert_alpha()
for i in range(SCREEN_WIDTH):
    for j in range(SCREEN_HEIGHT):
        if screen_array[i, j] == 127:
            print(surf.get_at((i, j)))
            break
    else: continue
    break

for i in range(SCREEN_WIDTH):
    for j in range(SCREEN_HEIGHT):
        if screen_array[i, j] == 0:
            print(surf.get_at((i, j)))
            break
    else: continue
    break

mask = pg.mask.from_threshold(surf, color=(255, 255, 255, 255), threshold=(1, 1, 1, 255))

screen_ratio = SCREEN_HEIGHT/SCREEN_WIDTH
img = Image.open("source/brick_wall.png")
img_ratio = img.size[1]/img.size[0]

if screen_ratio > img_ratio:
    height = SCREEN_HEIGHT
    width = height/img_ratio
else:
    width = SCREEN_WIDTH
    height = width*img_ratio
    
width, height = int(width), int(height)
img = img.resize((width, height))
pil_img = img.crop((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

pg_img = pg.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()

print(screen.get_alpha())
print(pg_img.get_alpha())


img = mask.to_surface(setsurface=pg_img)
screen.blit(img, (0, 0))

run = True
while run:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
    
    pg.display.update()
    CLOCK.tick(FPS)