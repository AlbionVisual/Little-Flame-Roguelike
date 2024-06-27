from random import randint
from pprint import pprint as print 
from primitieves import *

class Chunk():
    field = [[0]*16]*16

    def __init__(self, p):
        self.field = self.genField()
    
    def genField(self, p1, p2):
        ...

class Map:
    seed = -1
    chunks = {(0,0):[]}

    def __init__(self, seed = -1):
        if seed < 0:
            seed = randint(1e6,1e10)
        self.seed = seed
    
    def __repr__(self):
        return self.field.__str__()


p1 = Point(1,2)
p2 = Point(3,7)
print(p1 * 2 + p2)