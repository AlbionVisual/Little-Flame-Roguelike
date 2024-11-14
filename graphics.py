import arcade
# from field_gen_paths import MapPaths
from map import Map as MapPaths

default_settings = {
    'SCREEN_WIDTH': 1000,
    'SCREEN_HEIGHT': 650,
    'SCREEN_TITLE': "Simple Roguelike graphics",
    'CHARACTER_SCALING': 1 / 16,
    'TILE_SCALING': 2,
    'LOOT_SCALING': 2,
    'TILE_SIZE': 32,
    'RIGHT_FACING': 0,
    'LEFT_FACING': 1,
    'PLAYER_MOVEMENT_SPEED': 3,
    'PLAYER_ANIM_FRAMES': 33,
    'TILE_HIT_BOX': ((-8.0, -8.0), (8.0, -8.0), (8.0, 8.0), (-8.0, 8.0)),
    'LOOT_HIT_BOX': ((-8.0, -8.0), (8.0, -8.0), (8.0, 8.0), (-8.0, 8.0)),
    'FLOOR_TEXTURE': "Textures/concrete_gray_darken.png",
    'WALL_TEXTURE': "Textures/concrete_gray.png",
    'LIGHTEN_FLOOR_TEXTURE': "Textures/hardened_clay_stained_yellow_darken.png",
    'LIGHTEN_WALL_TEXTURE': "Textures/concrete_yellow.png",
    'LOG_TEXTURE': "Textures/log.png",
    'LOOT_SPAWN_ATTEMPTS': 5,
    'LOOT_SPAWN_CHANCE': 60,
    'LOOT_TYPES_AMOUNT': 10,
    'ANIM_MOVEMENT_RANGE': 5,
    'PICKABLES_RESCALING': 0.8,
    'DISPLAY_RANGE': 3,
}

def load_texture_pair(filename):
    flipped_img = arcade.load_texture(filename, flipped_horizontally=True)
    img = arcade.load_texture(filename)
    return [img, flipped_img]

