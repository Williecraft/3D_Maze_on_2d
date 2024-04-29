import numpy as np
import random
from PIL import Image, ImageDraw
import time

class Maze:
    direction = ((1, 0), (0, 1), (0, -1), (-1, 0)) #定義方向序列
    
    def __init__(self, size:int) -> None:
        self.size = size
        self.wall_info = {(0, 0):[True]*len(self.direction)}
        
        
        pos_add = lambda x, y: (x[0]+y[0], x[1]+y[1])
        
        # 生成隨機迷宮
        near = {(i, j): {pos_add((i, j), d) for d in self.direction if all(0 <= next < size for next in pos_add((i, j), d))} for j in range(size) for i in range(size)}
        near[(1, 0)].remove((0, 0))
        near[(0, 1)].remove((0, 0))
        
        pos = (0, 0)
        while True:
            # 隨機取一個方向
            choices = []
            for i, d in enumerate(self.direction):
                next = pos_add(pos, d)
                if not all(0 <= j < size for j in next):
                    continue
                if next in self.wall_info: continue
                choices.append((i, d))
                
            if choices: # 破壞牆壁並前進下一格
                dindex, next_d = random.choice(choices)
                
                self.wall_info[pos][dindex] = False
                
                pos = pos_add(pos, next_d)
                self.wall_info[pos] = [True]*len(self.direction)
                self.wall_info[pos][-(dindex+1)] = False
                
                for d in self.direction:
                    next = pos_add(pos, d)
                    if next in near:
                        near[next].remove(pos)
                        if not near[next]: del near[next]
                
            else: # 跳到有可能前往相鄰房間的地點
                choices = [p for p in self.wall_info if p in near]
                if choices: pos = random.choice(choices)
                else: break
                
        # 迷宮陣列化
        self.array = np.zeros((size*6+1, size*6+1), dtype='int32')
        self.array[0,:] = 1
        self.array[-1,:] = 1
        self.array[:,0] = 1
        self.array[:,-1] = 1
        
        for i in range(size):
            for j in range(size):
                if self.wall_info[(i, j)][0]:
                    self.array[i*6+6:i*6+7 , j*6:j*6+7] = 1
                if self.wall_info[(i, j)][1]:
                    self.array[i*6:i*6+7 , j*6+6:j*6+7] = 1
    
    def get_point(self, pos):
        return self.array[pos]
                    
                        
if __name__ == '__main__':
    n = 3
    size = (n*60+10, n*60+10)

    start = time.time()
    maze = Maze(n)
    print(round(time.time()-start, 2))
    img = Image.new('RGB', size, 'white')

    draw = ImageDraw.Draw(img)
    draw.rectangle(( (0, 0) , (size[0], 10) ), fill=256)
    draw.rectangle(( (0, 0) , (10, size[1]) ), fill=256)
    draw.rectangle(( (size[0]-10, 0) , (size[0], size[1]) ), fill=256)
    draw.rectangle(( (0, size[1]-10) , (size[0], size[1]) ), fill=256)

    def draw_room(maze: Maze, pos:tuple):
        global draw
        
        screen_pos = pos[0]*60, pos[1]*60
        if maze.wall_info[pos][0]: draw.rectangle(( (screen_pos[0]+60, screen_pos[1]) , (screen_pos[0]+70, screen_pos[1]+70) ), fill=256)
        if maze.wall_info[pos][1]: draw.rectangle(( (screen_pos[0], screen_pos[1]+60) , (screen_pos[0]+70, screen_pos[1]+70) ), fill=256)

    for i in range(n):
        for j in range(n):
            draw_room(maze, (i, j))        

    img.show()