from random import randint
from pprint import pprint as print 
from primitieves import *

seed = 7687906

class Chunk():
    field = [[0]*16 for _ in range(16)]
    p = Point()
    width = 4

    def __init__(self, p, seed):
        self.genField(p, seed)
        self.p = p
    
    def genField(self, p, seed):
        self.width = (seed * (p.x + p.y) % 13 + 4) # Random staff
        ws = (8 - self.width // 2, 8 + self.width // 2)
        ws1 = (8 - self.width // 2, 8 + self.width // 2 - 1)
        for i in range(*ws):
            for j in range(*ws):
                self.field[i][j] = 1 if i not in ws1 and j not in ws1 else 2

    def __repr__(self, show = False):
        if show: print(self.field)
        return f'Chunk {self.p}'

class Map:
    seed = -1
    chunks = {(0,0):[]}
    player = Point(8, 8)

    def __init__(self, seed = -1):
        if seed < 0:
            seed = randint(1e6,1e10)
        self.seed = seed
        self.chunks[(0,0)] = Chunk(Point(0, 0), seed)
    
    def __repr__(self):
        dot = ', '
        return f'Seed: {self.seed}, genered: {dot.join(str(i) for i in self.chunks.keys())}'
    
    def genChunk(self, p):
        if isinstance(p, Point):
            self.chunks[(p.x, p.y)] = Chunk(p, self.seed)
        else: self.chunks[*p] = Chunk(p, self.seed)
    
    def get(self, p):
        if isinstance(p, Point):
            return self.chunks[p.x][p.y]
        else:return self.chunks[p[1]][p[2]]


p1 = Point(1,0)
p2 = Point(3,7)
# c = Chunk(p1, seed)
m = Map()
m.genChunk(Point(1, 0))
print(m)