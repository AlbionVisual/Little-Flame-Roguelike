import hashlib

class Chunk:
    settings = {
        'LOOT_SPAWN_ATTEMPTS': 5,
        'LOOT_SPAWN_CHANCE': 20,
        'LOOT_TYPES_AMOUNT': 10,
    }

    seed = -1
    hash_max = 4_294_967_295

    def __init__(self, p, *other):
        if other: print('you passed wrong amount of parameters: ', other)
        if not hasattr(self, 'pos'): self.pos = tuple(p)
        self.field = [[[0] for _ in range(16)] for _ in range(16)]
        self.loot = {}
        self.genered = True
        self.genField()
    
    def genField(self):
        for y in range(16):
            for x in range(16):
                rand_num = self.hash_func(x, y, *self.pos)
                self.field[x][y] = [3 if rand_num > 2/4*Chunk.hash_max else 4 if rand_num > 1/4*Chunk.hash_max else 0]

        self.width = 16
        for i in range(Chunk.settings["LOOT_SPAWN_ATTEMPTS"]):
            if self.hash_func(self.width, self.pos[0], self.pos[1], i) % 100 <= Chunk.settings["LOOT_SPAWN_CHANCE"]:
                coord_x = int(self.hash_func(self.width, self.pos[0] * (i + 1), self.pos[1] * (i + 1)) % (self.width - 2) + 9 - self.width // 2)
                coord_y = int(self.hash_func(self.width, self.pos[1] * (i + 1), self.pos[0] * (i + 1)) % (self.width - 2) + 9 - self.width // 2)
                if self.field[coord_x][coord_y] == 3: self.loot[(coord_x, coord_y)] = {'type': self.hash_func(self.width, self.pos[0] * (i + 1), self.pos[1] * (i + 1)) % Chunk.settings["LOOT_TYPES_AMOUNT"], 'pickable': True}

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