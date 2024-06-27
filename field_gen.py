from random import randint
from pprint import pprint as print 
from primitieves import *

seed = 7687906

class Chunk():
    field = [[0]*16 for _ in range(16)]
    p = Point()

    def __init__(self, p, seed):
        self.genField(p, seed)
        self.p = p
    
    def genField(self, p, seed):
        width = (seed * (p.x + p.y) % 13 + 4) # Random staff
        for i in range(8 - width // 2, 8 + width // 2):
            for j in range(8 - width // 2, 8 + width // 2):
                self.field[i][j] = 1 if i not in (8 - width // 2, 8 + width // 2 - 1) and j not in (8 - width // 2, 8 + width // 2 - 1) else 2

    def __repr__(self):
        print(f'Chunk {self.p}')
        print(self.field)
        return ''

class Map:
    seed = -1
    chunks = {(0,0):[]}

    def __init__(self, seed = -1):
        if seed < 0:
            seed = randint(1e6,1e10)
        self.seed = seed
    
    def __repr__(self):
        return self.field.__str__()


p1 = Point(1,0)
p2 = Point(3,7)
c = Chunk(p1, seed)
print(c)