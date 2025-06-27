from .game_setup import GameSetup
from .utils.sprites import *
from .generators.map import map_types_relation
from .generators.map import Map
from .generators.map_layers import MapLayers
from .generators.field_gen_paths import MapPaths

class GameMapGenerator(GameSetup):

    def setup(self, seed = -1, **new_settings):

        super().setup(**new_settings)

        Algorithm_class = globals()[self.settings["ALGORITHM_NAME"]]
        Map.settings = self.settings
        self.map = Algorithm_class(seed)
        print('Seed: ', self.map.seed)

        self.gen_map()
        self.drawn_chunks = set()
        self.draw_map()
        self.lighten = (set(), set())

    def gen_map(self):
        chunk_x, chunk_y = self.player_sprite.get_chunk()
        self.map.genArea((chunk_x, chunk_y))

        self.player_sprite.chunk = self.player_sprite.get_chunk()

    def draw_map(self, chunk_x = None, chunk_y = None):

        # self.scene.get_sprite_list("Enemies").clear()
        self.scene.get_sprite_list("Loot").clear()
        self.scene.get_sprite_list("Items").clear()

        # Count player's chunk as center one 
        if chunk_x == None: chunk_x = self.player_sprite.chunk[0]
        if chunk_y == None: chunk_y = self.player_sprite.chunk[1]

        # For every chunk placed in distance not greater than R from center
        R = self.settings['DISPLAY_RANGE']
        drawn_chunks = set()
        for x in range(int(chunk_x - R), int(chunk_x + R + 1)):
            for y in range(int(chunk_y - R), int(chunk_y + R + 1)):
                chunk = self.map.get((x, y))

                # for every loot in chunk
                for coord, data in chunk.loot.items():                      
                    xi, yi = coord
                    if chunk.field[yi][xi][0] in (1, 5): loot = LootSprite(self.loot_textures[data['type']], pickable=data['pickable'])
                    else: loot = LootSprite(pickable=data['pickable'])
                    loot.center_x = self.settings['TILE_SIZE'] * 16 * x + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * xi
                    loot.center_y = self.settings['TILE_SIZE'] * 16 * y + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * yi
                    loot.pos = (xi, yi)
                    xl, yl = (xi + tuple(chunk.pos)[0] * 16, yi + tuple(chunk.pos)[1] * 16)
                    if not data['pickable'] and (xl, yl) in self.active_loot:
                        self.active_loot[(xl, yl)] = loot
                        loot.is_active = True
                    loot.type = data['type']
                    loot.chunk = (x, y)
                    chunk.loot[coord]['sprite'] = loot
                    self.scene.add_sprite("Loot" if data["pickable"] else "Items", loot)

                # for every enemy in chunk
                to_remove = []
                for (xi, yi), data in chunk.enemies.items():
                    if 'sprite' not in data.keys():
                        enemy = EnemyCharacter()
                        if chunk.field[yi][xi][0] in (1, 5):
                            enemy.visible = True
                        enemy.center_x = self.settings['TILE_SIZE'] * 16 * x + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * xi
                        enemy.center_y = self.settings['TILE_SIZE'] * 16 * y + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * yi
                        enemy.pos = (xi, yi)
                        enemy.chunk = (x, y)
                        chunk.enemies[(xi, yi)]['sprite'] = enemy
                        self.scene.add_sprite("Enemies", enemy)
                    else:
                        enemy = data['sprite']
                        # self.scene.add_sprite("Enemies", enemy)
                        to_remove+=[(xi,yi)]
                        # self.map.get(enemy.get_chunk()).enemies[enemy.pos]
                        # enemy.chunk = enemy.get_chunk()
                        
                for key in to_remove:
                    del chunk.enemies[key]
                
                if (x - chunk_x)**2 + (y - chunk_y)**2 > R**2: continue # skip chunks not in a circle
                drawn_chunks.add((x, y))
                if (x, y) in self.drawn_chunks: continue # skip already drawn chunks

                # for all cells in chunk
                for i, line in enumerate(chunk.field):
                    for j, cell in enumerate(line):
                        tile_type = map_types_relation[cell[0]]
                        if tile_type != 'nothing': # if cell has sth
                            if len(cell) == 1:                              # create new sprite if there isn't one yet
                                cell += [TileSprite()]
                                cell[1].center_x = self.settings['TILE_SIZE'] // 2 + j * self.settings['TILE_SIZE'] + self.settings['TILE_SIZE'] * 16 * x
                                cell[1].center_y = self.settings['TILE_SIZE'] // 2 + i * self.settings['TILE_SIZE'] + self.settings['TILE_SIZE'] * 16 * y
                            if tile_type[:7] == 'lighten': 
                                print('err: lighten tile tried to generate!')
                                continue
                            if tile_type[:3] == 'inv':                      # set hitbox for invisibles
                                # cell[1].set_hit_box(self.settings['TILE_HIT_BOX'])
                                ...
                            else:
                                cell[1].change_texture(light = 0)           # or set texture for visibles
                            if tile_type[-4:] == 'wall':
                                if cell[1] in self.scene.get_sprite_list("Floor"):
                                    print('err: drawing the wall already in sprite list')
                                else: 
                                    self.scene.add_sprite("Walls", cell[1])
                            else:
                                if cell[1] in self.scene.get_sprite_list("Floor"):
                                    print('err: drawing the floor already in sprite list!')
                                else: 
                                    self.scene.add_sprite("Floor", cell[1])

        for x, y in self.drawn_chunks - drawn_chunks:                       # for every far chunk
            chunk = self.map.get((x, y))
            for i, line in enumerate(chunk.field):
                for j, cell in enumerate(line):
                    if len(cell) == 2:                                      # for every cell with tile sprite
                        tile_type = map_types_relation[cell[0]]
                        if tile_type[-4:] == 'wall':
                            self.scene.get_sprite_list("Walls").remove(cell[1])
                        else:
                            self.scene.get_sprite_list("Floor").remove(cell[1])

        self.drawn_chunks = drawn_chunks