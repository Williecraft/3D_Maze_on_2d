try:
    try:
        import pygame as pg
        import numpy as np
        from PIL import Image
    except ModuleNotFoundError:
        import os
        os.system(r"pip install -r module_install/requirements.txt")
        import pygame as pg
        import numpy as np
        from PIL import Image
        
    import sys 
    import datetime   
    from GameModule.PlaneInSpace import Plane
    from GameModule.Maze3D import Maze
    from GameModule.Button import Button

    # 常數設定
    SCALE = 10
    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 540
    MIN_LVL, MAX_LVL = 2, 10
    CAN_SHOW_ANS = True

    # 視窗初始化
    pg.init()
    pg.display.set_caption("在二維上的三維迷宮")
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    FPS = 30
    CLOCK = pg.time.Clock()
    pg.mixer.music.load("resource/Sounds/PeriTune_Sugar_Sprinkle.mp3")
    pg.mixer.music.set_volume(0.7)
    pg.mixer.music.play(-1)
    
    # 遊戲物件
    class Game:
        # 獲取背景圖片
        def get_pic(filename:str):
            screen_ratio = SCREEN_HEIGHT/SCREEN_WIDTH
            pil_img = Image.open(fr"resource/Pictures/{filename}.png")
            img_ratio = pil_img.size[1]/pil_img.size[0]
            
            # 計算大小並切割圖片
            if screen_ratio > img_ratio:
                height = SCREEN_HEIGHT
                width = height/img_ratio
            else:
                width = SCREEN_WIDTH
                height = width*img_ratio
            
            width, height = int(width), int(height)
            pil_img = pil_img.resize((width, height))
            pil_img = pil_img.crop((0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # 轉成Pygame圖片
            pg_img = pg.image.fromstring(pil_img.tobytes(), pil_img.size, pil_img.mode).convert_alpha()
            return pg_img
        
        # static圖片檔
        wall_img = get_pic("brick_wall")
        path_img = get_pic("dirt_path")
        end_img = get_pic("diamond_block")
        start_img = get_pic("emerald_block")
        grass_img = get_pic("grass_block")
        
        # 初始化遊戲
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
            self.pause_button = Button(pg.image.load("resource/Pictures/pause.png").convert_alpha(), pos=(30, 30), scale=0.01*SCALE)
            if CAN_SHOW_ANS: self.hint_button = Button(pg.image.load("resource/Pictures/hint.png").convert_alpha(), pos=(8.5*SCALE, 3*SCALE), scale=0.01*SCALE)
            if CAN_SHOW_ANS: self.hint_on_button = Button(pg.image.load("resource/Pictures/hint_on.png").convert_alpha(), pos=(8.5*SCALE, 3*SCALE), scale=0.01*SCALE)
            self.font_small = pg.font.Font("resource/Fonts/XiaolaiMonoSC-Regular.ttf", SCALE*3)
            self.font_big = pg.font.Font("resource/Fonts/XiaolaiMonoSC-Regular.ttf", SCALE*7)
            self.pause_total = datetime.timedelta(0)
            self.start_time = datetime.datetime.now()
        
        # 根據畫面資訊建立mask刻製圖片並貼上
        def draw_pic(self, screen_array:np.ndarray, target:int, source_img:pg.Surface):
            draw_array = screen_array.copy()
            draw_array[draw_array == np.int16(target)] = 255
            draw_array[draw_array != np.int16(255)] = 0
            
            surf = pg.surfarray.make_surface(draw_array).convert_alpha()
            mask = pg.mask.from_threshold(surf, color=(255, 255, 255, 255), threshold=(1, 1, 1, 255))
            
            img = mask.to_surface(setsurface=source_img, unsetcolor=(0, 0, 0, 0)).convert_alpha()
            self.screen.blit(img, (0, 0))
        
        # 畫面繪製方法
        def ScreenDraw(self):  
            self.screen.fill("white")
            screen_array = np.full((SCREEN_WIDTH, SCREEN_HEIGHT), fill_value=-1,dtype='int16')
            
            center = np.array(self.cPos[:2])
            
            # 迭代全部平面上的點
            for p in self.points:
                pos = np.array(p)
                vector = pos-center
                
                # 三維轉二維
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
            
            # 呼叫圖片繪製
            self.draw_pic(screen_array, 1, self.wall_img)
            self.draw_pic(screen_array, 0, self.grass_img)
            self.draw_pic(screen_array, 3, self.path_img)
            self.draw_pic(screen_array, 2, self.start_img)
            self.draw_pic(screen_array, 9, self.end_img)
        
        # 根據移動步數，獲取目前平面向右的向量
        def getRightVector(self, step:int):
            v = np.cross((0, 0, 1), self.plane.normal_vector)
            v = v*step/np.sum(v**2)**0.5
            v =  v.astype(int)
            return v
        
        # 獲取當前遊戲時間字串
        def render_time(self) -> str:
            time = (datetime.datetime.now()-self.start_time-self.pause_total)
            secs = time.seconds
            msec = time.microseconds
            mins, secs = secs//60, secs%60
            hours, mins = mins//60, mins%60
            return f"{hours:02d}:{mins:02d}:{secs:02d}.{msec//10000}"
        
        # 遊戲主迴圈
        def main(self):
            run = True
            while run:
                rotate = 0
                rightclick = False
                leftclick = False
                
                events = pg.event.get()
                for event in events:
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                    # 滾輪偵測
                    if event.type == pg.MOUSEWHEEL:
                        if event.y: rotate = event.y
                    # 獲取滑鼠拖曳
                    if event.type == pg.MOUSEMOTION:
                        mouse_motion = event.rel
                        leftclick = bool(event.buttons[0])
                    # 右鍵偵測
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
                                return self.end(datetime.datetime.now()-self.start_time-self.pause_total)
                            
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
                
                # 暫停按鈕繪製
                self.pause_button.draw(self.screen)
                pause = self.pause_button.click_test(events)
                if pause: 
                    if not self.pause(self.render_time()): return 'menu'
                    
                # 顯示提示按鈕
                if CAN_SHOW_ANS:
                    if self.showAns:
                        self.hint_on_button.draw(self.screen)
                        clickHint = self.hint_on_button.click_test(events)
                        if clickHint:
                            self.showAns = False
                    else:
                        self.hint_button.draw(self.screen)
                        clickHint = self.hint_button.click_test(events)
                        if clickHint:
                            self.showAns = True
                
                # 顯示時間
                timedisplay = self.font_small.render(self.render_time(), True, "black")
                self.screen.blit(timedisplay, (10, SCREEN_HEIGHT-timedisplay.get_size()[1]-10))
                
                
                # 畫面更新
                pg.display.update()
                CLOCK.tick(FPS)
                # print(round(CLOCK.get_fps()))
        
        # 遊戲暫停模式
        def pause(self, nowtime:str):
            pause_time = datetime.datetime.now()
            quit_button = Button(pg.image.load("resource/Pictures/quit.png").convert_alpha(), pos=(30, 30), scale=0.01*SCALE)
            start_button = Button(pg.image.load("resource/Pictures/start.png").convert_alpha(), pos=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2), scale=0.02*SCALE)
            pause_text = self.font_small.render("遊戲暫停", True, "black")
            pause_text_rect = pause_text.get_rect()
            pause_text_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2-10*SCALE)
            run = True
            while run:
                events = pg.event.get()
                for event in events:
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                        
                self.screen.fill("white")
                
                # 顯示退出按鈕
                quit_button.draw(self.screen)
                gamequit = quit_button.click_test(events)
                if gamequit: return False
                
                self.screen.blit(pause_text, pause_text_rect)
                
                # 顯示開始按鈕
                start_button.draw(self.screen)
                restart = start_button.click_test(events)
                if restart:
                    self.pause_total = self.pause_total+datetime.datetime.now()-pause_time
                    return True
                
                # 顯示時間
                timedisplay = self.font_small.render(nowtime, True, "black")
                self.screen.blit(timedisplay, (10, SCREEN_HEIGHT-timedisplay.get_size()[1]-10))
                
                pg.display.update()
                CLOCK.tick(FPS)
        
        # 遊戲結束模式
        def end(self, time:datetime.timedelta):
            self.screen.fill("white")
            pg.display.update()
            
            # 初始化按鈕
            button_image = pg.image.load("resource/Pictures/button.png").convert_alpha()
            next_lvl = Button(button_image, pos = (SCREEN_WIDTH//2, 25*SCALE), scale=0.05*SCALE, content="下一關", ret="next_lvl")
            play_again = Button(button_image, pos = (SCREEN_WIDTH//2, 35*SCALE), scale=0.05*SCALE, content="再玩一次", ret="game")
            back_to_menu = Button(button_image, pos = (SCREEN_WIDTH//2, 45*SCALE), scale=0.05*SCALE, content="主選單", ret="menu")
            buttons = (next_lvl, play_again, back_to_menu)
            
            # 計算最終成績(用時)
            secs = time.seconds
            msec = time.microseconds
            mins, secs = secs//60, secs%60
            hours, mins = mins//60, mins%60
            timedisplay = self.font_small.render(f"用時 {hours:02d}:{mins:02d}:{secs:02d}.{msec//10000}", True, "black")
            time_rect = timedisplay.get_rect()
            time_rect.center = (SCREEN_WIDTH//2, 17*SCALE)
            
            # "恭喜通關"標題
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
                        
                self.screen.fill("white")
                
                self.screen.blit(congrats, congrats_rect.topleft)
                self.screen.blit(timedisplay, time_rect.topleft)
                
                # 按鈕繪製與偵測
                for b in buttons:
                    b.draw(self.screen)
                    click = b.click_test(events)
                    if click:
                        return b.ret
                
                pg.display.update()
                CLOCK.tick(FPS)
    
    # 主畫面物件
    class Menu:
        def __init__(self, screen: pg.Surface):
            self.screen = screen
            button_image = pg.image.load("resource/Pictures/button.png").convert_alpha()
            self.start_game = Button(button_image, pos = (SCREEN_WIDTH//2, 25*SCALE), scale=0.05*SCALE, content="開始遊戲", ret = 'game')
            self.jump_lvl = Button(button_image, pos = (SCREEN_WIDTH//2, 35*SCALE), scale=0.05*SCALE, content="跳至關卡", ret = 'jump')
            self.quit_game = Button(button_image, pos = (SCREEN_WIDTH//2, 45*SCALE), scale=0.05*SCALE, content="退出遊戲", ret = 'quit')
            self.buttons = (self.start_game, self.jump_lvl, self.quit_game)
            self.font = pg.font.Font("resource/Fonts/XiaolaiMonoSC-Regular.ttf", SCALE*7)
            
        def main(self):
            title = self.font.render(f"二維上的三維迷宮", True, "black")
            title_rect = title.get_rect()
            title_rect.center = (SCREEN_WIDTH//2, 10*SCALE)

            run = True
            while run:
                events = pg.event.get()
                for event in events:
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                
                self.screen.fill("white")
                self.screen.blit(title, title_rect)
                
                # 按鈕繪製與偵測
                for b in self.buttons:
                    b.draw(self.screen)
                    click = b.click_test(events)
                    if click:
                        return b.ret
                    
                pg.display.update()
                CLOCK.tick(FPS)
    
    # 關卡選擇物件
    class JumpLvl:
        def __init__(self, screen:pg.Surface):
            self.screen = screen
            
            # 按鈕初始化
            button_image = pg.image.load("resource/Pictures/button.png").convert_alpha()

            self.left = Button(pg.image.load("resource/Pictures/left_arrow.png").convert_alpha(), pos = (SCREEN_WIDTH//2-20*SCALE, SCREEN_HEIGHT//2), scale=0.03*SCALE, ret = "left")
            self.right = Button(pg.image.load("resource/Pictures/right_arrow.png").convert_alpha(), pos = (SCREEN_WIDTH//2+20*SCALE, SCREEN_HEIGHT//2), scale=0.03*SCALE, ret = "right")
            self.start_game = Button(button_image, pos = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2+20*SCALE), content="開始遊戲", scale=0.05*SCALE, ret = "game")
            self.back_button = Button(pg.image.load("resource/Pictures/quit.png").convert_alpha(), pos=(30, 30), scale=0.01*SCALE, ret = "back")
            self.buttons = (self.left, self.right, self.start_game, self.back_button)
            # 字體初始化
            self.font = pg.font.Font("resource/Fonts/XiaolaiMonoSC-Regular.ttf", SCALE*6)
            self.font_back = pg.font.Font("resource/Fonts/XiaolaiMonoSC-Regular.ttf", SCALE*6+SCALE//3)
            
            # 依照關卡最大最小值建立漸層顏色
            sep = 512/(MAX_LVL-MIN_LVL)
            l = 0
            self.colors = []
            for i in range(MAX_LVL+1):
                if i < MIN_LVL: self.colors.append(-1)
                else:
                    R = min(round(l), 255)
                    G = min(512-round(l), 255)
                    self.colors.append( (R, G, 0) )
                    l += sep
        
        # 關卡選擇主函式
        def main(self):
            run = True
            lvl = MIN_LVL
            while run:
                events = pg.event.get()
                for event in events:
                    if event.type == pg.QUIT:
                        pg.quit()
                        sys.exit()
                
                self.screen.fill("white")
                
                lvl_show = self.font.render(str(lvl), True, "black")
                lvl_show_back = self.font_back.render(str(lvl), True, self.colors[lvl])
                rectF = lvl_show.get_rect()
                rectB = lvl_show_back.get_rect()
                rectF.center = rectB.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
                
                self.screen.blit(lvl_show_back, rectB)
                self.screen.blit(lvl_show, rectF)
                
                # 按鈕繪製與偵測
                for b in self.buttons:
                    b.draw(self.screen)
                    click = b.click_test(events)
                    if click:
                        if b.ret == "left": lvl = max(MIN_LVL, lvl-1)
                        elif b.ret == "right": lvl = min(MAX_LVL, lvl+1)
                        elif b.ret == "game": return ("game", lvl)
                        elif b.ret == "back": return ("back", -1)
                
                pg.display.update()
                CLOCK.tick(FPS)
    
    lvl = 3
    op = "menu"
    while True:
        if op == "menu":
            current = Menu(screen)
            op = current.main()
        elif op == "game":
            current = Game(screen, lvl)
            op = current.main()
        elif op == "next_lvl":
            lvl += 1
            op = 'game'
        elif op == "jump":
            current = JumpLvl(screen)
            op, newLvL = current.main()
            if op == "back": op = "menu"
            else: lvl = newLvL
        else: break
except Exception as err:
    pg.quit()
    print("ERROR:", err)
    import os
    os.system("PAUSE")