from .map import Map
from .chunk import Chunk # type: ignore

class ChunkLayers(Chunk):
    def __init__(self, p, *args):
        self.init_vars(p)
        
        super().__init__(p, *args)

    def init_consts():
        ChunkLayers.layers_offsets = []
        ChunkLayers.layers_weights = []
        weights_sum = 0
        ChunkLayers.layers_offsets = [[0,0]for _ in range(ChunkLayers.settings['AMOUNT_OF_LAYERS'])]
        ChunkLayers.layers_offsets[2] = [1,1]
        ChunkLayers.layers_offsets[3] = [3,3]
        for i in range(ChunkLayers.settings['AMOUNT_OF_LAYERS']):
            # ChunkLayers.layers_offsets += [(ChunkLayers.hash_func(2**i + 1, 7) % (2**i),
            #                         ChunkLayers.hash_func(2**i + 1, 11) % (2**i))]
            ChunkLayers.layers_weights += [ChunkLayers.hash_func(2**i + 31, 17) % (ChunkLayers.hash_max - 2*ChunkLayers.settings['MIN_WEIGHTS_COFF'] * ChunkLayers.hash_max) + ChunkLayers.settings['MIN_WEIGHTS_COFF'] * ChunkLayers.hash_max]
            weights_sum += ChunkLayers.layers_weights[-1]
        ChunkLayers.layers_weights = [i / weights_sum for i in ChunkLayers.layers_weights]
        # print("\nOffsets: ",ChunkLayers.layers_offsets, "\nWeights: ", ChunkLayers.layers_weights)

    def genField(self):
        for y in range(16):
            for x in range(16):
                rand_num = self.cell_value(x, y)
                self.field[x][y] = [3 if rand_num > self.settings['WALL_SPAWN_CHANCE']*ChunkLayers.hash_max else 4]
    
    def cell_value(self, x, y):
        x_all = x + self.pos[0] * 16
        y_all = y + self.pos[1] * 16
        cell_sum = 0
        for i in range(self.settings['AMOUNT_OF_LAYERS']):
            xi = x_all // 2**i + ChunkLayers.layers_offsets[i][0]
            yi = y_all // 2**i + ChunkLayers.layers_offsets[i][1]
            cell_sum += self.hash_func(xi, yi,2**i + 1) * ChunkLayers.layers_weights[i]
        return cell_sum

class MapLayers(Map):
    def __init__(self, *args):
        super().__init__(*args)
        self.chunk_class = ChunkLayers
        ChunkLayers.init_consts()