class PlayerCharacter(arcade.Sprite):
    settings = { # This data works if sth wrong!
        'RIGHT_FACING': 0,
        'LEFT_FACING': 1,
        'CHARACTER_SCALING': 1,
        'PLAYER_ANIM_FRAMES': 10,
        'TILE_SIZE': 128
    }
    
    def __init__(self):
        super().__init__()
        self.character_face_direction = PlayerCharacter.settings['RIGHT_FACING']
        self.cur_texture = 0
        self.scale = PlayerCharacter.settings['CHARACTER_SCALING']
        self.chunk = (0, 0)
        self.walk_textures = [
            load_texture_pair("Textures/flame/flame_{0:02d}.png".format(i)) for i in range(PlayerCharacter.settings['PLAYER_ANIM_FRAMES'])
        ]
        self.texture = self.walk_textures[0][self.character_face_direction]
        self.hit_box = self.texture.hit_box_points

    def get_chunk(self):
        return (int(self.center_x // (16 * PlayerCharacter.settings['TILE_SIZE'])), int(self.center_y // (16 * PlayerCharacter.settings['TILE_SIZE'])))

    def update_animation(self, delta_time: float = 1 / 60):

        if self.change_x < 0 and self.character_face_direction == PlayerCharacter.settings['RIGHT_FACING']:
            self.character_face_direction = PlayerCharacter.settings['LEFT_FACING']
        elif self.change_x > 0 and self.character_face_direction == PlayerCharacter.settings['LEFT_FACING']:
            self.character_face_direction = PlayerCharacter.settings['RIGHT_FACING']
        self.cur_texture += 1
        if self.cur_texture >= PlayerCharacter.settings['PLAYER_ANIM_FRAMES']:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class TileSprite(arcade.Sprite):
    settings = { # This data works if sth wrong!
        'TILE_SCALING': 1
    }
    def __init__(self, texture = 'invisible'):
        super().__init__(scale = TileSprite.settings['TILE_SCALING'])
        if texture[:3] != 'inv': self.change_texture(texture)
    
    def change_texture(self, texture):
        self.texture = texture

class LootSprite(arcade.Sprite):
    settings = { # This data works if sth wrong!
        'LOOT_SCALING': 1,
        'PICKABLES_RESCALING': 0.8,
        'ANIM_MOVEMENT_RANGE': 10,
    }
    def __init__(self, texture = None, pickable = True):
        super().__init__(scale = LootSprite.settings['LOOT_SCALING'])

        self.amount = 1

        self.chunk = None
        self.pos = None

        if texture is not None: self.change_texture(texture)
        self.pickable = pickable
        if pickable: self.scale *= LootSprite.settings['PICKABLES_RESCALING']
        self.type = None
        
        self.offset_y = 0
        self.offset_x = 0
        self.moving_up = True
        self.moving_right = True
        self.is_active = False

        self.checked_anim = True
    
    def change_texture(self, texture):
        self.texture = texture

    def update_animation(self, delta_time: float = 1 / 30):
        if self.texture is not None:
            if self.pickable:
                if self.moving_up:
                    if self.offset_y <= LootSprite.settings['ANIM_MOVEMENT_RANGE'] / 2: self.offset_y += 1
                    else: self.moving_up = False
                else:
                    if self.offset_y >= -LootSprite.settings['ANIM_MOVEMENT_RANGE'] / 2: self.offset_y += -1
                    else: self.moving_up = True
                self.center_y += self.offset_y // abs(self.offset_y) if self.offset_y != 0 else 0
            elif self.is_active:
                if self.moving_right:
                    if self.offset_x <= LootSprite.settings['ANIM_MOVEMENT_RANGE'] / 8: self.offset_x += 1
                    else: self.moving_right = False
                else:
                    if self.offset_x >= -LootSprite.settings['ANIM_MOVEMENT_RANGE'] / 8: self.offset_x += -1
                    else: self.moving_right = True
                self.center_x += self.offset_x // abs(self.offset_x) if self.offset_x != 0 else 0

class Roguelike(arcade.Window):
    def __init__(self, seed = -1, **new_settings):
        self.settings = default_settings
        for option in new_settings:
            self.settings[option] = new_settings[option]
        PlayerCharacter.settings = self.settings
        TileSprite.settings = self.settings
        LootSprite.settings = self.settings
        self.seed = seed
        super().__init__(self.settings['SCREEN_WIDTH'], self.settings['SCREEN_HEIGHT'], self.settings['SCREEN_TITLE'])
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.scene = None
        self.player_sprite = None
        self.camera = None
        self.physics_engine = None
        self.lighten = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.gui_camera = None
        self.score = None
        self.active_loot = None

        self.debug_show = False

    def setup(self):
        self.tile_textures = {
            "floor": arcade.load_texture(self.settings['FLOOR_TEXTURE']), 
            "wall": arcade.load_texture(self.settings['WALL_TEXTURE']),
            "lighten_floor": arcade.load_texture(self.settings['LIGHTEN_FLOOR_TEXTURE']),
            "lighten_wall": arcade.load_texture(self.settings['LIGHTEN_WALL_TEXTURE'])
        }
        self.loot_textures = [
            arcade.load_texture('Textures/apple.png'),
            arcade.load_texture('Textures/book.png'),
            arcade.load_texture('Textures/carrot.png'),
            arcade.load_texture('Textures/compass.png'),
            arcade.load_texture('Textures/chainmail_helmet.png'),
            arcade.load_texture('Textures/feather.png'),
            arcade.load_texture('Textures/fish.png'),
            arcade.load_texture('Textures/stone_sword.png'),
            arcade.load_texture('Textures/wood_axe.png'),
            arcade.load_texture('Textures/stick.png')
        ]
        self.interface_textures = {
            "selector": arcade.load_texture('Textures/frame.png')
        }

        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Loot", use_spatial_hash=True)
        self.scene.add_sprite_list("Items", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")
    
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = self.settings['TILE_SIZE'] * 7 + self.settings['TILE_SIZE'] // 2
        self.player_sprite.center_y = self.settings['TILE_SIZE'] * 7 + self.settings['TILE_SIZE'] // 2
        self.scene.add_sprite("Player", self.player_sprite)

        MapPaths.settings = self.settings
        self.map = MapPaths(self.seed)
        print('Seed: ', self.map.seed)

        self.gen_map()
        self.draw_map()
        self.lighten = (set(), set())
        arg = self.map.genTreeLight(
                (self.player_sprite.center_x // self.settings['TILE_SIZE'], self.player_sprite.center_y // self.settings['TILE_SIZE'])
        )
        self.change_lights(arg)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

        self.interface = arcade.Scene()
        self.interface.add_sprite_list("Icons", use_spatial_hash=True)
        self.interface.add_sprite_list("Selector", use_spatial_hash=True)

        self.selector_sprite = arcade.Sprite(scale=1.25)
        self.selector_sprite.texture = self.interface_textures["selector"]
        self.selector_sprite.center_x = self.settings["TILE_SIZE"] // 2 + 4
        self.selector_sprite.center_y = self.settings["TILE_SIZE"] // 2 + 4
        self.selector_sprite.slot = 0
        self.interface.add_sprite("Selector", self.selector_sprite)

        self.labels = []

        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        self.score = []
        self.active_loot = {}
    
    def process_keychange(self):
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = self.settings['PLAYER_MOVEMENT_SPEED']
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -self.settings['PLAYER_MOVEMENT_SPEED']
        else:
            self.player_sprite.change_x = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = self.settings['PLAYER_MOVEMENT_SPEED']
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -self.settings['PLAYER_MOVEMENT_SPEED']
        else:
            self.player_sprite.change_y = 0

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right_pressed = True
        elif key == arcade.key.E:
            self.pickup("Items")
        elif key == arcade.key.Q:
            self.drop()
        elif key == arcade.key.F4:
            self.map.debug_chunk(self.player_sprite.chunk)
        elif 49 <= key <= 57: # numbers
            self.selector_sprite.center_y = self.settings["TILE_SIZE"] // 2 + 4 + (self.settings["TILE_SIZE"] + 8) * (key - 49)
            self.selector_sprite.slot = key - 49
        elif key == arcade.key.F3:
            self.debug_show = not self.debug_show
        self.process_keychange()
    
    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right_pressed = False

        self.process_keychange()

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - self.camera.viewport_width / 2
        screen_center_y = self.player_sprite.center_y - self.camera.viewport_height / 2

        self.camera.move_to((screen_center_x, screen_center_y))

    def gen_map(self):
        self.scene.get_sprite_list("Walls").clear()

        chunk_x, chunk_y = self.player_sprite.get_chunk()
        self.map.genArea((chunk_x, chunk_y))

        self.player_sprite.chunk = self.player_sprite.get_chunk()
    
    def change_lights(self, new_lights):
        for i in range(2):
            for cell in self.lighten[i] - new_lights[i]:
                if i == 1: cell.change_texture(self.tile_textures["floor"])
                else: cell.change_texture(self.tile_textures["wall"])

            for cell in new_lights[i] - self.lighten[i]:
                if i == 1: cell.change_texture(self.tile_textures["lighten_floor"])
                else: cell.change_texture(self.tile_textures["lighten_wall"])
        
        for loot in self.scene["Loot"]:
            if self.map.get(loot.chunk).field[loot.pos[1]][loot.pos[0]][0] == 5:
                loot.change_texture(self.loot_textures[loot.type])


        self.lighten = new_lights

    def check_crafts(self):
        templates = [
            { # Sword
                'res': 7,
                'craft':[
                    ['#'],
                    ['#'],
                    ['$']
                ],
                'amount': 1
            },
            { # Axe
                'res': 8,
                'craft':[
                    ['#', '#'],
                    ['$', '#'],
                    ['$', '*']
                ],
                'amount': 1
            },
            { # Apple 
                'res': 0,
                'craft':[
                    ['*', '$', '#', '*'],
                    ['#', '$', '#', '#'],
                    ['#', '#', '#', '#'],
                    ['*', '#', '#', '*']
                ],
                'amount': 12
            }
        ]

        min_x = int(self.player_sprite.center_x // self.settings['TILE_SIZE']) + 7
        max_x = int(self.player_sprite.center_x // self.settings['TILE_SIZE']) - 7
        min_y = int(self.player_sprite.center_y // self.settings['TILE_SIZE']) + 7
        max_y = int(self.player_sprite.center_y // self.settings['TILE_SIZE']) - 7
        field = [[None] * 14 for _ in range(14)]
        start_x, start_y = max_x, max_y

        def check_for_colision(craft, x, y):
            nonlocal field
            sym_types = {}
            for i, line in enumerate(reversed(craft)):
                if field[x - 1][y + i] != None: return False
                if field[x + len(craft[0])][y + i] != None: return False
                for j, patt in enumerate(line):
                    if field[x + j][y - 1] != None: return False
                    if field[x + j][y + len(craft)] != None: return False
                    if patt == '*': 
                        if field[x + j][y + i] != None: return False
                    else:
                        if field[x + j][y + i] == None: return False
                        if patt in sym_types and field[x + j][y + i] != sym_types[patt]: return False
                        else: 
                            if field[x + j][y + i] in sym_types.values() and patt not in sym_types: return False
                            else: sym_types[patt] = field[x + j][y + i]
            return True

        def bring_back(pattern):
            # print("calling bring back")
            nonlocal min_y, min_x, max_x, max_y, field, start_y, start_x
            for i in range(min_x, max_x - len(pattern[0]) + 1):
                for j in range(min_y, max_y - len(pattern) + 1):
                    if check_for_colision(pattern, i - start_x, j - start_y):
                        return (i, j)
            return False

        for coord, loot in self.active_loot.items():
            if coord[0] > max_x: max_x = coord[0]
            if coord[0] < min_x: min_x = coord[0]
            if coord[1] > max_y: max_y = coord[1]
            if coord[1] < min_y: min_y = coord[1]
            field[coord[0] - start_x][coord[1] - start_y] = loot.type
        
        max_x += 1
        max_y += 1

        for temp in templates:
            res = bring_back(temp['craft'])
            if res:
                for i in range(len(temp['craft'][0])):
                    for j in range(len(temp['craft'])):
                        cords = (res[0] + i, res[1] + j)
                        if cords in self.active_loot:
                            loot = self.active_loot[cords]
                            del self.active_loot[cords]
                            loot.remove_from_sprite_lists()
                            del self.map.get(loot.chunk).loot[loot.pos]
                
                res = (res[0] + len(temp['craft'][0]) // 2, res[1] + len(temp['craft']) // 2)
                x, y = (i // 16 for i in res)
                xi, yi = (i % 16 for i in res)
                chunk = self.map.get((x, y))
                loot = LootSprite(self.loot_textures[temp['res']], pickable=True)
                loot.set_hit_box(self.settings['LOOT_HIT_BOX'])
                loot.center_x = self.settings['TILE_SIZE'] * 16 * x + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * xi
                loot.center_y = self.settings['TILE_SIZE'] * 16 * y + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * yi
                loot.pos = (xi, yi)
                loot.type = temp['res']
                loot.amount = temp['amount']
                loot.chunk = (x, y)
                chunk.loot[(xi, yi)] = {'type': temp['res'], 'sprite': loot}
                self.scene.add_sprite("Loot", loot)

                # print(temp['res'], res)
                return
        
    def draw_map(self, chunk_x = None, chunk_y = None):
        if chunk_x == None: chunk_x = self.player_sprite.chunk[0]
        if chunk_y == None: chunk_y = self.player_sprite.chunk[1]
        self.scene["Loot"].clear()
        self.scene["Items"].clear()
        for x in range(chunk_x - 1, chunk_x + 2):
            for y in range(chunk_y - 1, chunk_y + 2):
                chunk = self.map.get((x, y))
                for i, line in enumerate(chunk.field):
                    for j, cell in enumerate(line):
                        if cell[0] != 0:
                            if cell[0] in (5, 6): cell[0] -= 4
                            chunk.field[i][j] = [cell[0], TileSprite()]
                            chunk.field[i][j][1].center_x = self.settings['TILE_SIZE'] // 2 + j * self.settings['TILE_SIZE'] + self.settings['TILE_SIZE'] * 16 * x
                            chunk.field[i][j][1].center_y = self.settings['TILE_SIZE'] // 2 + i * self.settings['TILE_SIZE'] + self.settings['TILE_SIZE'] * 16 * y
                            if cell[0] == 3:
                                chunk.field[i][j][1].set_hit_box(self.settings['TILE_HIT_BOX'])
                                self.scene.add_sprite("Floor", chunk.field[i][j][1])
                            elif cell[0] == 4:
                                chunk.field[i][j][1].set_hit_box(self.settings['TILE_HIT_BOX'])
                                self.scene.add_sprite("Walls", chunk.field[i][j][1])
                            elif cell[0] == 1:
                                chunk.field[i][j][1].change_texture(self.tile_textures["floor"])
                                self.scene.add_sprite("Floor", chunk.field[i][j][1])
                            elif cell[0] == 2:
                                chunk.field[i][j][1].change_texture(self.tile_textures["wall"])
                                self.scene.add_sprite("Walls", chunk.field[i][j][1])
                for coord, data in chunk.loot.items():
                    xi, yi = coord
                    if chunk.field[yi][xi][0] in (1, 5): loot = LootSprite(self.loot_textures[data['type']], pickable=data['pickable'])
                    else: loot = LootSprite(pickable=data['pickable'])
                    loot.set_hit_box(self.settings['LOOT_HIT_BOX'])
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

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.center_camera_to_player()
        if self.player_sprite.get_chunk() != self.player_sprite.chunk:
            self.gen_map()
            self.draw_map()

        # self.map.genLight(
        #     (self.player_sprite.center_x / self.settings['TILE_SIZE'], self.player_sprite.center_y / self.settings['TILE_SIZE']),
        #     lambda cell, arg: cell[1].change_texture(arg),
        #     (0, self.tile_textures["floor"], self.tile_textures["wall"], 0, 0, self.tile_textures["lighten_floor"], self.tile_textures["lighten_wall"])
        # )

        arg = self.map.genTreeLight(
                (int(self.player_sprite.center_x // self.settings['TILE_SIZE']), int(self.player_sprite.center_y // self.settings['TILE_SIZE']))
        )
        if arg != self.lighten: self.change_lights(arg)

        self.pickup()

        for cords, loot in list(self.active_loot.items()):
            if self.map.get(loot.chunk).field[loot.pos[1]][loot.pos[0]][1].texture != self.tile_textures['lighten_floor']:
                loot.is_active = False
                del self.active_loot[cords]

        footed_loot = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Items"] 
        )
        for loot in footed_loot:
            x, y = (loot.pos[i] + val * 16 for i, val in enumerate(loot.chunk))
            if (x, y) not in self.active_loot:
                loot.is_active = True
                self.active_loot[(x, y)] = loot
                if len(self.active_loot) > 1: self.check_crafts()

        self.scene.update_animation(
            delta_time, ["Player", "Loot", "Items"]
        )
    
    def drop(self, all = False):
        if not all:
            slot = self.selector_sprite.slot
            if len(self.score) > slot and self.score[slot] > 0:
                posx, posy = (int(i // self.settings['TILE_SIZE']) for i in self.player_sprite.position)
                chunk = self.map.get((posx // 16, posy // 16))
                if (posx % 16, posy % 16) not in chunk.loot:
                    texture = self.loot_textures[self.labels[slot]['type']]
                    loot = LootSprite(texture, pickable=False)
                    loot.set_hit_box(self.settings['LOOT_HIT_BOX'])

                    loot.center_x = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * posx
                    loot.center_y = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * posy
                    loot.pos = (posx % 16, posy % 16)
                    loot.type = self.labels[slot]['type']
                    loot.chunk = tuple(chunk.p)
                    self.scene.add_sprite("Items", loot)
                    chunk.loot[(posx % 16, posy % 16)] = {'type': self.labels[slot]['type'], 'pickable': False, 'sprite': loot}
                    
                    
                    self.score[slot] -= 1
                    if self.score[slot] == 0:
                        del self.score[slot]
                        self.labels[slot]['sprite'].remove_from_sprite_lists()
                        del self.labels[slot]
                        for i in range(len(self.labels)):
                            self.labels[i]['sprite'].center_x = 20
                            self.labels[i]['sprite'].center_y = 40 * i + 20
                            self.labels[i]['label'].x = 32
                            self.labels[i]['label'].y = 40 * i + 4
                    else:
                        self.labels[slot]['label'].text = str(self.score[slot])

                elif chunk.loot[(posx % 16, posy % 16)]['type'] == self.labels[slot]['type']:
                    chunk.loot[(posx % 16, posy % 16)]['sprite'].amount += 1
                    self.score[slot] -= 1
                    if self.score[slot] == 0:
                        del self.score[slot]
                        self.labels[slot]['sprite'].remove_from_sprite_lists()
                        del self.labels[slot]
                        for i in range(len(self.labels)):
                            self.labels[i]['sprite'].center_x = 20
                            self.labels[i]['sprite'].center_y = 40 * i + 20
                            self.labels[i]['label'].x = 32
                            self.labels[i]['label'].y = 40 * i + 4
                    else: self.labels[slot]['label'].text = str(self.score[slot])

    def pickup(self, scene_name = 'Loot'):
        loot_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene[scene_name]
        )
        for loot in loot_hit_list:
            if loot.is_active:
                cords = tuple(loot.pos[i] + val * 16 for i, val in enumerate(loot.chunk))
                del self.active_loot[cords]
                if len(self.active_loot) > 1: self.check_crafts()
            self.scene[scene_name].remove(loot)
            loot.remove_from_sprite_lists()
            del self.map.get(loot.chunk).loot[loot.pos]
            for i, item in enumerate(self.labels):
                if item['type'] == loot.type:
                    self.score[i] += loot.amount
                    item['label'].text = str(self.score[i])
                    del loot
                    break
            else:
                loot.center_x = 20
                loot.center_y = len(self.score) * 40 + 20
                loot.pos = None
                loot.chunk = None
                loot.pickable = False
                loot.scale = LootSprite.settings['LOOT_SCALING']
                self.interface.add_sprite("Icons",loot)
                self.score += [loot.amount]
                self.labels += [{'type': loot.type, 'label': arcade.Text(str(loot.amount), 32, (len(self.score) - 1) * 40 + 4, font_size=10), 'sprite': loot}]

    def on_draw(self):

        self.clear()

        self.camera.use()

        self.scene.draw()

        self.gui_camera.use()

        self.interface.draw()
        for item in self.labels: 
            if item['label']:
                item['label'].draw()

        if self.debug_show:
            tile_size = self.settings['TILE_SIZE']
            info = [
                # f'x, y: {self.player_sprite.position[0], self.player_sprite.position[1]}',
                f'X, Y: {int(self.player_sprite.position[0] // tile_size), int(self.player_sprite.position[1] // tile_size)}',
                f'Chunk x, y: {self.player_sprite.chunk}',
                'Walls: ' + str(len(self.scene['Walls'])),
                'Standing on:' + str(self.map.getCell(*[int(i/self.settings['TILE_SIZE']) for i in self.player_sprite.position]))
            ]
            line_height = 25
            start_x = 5
            start_y = self.settings['SCREEN_HEIGHT'] - line_height
            for line in info:
                arcade.draw_text(line,
                                start_x,
                                start_y,
                                arcade.color.WHITE,
                                20,
                                width=self.settings['SCREEN_WIDTH'])
                start_y -= line_height