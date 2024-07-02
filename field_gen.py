from random import randint
from pprint import pprint as print 
from primitieves import *

# seed = 7687906

class Chunk():
    field = [[0]*16 for _ in range(16)]
    p = Point()
    width = 6
    paths = { 'left': -1, 'top': -1, 'right': -1, 'bottom': -1 }

    def __init__(self, p, seed):
        self.p = Point(*tuple(p))
        self.field = [[0]*16 for _ in range(16)]
        self.paths = { 'left': -1, 'top': -1, 'right': -1, 'bottom': -1 }
        self.genField(seed)
    
    def genField(self, seed):
        self.width = (seed * (self.p.x + self.p.y) % 11 + 6) # Random staff
        ws = (8 - self.width // 2, 8 + self.width // 2)
        ws1 = (8 - self.width // 2, 8 + self.width // 2 - 1)
        for i in range(*ws):
            for j in range(*ws):
                self.field[i][j] = 1 if i not in ws1 and j not in ws1 else 2
    
    def addPaths(self):
        if self.paths['left'] != -1:
            for x in range(9 - self.width // 2):
                self.field[self.paths['left'] - 1][x] = 2
                self.field[self.paths['left']][x] = 1
                self.field[self.paths['left'] + 1][x] = 2
        if self.paths['right'] != -1:
            for x in range(7 + self.width // 2, 16):
                self.field[self.paths['right'] - 1][x] = 2
                self.field[self.paths['right']][x] = 1
                self.field[self.paths['right'] + 1][x] = 2
        if self.paths['top'] != -1:
            for y in range(7 + self.width // 2, 16):
                self.field[y][self.paths['top'] - 1] = 2
                self.field[y][self.paths['top']] = 1
                self.field[y][self.paths['top'] + 1] = 2
        if self.paths['bottom'] != -1:
            for y in range(9 - self.width // 2):
                self.field[y][self.paths['bottom'] - 1] = 2
                self.field[y][self.paths['bottom']] = 1
                self.field[y][self.paths['bottom'] + 1] = 2

    def __repr__(self, show = False):
        if show: print(self.field)
        return f'Chunk {self.p}'

class Map:
    seed = -1
    chunks = {}
    player = Point(8, 8)

    def __init__(self, seed = -1):
        if seed < 0:
            seed = randint(1e6,1e10)
        self.seed = seed
        self.genArea(Point(0,0))
    
    def __repr__(self):
        sep = ', '
        return f'Seed: {self.seed}, genered: {sep.join(str(i) for i in self.chunks.keys())}'
    
    def genChunk(self, p):
        self.chunks[tuple(p)] = Chunk(p, self.seed)
    
    def get(self, p):
        if p not in self:
            self.genChunk(p)
        if isinstance(p, Point):
            return self.chunks[(p.x, p.y)]
        else: return self.chunks[(p[0],p[1])]
    
    def genArea(self, p):
        if not isinstance(p, Point): p = Point(*p)
        vecs = [Point(-1,0), Point(1,0), Point(0,1), Point(0,-1)]
        self.get(p)
        for vec in vecs:
            self.get(p+vec)
            self.setPath(p, vec)
            self.get(p+vec).addPaths()
        self.get(p).addPaths()

    def setPath(self, p1, vec):
        p2 = p1 + vec
        randnum = (self.seed * (abs(p1.x) + abs(p1.y) + abs(p2.x) + abs(p2.y)))
        if randnum % 5 == 5 - 1: return
        # print("gened")
        chunk1 = self.get(p1)
        chunk2 = self.get(p2)
        m = min(chunk1.width, chunk2.width)
        randnum = randnum % (m-1) + 8 - m // 2
        
        if vec.x == -1:
            chunk1.paths['left'] = randnum
            chunk2.paths['right'] = randnum
        elif vec.x == 1:
            chunk1.paths['right'] = randnum
            chunk2.paths['left'] = randnum
        if vec.y == -1:
            chunk1.paths['bottom'] = randnum
            chunk2.paths['top'] = randnum
        elif vec.y == 1:
            chunk1.paths['top'] = randnum
            chunk2.paths['bottom'] = randnum

    def __contains__(self, p):
        return tuple(p) in self.chunks

# p1 = Point(1,0)
# p2 = Point(3,7)
# # c = Chunk(p1, seed)
# m = Map()
# m.genChunk(Point(1, 0))
# print(m)