from random import randint
from chunk import Chunk # type: ignore

map_types_relation = {
    0: 'nothing',
    1: 'floor',
    2: 'wall',
    3: 'inv_floor',
    4: 'inv_wall',
    5: 'lighten_floor',
    6: 'lighten_wall'
}

class Map:
    settings = {
        'DISPLAY_RANGE': 3
    }
    def __init__(self, seed = -1):
        if seed < 0:
            def isPrime(n):
                for i in range(2, int(n**(1/2) + 1)):
                    if n % i == 0: return False
                return True
            
            seed = randint(1e6,1e10)
            while not isPrime(seed):
                seed = randint(1e6,1e10)
        self.chunk_class = Chunk
        self.seed = seed
        self.chunk_class.seed = seed
        self.chunk_class.settings.update(Map.settings)
        self.chunks = {}
    
    def genArea(self, coords):
        R = Map.settings['DISPLAY_RANGE']
        for x in range(coords[0] - R, coords[0] + R + 1):
            for y in range(coords[1] - R, coords[1] + R + 1):
                if (x - coords[0])**2 + (y - coords[1])**2 <= R**2:
                    self.gen_chunk(x, y)

    def gen_chunk(self, *coords):
        if isinstance(coords[0], (tuple, list)): coords = coords[0]
        coords = tuple(coords)
        if coords in self.chunks:
            return self.chunks[coords]
        else:
            self.chunks[coords] = self.chunk_class(coords)

    def debug_chunk(self, *coords):
        if isinstance(coords[0], (tuple, list)): coords = coords[0]
        if coords in self.chunks:
            from matplotlib import pyplot as plt
            import matplotlib.patches as patches
            fig, ax = plt.subplots()
            plt.xlim(-0.5, 16.5)
            plt.ylim(-0.5, 16.5)
            plt.gca().set_aspect('equal', adjustable='box')

            for y, line in enumerate(self.chunks[coords].field):
                for x, el in enumerate(line):
                    square = patches.Rectangle((x, y), 1, 1, edgecolor='black', facecolor='#' + str(int(el[0]*10/6))*3)
                    ax.add_patch(square)

            plt.show()
        else:
            print('not genered!')

    def get(self, *coords):
        if isinstance(coords[0], (tuple, list)): coords = coords[0]
        if tuple(coords) not in self:
            self.gen_chunk(coords)
        return self.chunks[tuple(coords)]
    
    def __contains__(self, *pos):
        if isinstance(pos[0], (tuple, list)): pos = pos[0]
        return tuple(pos) in self.chunks

    def gen_light(self, pos, strength = 5):
        return self.genTreeLightNoDiag(pos, strength)

    def genTreeLightNoDiag(self, pos, strength = 5):
        vecs = [(-1,0), (0,1), (1,0), (0,-1), (-1,-1), (-1,1), (1,1), (1,-1)]
        walls = set()
        floor = set()
        queue = []
        checked = []

        def checkCell(cell):
            nonlocal queue
            nonlocal checked

            el = self.getCell(*cell["coord"])
            if el[0] in (2, 4, 6):
                walls.add(el[1])
                el[0] = 6
            if el[0] in (1, 3, 5):
                floor.add(el[1])
                el[0] = 5
                for vec in vecs:
                    pi = (cell["coord"][0] + vec[0], cell["coord"][1] + vec[1])
                    if pi not in checked and cell["strength"] > 0:
                        if sum(abs(i) for i in vec) == 1:
                            queue = [{"coord": pi, "strength": cell["strength"] - 1}] + queue
                        elif (self.getCell((pi[0] - vec[0], pi[1]))[0] == 5 # пропускаем клетки, когда сбоку нет подсвеченного пола, а по диагонали пол (опускаем видение сквозь углы)
                           or self.getCell((pi[0], pi[1] - vec[1]))[0] == 5):
                            queue = [{"coord": pi, "strength": cell["strength"] - 1.41421}] + queue
                            continue
                        checked += [pi]

        checkCell({"coord": tuple(pos), "strength": strength})

        while queue:
            el = queue.pop()
            checkCell(el)
        
        return floor, walls

    def genTreeLight(self, pos, strength = 5):
        vecs = [(-1,0), (0,1), (1,0), (0,-1), (-1,-1), (-1,1), (1,1), (1,-1)]
        walls = set()
        floor = set()
        queue = []
        checked = []

        def checkCell(cell):
            nonlocal queue
            nonlocal checked

            el = self.getCell(*cell["coord"])
            if el[0] in (2, 4, 6):
                walls.add(el[1])
                el[0] = 6
            if el[0] in (1, 3, 5):
                floor.add(el[1])
                el[0] = 5
                for vec in vecs:
                    pi = (cell["coord"][0] + vec[0], cell["coord"][1] + vec[1])
                    if pi not in checked and cell["strength"] > 0:
                        queue = [{"coord": pi, "strength": cell["strength"] - (1 if sum(abs(i) for i in vec) == 1 else  1.41421) }] + queue
                        checked += [pi]

        checkCell({"coord": tuple(pos), "strength": strength})

        while queue:
            el = queue.pop()
            checkCell(el)
        
        return floor, walls

    def getCell(self, *coords):
        if isinstance(coords[0], (tuple, list)): coords = coords[0]
        return self.get(coords[0] // 16, coords[1] // 16).field[coords[1] % 16][coords[0] % 16]
