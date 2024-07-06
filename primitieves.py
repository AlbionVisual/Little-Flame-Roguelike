class Vec():
    def __init__(self, x1=0, y1=0):
        self.x = x1
        self.y = y1
    
    def __repr__(self):
        return f'({self.x}, {self.y})'
    
    def __mul__(self, a):
        return Vec(self.x * a, self.y * a)
    
    def __add__(self, p):
        return Vec(self.x + p.x, self.y + p.y)
    
    def __iter__(self):
        self.current = None
        return self
    
    def __next__(self):
        if self.current == None:
            self.current = 'x'
            return self.x
        elif self.current == 'x':
            self.current = 'y'
            return self.y
        raise StopIteration