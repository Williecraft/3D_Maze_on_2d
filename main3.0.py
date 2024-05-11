import pygame as pg
from PlaneInSpace import Plane
from Maze3D import Maze
import sys
import numpy as np
import time
from PIL import Image

# 常數設定
SCALE = 10
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

# 視窗初始化
pg.init()
pg.display.set_caption("在二維上的三維迷宮")
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
FPS = 30
CLOCK = pg.time.Clock()

class Game:
    def get_pic(filename:str):
        screen_ratio = SCREEN_HEIGHT/SCREEN_WIDTH
        pil_img = Image.open(fr"resource/{filename}.png")
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
    
    wall_img = get_pic("brick_wall")
    path_img = get_pic("dirt_path")
    end_img = get_pic("diamond_block")
    start_img = get_pic("emerald_block")
    grass_img = get_pic("grass_block")
    
    def __init__(self, screen:pg.Surface, lvl:int, showAns:bool = False) -> None:
        self.screen = screen
        self.lvl = lvl
        self.showAns = showAns
        self.l = lvl*6+1
        self.maze = Maze(lvl)
        self.cPos = np.array([3*SCALE, 3*SCALE, 3*SCALE])
        self.plane = Plane(self.cPos, (10, -10, 0))
        self.points = self.plane.get_points_on_plane(self.l*SCALE-1)
        self.mid = np.array((SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        
    def draw_pic(self, screen_array:np.ndarray, target:int, source_img:pg.Surface):
        draw_array = screen_array.copy()
        draw_array[draw_array == np.int16(target)] = 255
        draw_array[draw_array != np.int16(255)] = 0
        
        surf = pg.surfarray.make_surface(draw_array).convert_alpha()
        mask = pg.mask.from_threshold(surf, color=(255, 255, 255, 255), threshold=(1, 1, 1, 255))
        
        img = mask.to_surface(setsurface=source_img, unsetcolor=(0, 0, 0, 0)).convert_alpha()
        self.screen.blit(img, (0, 0))
        
    def ScreenDraw(self):  
        self.screen.fill("#FFFFFF")
        screen_array = np.full((SCREEN_WIDTH, SCREEN_HEIGHT), fill_value=-1,dtype='int16')
        
        center = np.array(self.cPos[:2])
        
        for p in self.points:
            pos = np.array(p)
            vector = pos-center
            x = (vector[0]**2+vector[1]**2)**0.5
            
            if self.plane.normal_vector[0]*vector[1]<self.plane.normal_vector[1]*vector[0]: x = -x
            x = self.mid[0]+int(x)
            
            if x > SCREEN_WIDTH or x < 0: continue
            
            for z in range(max(0, (-self.mid[1]+self.cPos[2])//SCALE), min(self.l, ((SCREEN_HEIGHT-self.mid[1])+self.cPos[2])//SCALE)):
                pArray = (p[0]//SCALE, p[1]//SCALE, z)
                
                y = self.mid[1]+int(z*SCALE-self.cPos[2])
                
                if (0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT):
                    if self.showAns and self.maze.path[pArray] > 0:
                        screen_array[x, y:y+SCALE] = 2
                    else:
                        screen_array[x, y:y+SCALE] = self.maze.array[pArray]
        
        self.draw_pic(screen_array, 1, self.wall_img)
        self.draw_pic(screen_array, 0, self.grass_img)
        self.draw_pic(screen_array, 3, self.path_img)
        self.draw_pic(screen_array, 2, self.start_img)
        self.draw_pic(screen_array, 9, self.end_img)
    
    def getRightVector(self, step:int):
        v = np.cross((0, 0, 1), self.plane.normal_vector)
        v = v*step/np.sum(v**2)**0.5
        v =  v.astype(int)
        return v
    
    def run(self):
        run = True
        while run:
            rotate = 0
            rightclick = False
            leftclick = False
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                if event.type == pg.MOUSEWHEEL:
                    if event.y: rotate = event.y
                if event.type == pg.MOUSEMOTION:
                    mouse_motion = event.rel
                    leftclick = bool(event.buttons[0])
                if event.type == pg.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        rightclick = True
                    
                    
            keys_pressed = pg.key.get_pressed()
            w, a, s, d = keys_pressed[pg.K_w],keys_pressed[pg.K_a],keys_pressed[pg.K_s],keys_pressed[pg.K_d]
            
            if not rotate: 
                toUP = 0
                toRIGHT = 0
                if w: toUP -= 1
                if s: toUP += 1
                if d: toRIGHT += 1
                if a: toRIGHT -= 1
                
                next = self.cPos
                if toUP or toRIGHT:
                    step = 0
                    while step < SCALE-1:
                        last = next
                        next = self.cPos+self.getRightVector(step)*toRIGHT+(0, 0, step*toUP)
                        
                        direction = ((1, 0), (0, 1), (0, -1), (-1, 0))
                        if tuple(next[:2]) not in self.points:
                            for d in direction:
                                if tuple(next[:2]+d) in self.points:
                                    next[:2] = next[:2]+d
                                    break
                            else:
                                next = last
                                break
                        
                        if self.maze.array[tuple(next//SCALE)] == 9:
                            run = False
                            break
                        
                        if self.maze.array[tuple(next//SCALE)] != 1:
                            step += 1
                            continue
                        step -= 1
                        next = last
                        break
                    if step:
                        self.cPos = next
                        if self.maze.array[tuple(next//SCALE)] == 0:
                            self.maze.array[tuple(next//SCALE)] = 3
                        
            
            if not any((w, a, s, d)) and rotate:   
                self.plane.rotateZ(2*rotate, self.cPos)
                self.points = self.plane.get_points_on_plane(self.l*SCALE-1)
            
            if leftclick and not rightclick:
                self.mid = self.mid + mouse_motion
            
            if rightclick and not leftclick:
                self.mid = np.array((SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                
            
            self.ScreenDraw()
            pg.draw.rect(screen, "red", ((self.mid[0]-SCALE//2, self.mid[1]-SCALE//2, SCALE, SCALE)))
            
            pg.display.update()
            CLOCK.tick(FPS)
            # print(round(CLOCK.get_fps()))
    
if __name__ == "__main__":
    game = Game(screen, 10, showAns = True)
    game.run()