import numpy as np
import random
import time

class Maze:
    direction = ((1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0), (-1, 0, 0)) #定義方向序列
    
    def __init__(self, size:int) -> None:
        if size <= 1: raise ValueError("(size) can't be less than 2")
        
        self.size = size
        self.wall_info = {(0, 0, 0):[True]*len(self.direction)}
        
        
        pos_add = lambda x, y: (x[0]+y[0], x[1]+y[1], x[2]+y[2])
        
        # 生成隨機迷宮
        near = {(i, j, k): {pos_add((i, j, k), d) for d in self.direction if all(0 <= next < size for next in pos_add((i, j, k), d))} for k in range(size) for j in range(size) for i in range(size)}
        near[(1, 0, 0)].remove((0, 0, 0))
        near[(0, 1, 0)].remove((0, 0, 0))
        near[(0, 0, 1)].remove((0, 0, 0))
        
        pos = (0, 0, 0)
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
        self.array = np.zeros((size*6+1, size*6+1, size*6+1), dtype=int)
        self.array[:, :, 0] = 1
        self.array[:, :, -1] = 1
        self.array[:, 0, :] = 1
        self.array[:, -1, :] = 1
        self.array[0, :, :] = 1
        self.array[-1, :, :] = 1
        
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    if self.wall_info[(i, j, k)][0]:
                        self.array[i*6+6:i*6+7, j*6:j*6+7, k*6:k*6+7] = 1
                    if self.wall_info[(i, j, k)][1]:
                        self.array[i*6:i*6+7, j*6+6:j*6+7, k*6:k*6+7] = 1
                    if self.wall_info[(i, j, k)][2]:
                        self.array[i*6:i*6+7, j*6:j*6+7, k*6+6:k*6+7] = 1
        
        self.path = self.array.copy()
                 
        self.array[1:6, 1:6, 1:6] = 2
        self.array[6*(size-1)+1:size*6, 6*(size-1)+1:size*6, 6*(size-1)+1:size*6] = 9
        
        self.path[self.path==1] = -1
        self.path[(3, 3, 3)] = 1
        
        passed = np.zeros((size*6+1, size*6+1, size*6+1), dtype=bool)
        def findpath(now):
            if self.array[now] == 9: return True
            
            passed[now] = 1
            for d in self.direction:
                next = tuple((now[i]+d[i] for i in range(len(d))))
                if [i%3 == 0 for i in next].count(True) >= 2 and all(0 <= i <= size*6 for i in next) and not passed[next] and self.path[next] == 0:
                    self.path[next] = self.path[now]+1
                    if findpath(next): return True
                    self.path[next] = 0
            return False
        assert findpath((3, 3, 3)), "No answer"
        
            
                    
                
            
    
if __name__ == '__main__':
    for i in range(2, 100):
        start = time.time()
        Maze(i)
        print(i, round(time.time()-start, 5), sep='\t')