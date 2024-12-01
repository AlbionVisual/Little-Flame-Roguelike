import arcade

default_settings = {
    'SCREEN_WIDTH': 1000,
    'SCREEN_HEIGHT': 650,
    'SCREEN_TITLE': "Roguelike graphics",
    'CHARACTER_SCALING': 1 / 16,
    'ENEMY_SCALING': 1,
    'TILE_SCALING': 2,
    'LOOT_SCALING': 2,
    'TILE_SIZE': 32,
    'RIGHT_FACING': 0,
    'LEFT_FACING': 1,
    'PLAYER_MOVEMENT_SPEED': 3,
    'PLAYER_ANIM_FRAMES': 33,
    'ENEMY_ANIM_FRAMES': 8,
    'TILE_HIT_BOX': ((-8.0, -8.0), (8.0, -8.0), (8.0, 8.0), (-8.0, 8.0)),
    'LOOT_HIT_BOX': ((-8.0, -8.0), (8.0, -8.0), (8.0, 8.0), (-8.0, 8.0)),
    'MOUSE_HIT_BOX': ((-2.0, 2.0), (1.0, 2.0), (1.0, -1.0), (-2.0, -1.0)),
    'LOOT_SPAWN_ATTEMPTS': 5,
    'LOOT_SPAWN_CHANCE': 60,
    'LOOT_TYPES_AMOUNT': 10,
    'ANIM_MOVEMENT_RANGE': 5,
    'PICKABLES_RESCALING': 0.8,
    'DISPLAY_RANGE': 2,
    'TILE_TYPES': {
        "floor": {
            "texture": "Textures/concrete_gray_darken.png",
            "lighten_texture": "Textures/hardened_clay_stained_yellow_darken.png",
            "solidity": 0
        },
        "wall": {
            "texture": "Textures/concrete_gray.png",
            "lighten_texture": "Textures/concrete_yellow.png",
            "solidity": 1
        }
    },
}

def load_texture_pair(filename):
    flipped_img = arcade.load_texture(filename, flipped_horizontally=True)
    img = arcade.load_texture(filename)
    return [img, flipped_img]

class EnemyCharacter(arcade.Sprite):
    settings = { # This data works if sth's wrong!
        'RIGHT_FACING': 0,
        'LEFT_FACING': 1,
        'CHARACTER_SCALING': 1,
        'PLAYER_ANIM_FRAMES': 10,
        'TILE_SIZE': 128
    }
    
    def __init__(self):
        super().__init__()
        self.character_face_direction = EnemyCharacter.settings['RIGHT_FACING']
        self.cur_texture = 0
        self.scale = EnemyCharacter.settings['ENEMY_SCALING']
        self.chunk = (0, 0)
        self.walk_textures = [
            load_texture_pair("Textures/swoop/swoop-{0:02d}.png".format(i)) for i in range(EnemyCharacter.settings['ENEMY_ANIM_FRAMES'])
        ]
        self.texture = self.walk_textures[0][self.character_face_direction]
        self.hit_box = self.texture.hit_box_points
        self.visible = False
        self.alpha = 0

    def get_chunk(self):
        return (int(self.center_x // (16 * EnemyCharacter.settings['TILE_SIZE'])), int(self.center_y // (16 * EnemyCharacter.settings['TILE_SIZE'])))

    def update_animation(self, delta_time: float = 1 / 60):
        
        if self.change_x < 0 and self.character_face_direction == EnemyCharacter.settings['RIGHT_FACING']:
            self.character_face_direction = EnemyCharacter.settings['LEFT_FACING']
        elif self.change_x > 0 and self.character_face_direction == EnemyCharacter.settings['LEFT_FACING']:
            self.character_face_direction = EnemyCharacter.settings['RIGHT_FACING']
        self.cur_texture += 0.5
        if self.cur_texture >= EnemyCharacter.settings['ENEMY_ANIM_FRAMES']:
            self.cur_texture = 0
        self.texture = self.walk_textures[int(self.cur_texture)][self.character_face_direction]

        self.alpha = 255 if self.visible else 0

class PlayerCharacter(arcade.Sprite):
    settings = { # This data works if sth's wrong!
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
    def __init__(self, tile = 'invisible'):
        super().__init__(scale = TileSprite.settings['TILE_SCALING'])
        self.is_lighten = False
        self.is_visible = False
        if not isinstance(tile, str) or tile[:3] != 'inv':
            self.is_visible = True
            self.set_tile(tile)
    
    def change_texture(self, light = 0):
        self.is_lighten = bool(light)
        self.texture = self.tile['lighten_texture'] if light else self.tile['texture']

    def set_tile(self, new_tile):
        self.is_visible = True
        self.tile = new_tile

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
    
    def is_in_inventory(self): return not bool(self.chunk)
    
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
