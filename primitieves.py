class Point():
    x = 0
    y = 0

    def __init__(self, x1=0, y1=0):
        self.x = x1
        self.y = y1
    
    def __repr__(self):
        return f'({self.x}, {self.y})'
    
    def __mul__(self, a):
        return Point(self.x * a, self.y * a)
    
    def __add__(self, p):
        return Point(self.x + p.x, self.y + p.y)

class Cell():
    p = Point()
    isWall = False

    def __init__(self, p, isWall = False):
        self.p = p
        self.isWall = isWall
    
    def __repr__(self):
        if self.isWall: return f'{self.p} is wall'
        else: return f'{self.p} isn\'t wall'