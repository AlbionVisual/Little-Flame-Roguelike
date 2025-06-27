import hashlib
from pprint import pprint as print 
from .primitieves import *
from .map import Map
from .chunk import Chunk # type: ignore

class ChunkPaths(Chunk):
    seed = -1

    def __init__(self, p):
        self.pos = Vec(*tuple(p))
        super().__init__(p)
        self.paths = { 'left': -1, 'top': -1, 'right': -1, 'bottom': -1 }
        self.genered = True
        self.pathAdded = False
    
    def genField(self):
        self.width = ((ChunkPaths.seed * (self.pos.x + self.pos.y) % 11 + 6) // 2) * 2 # Random staff
        ws = (8 - self.width // 2, 8 + self.width // 2)
        ws1 = (8 - self.width // 2, 8 + self.width // 2 - 1)
        for i in range(*ws):
            for j in range(*ws):
                self.field[i][j] = [3 if i not in ws1 and j not in ws1 else 4]
                
        for i in range(ChunkPaths.settings["LOOT_SPAWN_ATTEMPTS"]):
            if self.hash_func(self.width, self.pos.x, self.pos.y, i) % 100 <= ChunkPaths.settings["LOOT_SPAWN_CHANCE"]:
                coord_x = int(self.hash_func(self.width, self.pos.x * (i + 1), self.pos.y * (i + 1)) % (self.width - 2) + 9 - self.width // 2)
                coord_y = int(self.hash_func(self.width, self.pos.y * (i + 1), self.pos.x * (i + 1)) % (self.width - 2) + 9 - self.width // 2)
                self.loot[(coord_x, coord_y)] = {'type': self.hash_func(self.width, self.pos.x * (i + 1), self.pos.y * (i + 1)) % ChunkPaths.settings["LOOT_TYPES_AMOUNT"], 'pickable': True}
        
        if self.hash_func(self.width, self.pos.x, self.pos.y, i) % 100 <= ChunkPaths.settings["ENEMIES_SPAWN_CHANCE"]:
            coord_x = int(self.hash_func(self.pos.x, self.pos.y, self.width) % (self.width - 2) + 9 - self.width // 2)
            coord_y = int(self.hash_func(self.pos.y, self.pos.x, self.width) % (self.width - 2) + 9 - self.width // 2)
            self.enemies[(coord_x, coord_y)] = {}
            # print(('Enemy gened:', coord_x, coord_y, self.pos.x, self.pos.y))

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
        
        self.check_borders()

class MapPaths(Map):
    hash_max = 4_294_967_295
    def __init__(self, seed = -1):
        super().__init__(seed)
        # ChunkPaths.settings.update(MapPaths.settings)
        self.genArea(Vec(0,0))
    
    def __repr__(self):
        sep = ', '
        return f'Seed: {self.seed}, genered: {sep.join(str(i) for i in self.chunks.keys())}'
    
    def gen_chunk(self, p):
        self.chunks[tuple(p)] = ChunkPaths(p)
    
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
        
    def get(self, *coords):
        if isinstance(coords[0], (tuple,list,Vec)): coords = coords[0]
        if tuple(coords) not in self:
            self.gen_chunk(coords)
        return self.chunks[tuple(coords)]
    
    def genArea(self, p, start = None):
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
        
        p += up

        R = self.settings["DISPLAY_RANGE"]
        if start == None:
            start = p
            for i in range(int(start.x - R), int(start.x + R + 1)):
                for j in range(int(start.y - R), int(start.y + R + 1)):
                    pi = start + right * i + up * j
                    if (pi + start*(-1)).dist() > R**2: continue
                    self.genArea(pi, start)
                    # print()

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
    
    def hash_func(*args):
        input_data = str(Chunk.seed).encode('utf-8') + b''.join(str(arg).encode('utf-8') for arg in args)
        hash_object = hashlib.sha256(input_data)
        hash_bytes = hash_object.digest()
        random_number = int.from_bytes(hash_bytes[:4], byteorder='big')
        return random_number