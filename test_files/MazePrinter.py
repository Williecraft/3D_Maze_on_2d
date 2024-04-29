from PIL import Image, ImageDraw
from Maze2D import Maze
import numpy as np

class Line:
    def __init__(self, rpoint:tuple[float, float], normal_vector:tuple[float, float]) -> None:
        self.rpoint = np.array(rpoint)
        self.normal_vector = np.array(normal_vector)
        self.C = sum(self.normal_vector*self.rpoint)
        
    def func(self, point:tuple) -> float: 
        point = np.array(point)
        return sum(point*self.normal_vector) - self.C
        
    def check_on_line(self, point:tuple[float, float]) -> bool:
        point = np.array(point)
        
        lu = self.func(point)
        ld = self.func(point+[1, 0])
        ru = self.func(point+[0, 1])
        rd = self.func(point+[1, 1])
        
        return (lu*rd <= 0 or ld*ru <= 0)

n = 3
l = n*6+1
scale = 10

size = (l*10, l*10)
maze = Maze(n)
pos = (25, 25)

line = Line(pos, (2, -1))

img = Image.new('RGB', size, 'white')
draw = ImageDraw.Draw(img)

for i in range(l):
    for j in range(l):
        if maze.array[i, j]:
            draw.rectangle(((i*scale, j*scale) , ((i+1)*scale, (j+1)*scale)), fill=0x000000)
    
    
stack = [pos] 
passed = {pos}

def check(passed, size, p):
    if not all(0 <= p[i] < size[i] for i in range(len(p))): return False
    if p in passed: return False
    return True

add = lambda x, y: (x[0]+y[0], x[1]+y[1])

while stack:
    p = stack.pop()
    passed.add(p)
    if line.check_on_line(p):
        pos_in_array = p[0]//scale, p[1]//scale
        
        if maze.get_point(pos_in_array) == 1:
            draw.point(p, fill=0xFF0000)
        else:
            draw.point(p, fill=0x00ff00)
        for d in maze.direction:
            if check(passed, size, add(p, d)): stack.append(add(p, d))
                 
                 
draw.ellipse((add(pos, (-2, -2)), add(pos, (2, 2))), fill='red')
img.show()
print()