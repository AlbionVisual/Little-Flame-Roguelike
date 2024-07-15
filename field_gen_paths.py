from random import randint
from pprint import pprint as print 
from primitieves import *

class ChunkPaths():
    settings = {
        'LOOT_SPAWN_ATTEMPTS': 5,
        'LOOT_SPAWN_CHANCE': 20,
        'LOOT_TYPES_AMOUNT': 10,
    }
    seed = -1

    def __init__(self, p, new_seed = None):
        if new_seed != None: ChunkPaths.seed = new_seed
        self.p = Vec(*tuple(p))
        self.field = [[[0] for _ in range(16)] for _ in range(16)]
        self.paths = { 'left': -1, 'top': -1, 'right': -1, 'bottom': -1 }
        self.loot = {}
        self.genered = True
        self.pathAdded = False
        self.genField()
    
    def genField(self):
        self.width = ((ChunkPaths.seed * (self.p.x + self.p.y) % 11 + 6) // 2) * 2 # Random staff
        ws = (8 - self.width // 2, 8 + self.width // 2)
        ws1 = (8 - self.width // 2, 8 + self.width // 2 - 1)
        for i in range(*ws):
            for j in range(*ws):
                self.field[i][j] = [3 if i not in ws1 and j not in ws1 else 4]
                
        for i in range(ChunkPaths.settings["LOOT_SPAWN_ATTEMPTS"]):
            if self.hash_func(self.width, self.p.x, self.p.y, i) % 100 <= ChunkPaths.settings["LOOT_SPAWN_CHANCE"]:
                coord_x = int(self.hash_func(self.width, self.p.x * (i + 1), self.p.y * (i + 1)) % (self.width - 2) + 9 - self.width // 2)
                coord_y = int(self.hash_func(self.width, self.p.y * (i + 1), self.p.x * (i + 1)) % (self.width - 2) + 9 - self.width // 2)
                self.loot[(coord_x, coord_y)] = self.hash_func(self.width, self.p.x * (i + 1), self.p.y * (i + 1)) % ChunkPaths.settings["LOOT_TYPES_AMOUNT"]

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

    def hash_func(self, *data):
        res = 0
        for x in data:
            res = (res * 31 + x * ChunkPaths.seed) & 0xFFFFFFFF
        return res

class MapPaths:
    settings = {

    }

    def __init__(self, seed = -1):
        if seed < 0:
            seed = randint(1e6,1e10)
        self.seed = seed
        self.chunks = {}
        ChunkPaths.settings = MapPaths.settings
        self.genArea(Vec(0,0))
    
    def __repr__(self):
        sep = ', '
        return f'Seed: {self.seed}, genered: {sep.join(str(i) for i in self.chunks.keys())}'
    
    def genChunk(self, p):
        self.chunks[tuple(p)] = ChunkPaths(p, self.seed)
    
    def genLight(self, p, f, f_args, strength = 5): # simpliest circle
        p = Vec(*p)
        for i in range(int(p.x) - strength - 3, int(p.x) + strength + 3):
            for j in range(int(p.y) - strength - 3, int(p.y) + strength + 3):
                cell = self.getCell(Vec(i, j))
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
        vecs = [Vec(-1,0), Vec(0,1), Vec(1,0), Vec(0,-1), Vec(-1,-1), Vec(-1,1), Vec(1,1), Vec(1,-1)]
        walls = set()
        floor = set()
        queue = []
        checked = []
        def checkCell(cell):
            nonlocal queue
            nonlocal checked
            el = self.getCell(Vec(*cell["coord"]))
            if el[0] in (2, 4, 6):
                walls.add(el[1])
                el[0] = 6
            if el[0] in (1, 3, 5): 
                floor.add(el[1])
                el[0] = 5
                for vec in vecs:
                    pi = Vec(*cell["coord"]) + vec
                    if tuple(pi) not in checked and cell["strength"] > 0:
                        queue = [{"coord": (pi.x, pi.y), "strength": cell["strength"] - (1 if sum(abs(i) for i in vec) == 1 else  1.41421) }] + queue
                        checked += [tuple(pi)]

        checkCell({"coord": tuple(p), "strength": strength})
        while queue:
            el = queue.pop()
            checkCell(el)
        
        return walls, floor

    def getCell(self, p):
        return self.get(Vec(p.x // 16, p.y // 16)).field[p.y % 16][p.x % 16]

    def get(self, p):
        if p not in self:
            self.genChunk(p)
        if isinstance(p, Vec):
            return self.chunks[(p.x, p.y)]
        else: return self.chunks[(p[0],p[1])]
    
    def genArea(self, p):
        if not isinstance(p, Vec): p = Vec(*p)
        left = Vec(-1,0)
        right = Vec(1,0)
        up = Vec(0,1)
        down = Vec(0,-1)

        # Center
        chunk = self.get(p)
        if chunk.pathAdded == False:
            vecs = [left, right, up, down]
            for vec in vecs:
                self.get(p+vec)
                self.setPath(p, vec)
                self.get(p+vec).addPaths()
            chunk.addPaths()
            chunk.pathAdded = True

        # Left
        p += left
        chunk = self.get(p)
        if chunk.pathAdded == False:
            vecs = [left, up, down]
            for vec in vecs:
                self.get(p+vec)
                self.setPath(p, vec)
                self.get(p+vec).addPaths()
            chunk.addPaths()
            chunk.pathAdded = True

        # Right
        p += right * 2
        chunk = self.get(p)
        if chunk.pathAdded == False:
            vecs = [right, up, down]
            for vec in vecs:
                self.get(p+vec)
                self.setPath(p, vec)
                self.get(p+vec).addPaths()
            chunk.addPaths()
            chunk.pathAdded = True

        # Up
        p += left + up
        chunk = self.get(p)
        if chunk.pathAdded == False:
            vecs = [right, up, left]
            for vec in vecs:
                self.get(p+vec)
                self.setPath(p, vec)
                self.get(p+vec).addPaths()
            chunk.addPaths()
            chunk.pathAdded = True

        # Down
        p += down * 2
        chunk = self.get(p)
        if chunk.pathAdded == False:
            vecs = [right, down, left]
            for vec in vecs:
                self.get(p+vec)
                self.setPath(p, vec)
                self.get(p+vec).addPaths()
            chunk.addPaths()
            chunk.pathAdded = True

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