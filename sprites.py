import arcade
from PIL import Image
import math

def make_transparent_texture(width, height):
    """Создает прозрачную текстуру."""
    image = Image.new("RGBA", (int(width), int(height)), (0, 0, 0, 0))
    return arcade.Texture(image)

def rotate_vector(vec, angle):
    angle = math.radians(angle)
    
    new_x = vec[0] * math.cos(angle) - vec[1] * math.sin(angle)
    new_y = vec[0] * math.sin(angle) + vec[1] * math.cos(angle)
    
    return (new_x, new_y)

def normalize_vec(vec, scale = 1):
    vec_len = (vec[0]**2 + vec[1]**2)**(1/2)
    new_x = (vec[0] / vec_len) * scale
    new_y = (vec[1] / vec_len) * scale
    return (new_x, new_y)

default_settings = {
    'SCREEN_WIDTH': 1000,
    'SCREEN_HEIGHT': 650,
    'SCREEN_TITLE': "Roguelike graphics",
    'MIN_SCREEN_WIDTH': 150,
    'MIN_SCREEN_HEIGHT': 100,

    'CHARACTER_SCALING': 1 / 16,
    'PLAYER_MOVEMENT_SPEED': 3,
    "HEALTH_BOOST": 0.05,
    "HEALTH_LOSS_COFF": 0.5,
    'PLAYER_ANIM_FRAMES': 32,
    "MAX_LIGHT_STRENGTH":6,
    "MIN_LIGHT_STRENGTH":1,
    "PLAYER_ATACK_RANGE":2,

    'ARC_SCALING': 1.4,
    'ARC_DISTANCE_COFF': 20,
    'ARC_ANIM_FRAMES': 7,
    'ARC_ANIM_SPEED': 0.4,

    'ENEMY_SCALING': 1 / 16,
    'ENEMY_HIT_BOX': [(-16.0, -16.0), (16.0, -16.0), (16.0, 16.0), (-16.0, 16.0)],
    'ENEMY_ANIM_FRAMES': 31,
    'ENEMIES_SPAWN_ATTEMPTS': 1,
    'ENEMIES_SPAWN_CHANCE': 100,
    "ENEMY_HEAT_POINTS": 0.2,

    'TILE_SCALING': 2,
    'TILE_SIZE': 32,
    'TILE_HIT_BOX': [(-8.0, -8.0), (8.0, -8.0), (8.0, 8.0), (-8.0, 8.0)],
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

    'LOOT_SCALING': 2,
    'LOOT_HIT_BOX': [(-8.0, -8.0), (8.0, -8.0), (8.0, 8.0), (-8.0, 8.0)],
    'LOOT_SPAWN_ATTEMPTS': 5,
    'LOOT_SPAWN_CHANCE': 60,
    'LOOT_TYPES_AMOUNT': 9,
    
    'MOUSE_HIT_BOX_SIZE': (3.0, 3.0),

    'RIGHT_FACING': 1,
    'LEFT_FACING': 0,
    
    'DISPLAY_RANGE': 2,
    "ALGORITHM_NAME": "MapPaths",
    "BORDERS": {
        "LEFT": 1,
        "RIGHT": 1,
        "UP": 1,
        "DOWN": 1
    },
    'GAME_TYPE': 'INFINITE',
    'CAMERA_ALGORYTHM': 'OLD',
    'AMOUNT_OF_LAYERS':7,
    'WALL_SPAWN_CHANCE':0.3,
    'MIN_WEIGHTS_COFF':0.2,

    'ANIM_MOVEMENT_RANGE': 5,
    'PICKABLES_RESCALING': 0.8,
}

def load_texture_pair(filename):
    img = arcade.load_texture(filename)
    flipped_img = img.flip_left_right()
    return [img, flipped_img]

