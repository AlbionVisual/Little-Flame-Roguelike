import hashlib

class Chunk:
    settings = {
        'LOOT_SPAWN_ATTEMPTS': 5,
        'LOOT_SPAWN_CHANCE': 20,
        'LOOT_TYPES_AMOUNT': 10,
        'ENEMIES_SPAWN_CHANCE': 10,
        'BORDERS': {
            'LEFT': -1,
            'RIGHT': -1,
            'UP': -1,
            'DOWN': -1
        },
    }

    seed = -1
    hash_max = 4_294_967_295

    def init_vars(self, p):
        if not hasattr(self, 'pos'): self.pos = tuple(p)
        self.field = [[[0] for _ in range(16)] for _ in range(16)]
        self.loot = {}
        self.enemies = {}
        self.genered = True

    def __init__(self, p, *other):
        if other: print('you passed wrong amount of parameters: ', other)
        self.init_vars(p)

        self.genField()
        self.spawn_loot()
        self.spawn_enemies()

        self.check_borders()

    def genField(self):
        for y in range(16):
            for x in range(16):
                rand_num = self.hash_func(x, y, *self.pos)
                self.field[x][y] = [3 if rand_num > self.settings['WALL_SPAWN_CHANCE']*Chunk.hash_max else 4]

    def spawn_loot(self):
        for i in range(Chunk.settings["LOOT_SPAWN_ATTEMPTS"]):
            if self.hash_func(self.pos[0], self.pos[1], i)//100 % 100 <= Chunk.settings["LOOT_SPAWN_CHANCE"]:
                coord_x = int(self.hash_func(self.pos[0] * (i + 1), self.pos[1] * (i + 1)) % 16)
                coord_y = int(self.hash_func(self.pos[1] * (i + 1), self.pos[0] * (i + 1)) % 16)
                # print('New loot, cell: ', self.field[coord_x][coord_y][0])
                if self.field[coord_x][coord_y][0] == 3: self.loot[(coord_x, coord_y)] = {'type': self.hash_func(self.pos[0] * (i + 1), self.pos[1] * (i + 1)) % Chunk.settings["LOOT_TYPES_AMOUNT"], 'pickable': True}
    
    def spawn_enemies(self):
        for i in range(Chunk.settings["ENEMIES_SPAWN_ATTEMPTS"]):
            if self.hash_func(self.pos[0], self.pos[1], i) % 100 <= Chunk.settings["ENEMIES_SPAWN_CHANCE"]:
                coord_x = int(self.hash_func(self.pos[0], self.pos[1]) % 16)
                coord_y = int(self.hash_func(self.pos[1], self.pos[0]) % 16)
                if self.field[coord_x][coord_y][0] == 3: self.enemies[(coord_x, coord_y)] = {}
                # print(('Enemy gened:', coord_x, coord_y, self.pos[0], self.pos[1]))

    def check_borders(self):
        if self.settings['BORDERS']['RIGHT'] != -1 and self.pos[0] > self.settings['BORDERS']['RIGHT']:
            for i in range(16):
                self.field[i][15] = [4]
        if self.settings['BORDERS']['LEFT'] != -1 and self.pos[0] < -self.settings['BORDERS']['LEFT']:
            for i in range(16):
                self.field[i][0] = [4]
        if self.settings['BORDERS']['UP'] != -1 and self.pos[1] > self.settings['BORDERS']['UP']:
            for i in range(16):
                self.field[15][i] = [4]
        if self.settings['BORDERS']['DOWN'] != -1 and self.pos[1] < -self.settings['BORDERS']['DOWN']:
            for i in range(16):
                self.field[0][i] = [4]

    def __repr__(self, show = False):
        if show: print(self.field)
        return f'Chunk {self.pos}'

    def hash_func(*args):
        input_data = str(Chunk.seed).encode('utf-8') + b''.join(str(arg).encode('utf-8') for arg in args)
        hash_object = hashlib.sha256(input_data)
        hash_bytes = hash_object.digest()
        random_number = int.from_bytes(hash_bytes[:4], byteorder='big')
        return random_number

# type: ignore