from random import randint
from pprint import pprint as print 
from primitieves import *

class Chunk():
    field = [[0]*16 for _ in range(16)]
    p = Point()
    width = 6
    paths = { 'left': -1, 'top': -1, 'right': -1, 'bottom': -1 }

    def __init__(self, p, seed):
        self.p = Point(*tuple(p))
        self.field = [[[0] for _ in range(16)] for _ in range(16)]
        self.paths = { 'left': -1, 'top': -1, 'right': -1, 'bottom': -1 }
        self.genField(seed)
    
    def genField(self, seed):
        self.width = ((seed * (self.p.x + self.p.y) % 11 + 6) // 2) * 2 # Random staff
        ws = (8 - self.width // 2, 8 + self.width // 2)
        ws1 = (8 - self.width // 2, 8 + self.width // 2 - 1)
        for i in range(*ws):
            for j in range(*ws):
                self.field[i][j] = [3 if i not in ws1 and j not in ws1 else 4]    

    def addPaths(self):
        if self.paths['left'] != -1 and self.field[self.paths['left']][0][0] not in (1, 3, 5):
            for x in range(9 - self.width // 2):
                self.field[self.paths['left'] - 1][x] = [4]
                self.field[self.paths['left']][x] = [3]
                self.field[self.paths['left'] + 1][x] = [4]
        if self.paths['right'] != -1 and self.field[self.paths['right']][15][0] not in (1, 3, 5):
            for x in range(7 + self.width // 2, 16):
                self.field[self.paths['right'] - 1][x] = [4]
                self.field[self.paths['right']][x] = [3]
                self.field[self.paths['right'] + 1][x] = [4]
        if self.paths['top'] != -1 and self.field[15][self.paths['top']][0] not in (1, 3, 5):
            for y in range(7 + self.width // 2, 16):
                self.field[y][self.paths['top'] - 1] = [4]
                self.field[y][self.paths['top']] = [3]
                self.field[y][self.paths['top'] + 1] = [4]
        if self.paths['bottom'] != -1 and self.field[0][self.paths['bottom']][0] not in (1, 3, 5):
            for y in range(9 - self.width // 2):
                self.field[y][self.paths['bottom'] - 1] = [4]
                self.field[y][self.paths['bottom']] = [3]
                self.field[y][self.paths['bottom'] + 1] = [4]

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
    
    def genLight(self, p, f, f_args, strength = 5): # simpliest circle
        p = Point(*p)
        for i in range(int(p.x) - strength - 3, int(p.x) + strength + 3):
            for j in range(int(p.y) - strength - 3, int(p.y) + strength + 3):
                cell = self.getCell(Point(i, j))
                if (i - p.x)**2 + (j - p.y)**2 <= strength**2:
                    if cell[0] in (2, 4):
                        f(cell, f_args[6])
                        cell[0] = 6
                    if cell[0] in (1, 3):
                        f(cell, f_args[5])
                        cell[0] = 5
                elif len(cell) > 1:
                    if cell[0] == 6:
                        f(cell, f_args[2])
                        cell[0] = 2
                    if cell[0] == 5:
                        f(cell, f_args[1])
                        cell[0] = 1
    
    def genTreeLight(self, p, strength = 5):
        vecs = [Point(-1,0), Point(0,1), Point(1,0), Point(0,-1), Point(-1,-1), Point(-1,1), Point(1,1), Point(1,-1)]
        walls = set()
        floor = set()
        queue = []
        checked = []
        def checkCell(cell):
            nonlocal queue
            nonlocal checked
            el = self.getCell(Point(*cell["coord"]))
            if el[0] in (2, 4, 6):
                walls.add(el[1])
                el[0] = 6
            if el[0] in (1, 3, 5): 
                floor.add(el[1])
                el[0] = 5
                for vec in vecs:
                    pi = Point(*cell["coord"]) + vec
                    if tuple(pi) not in checked and cell["strength"] > 0:
                        queue = [{"coord": (pi.x, pi.y), "strength": cell["strength"] - (1 if sum(abs(i) for i in vec) == 1 else  1.41421) }] + queue
                        checked += [tuple(pi)]

        checkCell({"coord": tuple(p), "strength": strength})
        while queue:
            el = queue.pop()
            checkCell(el)
        
        return walls, floor

    def getCell(self, p):
        return self.get(Point(p.x // 16, p.y // 16)).field[p.y % 16][p.x % 16]

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
        randnum = self.hash_func(min(p1.x,p2.x), min(p1.y,p2.y), max(p2.x, p1.x), max(p2.y, p1.y))
        if randnum % 5 >= 3: return
        chunk1 = self.get(p1)
        chunk2 = self.get(p2)
        m = min(chunk1.width, chunk2.width)
        randnum = randnum % (m-2) + 9 - m // 2
        
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

    def hash_func(self, *data):
        res = 0
        for x in data:
            res = (res * 31 + x * self.seed) & 0xFFFFFFFF
        return res