class EnemyCharacter(arcade.Sprite):
    settings = {
        'RIGHT_FACING': 0,
        'LEFT_FACING': 1,
        'CHARACTER_SCALING': 1,
        'ENEMY_ANIM_FRAMES': 10,
        'ENEMY_SCALING': 1,
        'ENEMY_HIT_BOX': [(-16.0, -16.0), (16.0, -16.0), (16.0, 16.0), (-16.0, 16.0)],
    }
    walk_textures = []
    
    def __init__(self):
        super().__init__()
        self.character_face_direction = EnemyCharacter.settings['RIGHT_FACING']
        self.scale = EnemyCharacter.settings['ENEMY_SCALING']
        self.chunk = (0, 0)
        self.shape = EnemyCharacter.settings['ENEMY_HIT_BOX']
        size = -TileSprite.settings["ENEMY_HIT_BOX"][0][0] +TileSprite.settings["ENEMY_HIT_BOX"][1][0]
        
        self.transparent_texture = make_transparent_texture(size,size)
        self.texture = self.transparent_texture
        self.cur_texture = 0
        self.texture = EnemyCharacter.walk_textures[self.cur_texture][self.character_face_direction]

        self.visible = False
        self.alpha = 0
        self.striking = True

        self.change_x = 0.7
        self.change_y = 0.3

    def get_chunk(self):
        return (int(self.center_x // (16 * EnemyCharacter.settings['TILE_SIZE'])), int(self.center_y // (16 * EnemyCharacter.settings['TILE_SIZE'])))

    def killed(self):
        self.remove_from_sprite_lists()
    
    def update(self, delta_time = 1 / 60, *args, **kwargs):
        return super().update(delta_time, *args, **kwargs)

    def update_animation(self, delta_time: float = 1 / 60):
        
        if self.change_x < 0 and self.character_face_direction == EnemyCharacter.settings['RIGHT_FACING']:
            self.character_face_direction = EnemyCharacter.settings['LEFT_FACING']
        elif self.change_x > 0 and self.character_face_direction == EnemyCharacter.settings['LEFT_FACING']:
            self.character_face_direction = EnemyCharacter.settings['RIGHT_FACING']
        self.cur_texture += 0.5
        if self.cur_texture >= EnemyCharacter.settings['ENEMY_ANIM_FRAMES']:
            self.cur_texture = 0
        try:
            self.texture = EnemyCharacter.walk_textures[int(self.cur_texture)][self.character_face_direction]
        except:
            self.texture = self.transparent_texture
        
        self.alpha = 255 if self.visible else 0

class AtackArc(arcade.Sprite):
    swoop_textures = []

    def __init__(self, vec = (0, 1), scale = 1, pos = (0, 0)):
        scale *= AtackArc.settings["ARC_SCALING"]
        super().__init__(scale=scale)
        # top_vec = (0, 1)
        # self.hit_box = arcade.hitbox.HitBox([(0, 0), rotate_vector(top_vec, -60), rotate_vector(top_vec, -30),top_vec, rotate_vector(top_vec, +30),rotate_vector(top_vec, +60)])
        norm_vec = normalize_vec(vec, scale * AtackArc.settings['ARC_DISTANCE_COFF'])
        self.position = [pos[0] + norm_vec[0], pos[1] + norm_vec[1]]
        self.angle = -math.atan2(vec[1], vec[0]) * 180 / math.pi + 90
        self.transparent_texture = make_transparent_texture(AtackArc.swoop_textures[0].width,AtackArc.swoop_textures[0].height)
        self.texture = self.transparent_texture

        self.cur_texture = 0
        self.texture = AtackArc.swoop_textures[self.cur_texture]

    def update_animation(self, delta_time: float = 1 / 60):
        self.cur_texture += AtackArc.settings['ARC_ANIM_SPEED']
        if self.cur_texture >= AtackArc.settings['ARC_ANIM_FRAMES'] :
            # self.cur_texture = 0
            self.remove_from_sprite_lists()
        try:
            self.texture = AtackArc.swoop_textures[int(self.cur_texture)]
        except:
            self.texture = self.transparent_texture
        
        self.alpha = 255 if self.visible else 0

class PlayerCharacter(arcade.Sprite):
    settings = { # This data works if sth's wrong!
        'RIGHT_FACING': 0,
        'LEFT_FACING': 1,
        'CHARACTER_SCALING': 1,
        'PLAYER_ANIM_FRAMES': 10,
        'TILE_SIZE': 128
    }
    
    def __init__(self, textures = None):
        super().__init__()
        self.character_face_direction = PlayerCharacter.settings['RIGHT_FACING']
        self.scale = PlayerCharacter.settings['CHARACTER_SCALING']
        self.chunk = (0, 0)
        self.cur_texture = 0
        self.walk_textures = textures
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]
        self.health = 1.0

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

    def atack(self, direction = (1, 0)):
        shoot_x = direction[0] - self.center_x
        shoot_y = direction[1] - self.center_x
        return AtackArc(pos = self.position, vec = (shoot_x, shoot_y), scale=PlayerCharacter.settings["PLAYER_ATACK_RANGE"])

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
        else:
            self.shape = TileSprite.settings["TILE_HIT_BOX"]
            size = -TileSprite.settings["TILE_HIT_BOX"][0][0] +TileSprite.settings["TILE_HIT_BOX"][1][0]
            self.texture = make_transparent_texture(size, size)
    
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

        if texture is not None:
            self.change_texture(texture)
            self.shape = LootSprite.settings["LOOT_HIT_BOX"]
        else:
            size = -TileSprite.settings["LOOT_HIT_BOX"][0][0] +TileSprite.settings["LOOT_HIT_BOX"][1][0]
            self.change_texture(make_transparent_texture(size, size))
            self.shape = LootSprite.settings["LOOT_HIT_BOX"]
            
        self.pickable = pickable
        if pickable:
            if self.scale.__class__ == tuple:
                self.scale = tuple(item * LootSprite.settings['PICKABLES_RESCALING'] for item in self.scale)
            else:
                self.scale *= LootSprite.settings['PICKABLES_RESCALING']
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
        self.shown = True

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
