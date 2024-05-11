import pygame as pg
from PlaneInSpace import Plane
from Maze3D import Maze
from Button import Button
import sys
import numpy as np
import datetime
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
        self.quit_button = Button(pg.image.load("resource/quit.png").convert_alpha(), pos=(20, 20), scale=0.01*SCALE)
        self.start_time = datetime.datetime.now()
        self.font_small = pg.font.Font("Fonts/GenSenRounded-M.ttc", SCALE*3)
        self.font_big = pg.font.Font("Fonts/GenSenRounded-M.ttc", SCALE*7)
        
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
        
        # 遊戲主迴圈
        while run:
            rotate = 0
            rightclick = False
            leftclick = False
            
            events = pg.event.get()
            for event in events:
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
                    
            # WASD按鍵偵測
            keys_pressed = pg.key.get_pressed()
            w, a, s, d = keys_pressed[pg.K_w],keys_pressed[pg.K_a],keys_pressed[pg.K_s],keys_pressed[pg.K_d]
            
            # 角色移動
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
                            return self.end(datetime.datetime.now()-self.start_time)
                        
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
                        
            # 平面旋轉
            if not any((w, a, s, d)) and rotate:   
                self.plane.rotateZ(2*rotate, self.cPos)
                self.points = self.plane.get_points_on_plane(self.l*SCALE-1)
            
            # 畫面移動
            if leftclick and not rightclick:
                self.mid = self.mid + mouse_motion
            
            #畫面置中
            if rightclick and not leftclick:
                self.mid = np.array((SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                
            # 畫面繪製
            self.ScreenDraw()
            pg.draw.rect(screen, "red", ((self.mid[0]-SCALE//2, self.mid[1]-SCALE//2, SCALE, SCALE)))
            
            # 顯示退出按鈕
            self.quit_button.draw(self.screen)
            gamequit = self.quit_button.click_test(events)
            if gamequit and gamequit.button == 1: return 'menu'
            
            # 顯示時間
            time = (datetime.datetime.now()-self.start_time)
            secs = time.seconds
            msec = time.microseconds
            mins, secs = secs//60, secs%60
            hours, mins = mins//60, mins%60
            timedisplay = self.font_small.render(f"{hours:02d}:{mins:02d}:{secs:02d}.{msec//10000}", True, "black")
            self.screen.blit(timedisplay, (10, SCREEN_HEIGHT-timedisplay.get_size()[1]-10))
            
            
            # 畫面更新
            pg.display.update()
            CLOCK.tick(FPS)
            # print(round(CLOCK.get_fps()))

    def end(self, time:datetime.timedelta):
        self.screen.fill('white')
        pg.display.update()
        button_image = pg.image.load("resource/button.png").convert_alpha()
        next_lvl = Button(button_image, pos = (SCREEN_WIDTH//2, 25*SCALE), scale=0.05*SCALE, content="下一關", ret="next_lvl")
        play_again = Button(button_image, pos = (SCREEN_WIDTH//2, 35*SCALE), scale=0.05*SCALE, content="再玩一次", ret="game")
        back_to_menu = Button(button_image, pos = (SCREEN_WIDTH//2, 45*SCALE), scale=0.05*SCALE, content="主選單", ret="menu")
        
        buttons = (next_lvl, play_again, back_to_menu)
        
        secs = time.seconds
        msec = time.microseconds
        mins, secs = secs//60, secs%60
        hours, mins = mins//60, mins%60
        timedisplay = self.font_small.render(f"用時 {hours:02d}:{mins:02d}:{secs:02d}.{msec//10000}", True, "black")
        time_rect = timedisplay.get_rect()
        time_rect.center = (SCREEN_WIDTH//2, 17*SCALE)
        
        congrats = self.font_big.render(f"恭喜破關 Lv.{self.lvl}", True, "black")
        congrats_rect = congrats.get_rect()
        congrats_rect.center = (SCREEN_WIDTH//2, 10*SCALE)
        
        run = True
        while run:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    
            self.screen.fill('white')
            
            self.screen.blit(congrats, congrats_rect.topleft)
            self.screen.blit(timedisplay, time_rect.topleft)
            
            for b in buttons:
                b.draw(self.screen)
                click = b.click_test(events)
                if click and click.button == 1:
                    return b.ret
            
            pg.display.update()
            CLOCK.tick(FPS)
        
class Menu:
    def __init__(self, screen: pg.Surface):
        self.screen = screen
        button_image = pg.image.load("resource/button.png").convert_alpha()
        self.start_game = Button(button_image, pos = (SCREEN_WIDTH//2, 25*SCALE), scale=0.05*SCALE, content="開始遊戲", ret = 'game')
        self.jump_lvl = Button(button_image, pos = (SCREEN_WIDTH//2, 35*SCALE), scale=0.05*SCALE, content="跳至關卡", ret = 'jump')
        self.quit_game = Button(button_image, pos = (SCREEN_WIDTH//2, 45*SCALE), scale=0.05*SCALE, content="退出遊戲", ret = 'quit')
        self.buttons = (self.start_game, self.jump_lvl, self.quit_game)
        
    def run(self):
        run = True
        while run:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            
            self.screen.fill("#FFFFFF")
            
            for b in self.buttons:
                b.draw(self.screen)
                click = b.click_test(events)
                if click and click.button == 1:
                    return b.ret
                
            pg.display.update()
            CLOCK.tick(FPS)
                
            
            
    
if __name__ == "__main__":
    lvl = 2
    op = "menu"
    while True:
        if op == "menu":
            menu = Menu(screen)
            op = menu.run()
        elif op == "game":
            game = Game(screen, lvl, showAns = True)
            op = game.run()
        elif op == 'next_lvl':
            lvl += 1
            op = 'game'
        else: break
            