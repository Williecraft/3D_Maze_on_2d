import numpy as np

class Plane:
    def __init__(self, rpoint:tuple[int, int, int], normal_vector:tuple[float, float, float]) -> None:
        self.rpoint = np.array(rpoint, dtype='int32')
        self.normal_vector = np.array(normal_vector)
        self.C = sum(self.normal_vector*self.rpoint)
        
    def func(self, point:tuple[int, int]) -> float: 
        point = np.array(point)
        return point[0]*self.normal_vector[0]+point[1]*self.normal_vector[1] - self.C
        
    def check_on_plane(self, point:tuple[int, int]) -> int:
        point = np.array(point)
        
        direction = ((0, 0), (1, 0), (0, 1), (1, 1))
        arr = [self.func(point+d) for d in direction]
        
        return any(arr[i]*arr[-(i+1)] <= 0 for i in range(4))
    
    def get_points_on_plane(self, max:int) -> set[tuple[int, int]]:
        pos = tuple(self.rpoint[:2])
        result = set()
        checked = set()
        stack = [pos]
        
        
        def check(checked, max, p):
            if not all(0 <= i <= max for i in p): return False
            if p in checked: return False
            return True
        
        add = lambda x, y: tuple(x[i]+y[i] for i in range(len(x)))
        
        while stack:
            p = stack.pop()
            checked.add(p)
            
            if self.check_on_plane(p):
                result.add(p)
                
                for d in ((1, 0), (0, 1), (0, -1), (-1, 0)):
                    if check(checked, max, add(p, d)): stack.append(add(p, d))

        return result
    
    def rotateZ(self, angle:float, rpoint:tuple[int, int, int]):
        rpoint = np.array(rpoint)
        v = self.normal_vector
        deg = np.radians(angle)
        rotate = np.array([[np.cos(deg), -np.sin(deg),  0],
                           [np.sin(deg),  np.cos(deg),  0],
                           [          0,            0,  1]])
        self.update(rpoint=rpoint, normal_vector=rotate.dot(v))
        
    def update(self, rpoint:tuple[int, int, int] = None, normal_vector:tuple[float, float, float] = None):
        if not isinstance(rpoint, type(None)): 
            self.rpoint = np.array(rpoint, dtype='int32')
        if not isinstance(normal_vector, type(None)): 
            self.normal_vector = np.array(normal_vector)
        self.C = sum(self.normal_vector*self.rpoint)
        
    
if __name__ == '__main__':
    plane = Plane((3, 4, 5), (32, 645, 97))
    points = plane.get_points_on_plane(100)
    print(len(points))