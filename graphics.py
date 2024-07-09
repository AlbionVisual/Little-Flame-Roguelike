import arcade
from field_gen_paths import MapPaths

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
    'LOOT_SPAWN_CHANCE': 20,
    'LOOT_TYPES_AMOUNT': 10,
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
        'LOOT_SCALING': 1
    }
    def __init__(self, texture = None):
        super().__init__(scale = LootSprite.settings['LOOT_SCALING'])
        if texture is not None: self.change_texture(texture)
        self.pos = None
        self.chunk = None
        self.type = None
    
    def change_texture(self, texture):
        self.texture = texture

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
        self.jump_needs_reset = False
        self.gui_camera = None
        self.score = None

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
            arcade.load_texture('Textures/apple.png'),
            arcade.load_texture('Textures/compass.png'),
            arcade.load_texture('Textures/chainmail_helmet.png'),
            arcade.load_texture('Textures/feather.png'),
            arcade.load_texture('Textures/fish.png'),
            arcade.load_texture('Textures/stone_sword.png'),
            arcade.load_texture('Textures/wood_axe.png'),
            arcade.load_texture('Textures/stick.png')
        ]

        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Loot", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
    
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

        self.camera = arcade.Camera(self.width, self.height)
        self.gui_camera = arcade.Camera(self.width, self.height)
        self.score = 0
    
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
            if self.map.get(loot.chunk).field[loot.pos[0]][loot.pos[1]][0] == 5:
                loot.change_texture(self.loot_textures[loot.type])


        self.lighten = new_lights

    def draw_map(self, chunk_x = None, chunk_y = None):
        if chunk_x == None: chunk_x = self.player_sprite.chunk[0]
        if chunk_y == None: chunk_y = self.player_sprite.chunk[1]
        self.scene["Loot"].clear()
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
                    if chunk.field[yi][xi][0] in (1, 5): loot = LootSprite(self.loot_textures[data])
                    else: loot = LootSprite()
                    loot.set_hit_box(self.settings['LOOT_HIT_BOX'])
                    loot.center_x = self.settings['TILE_SIZE'] * 16 * x + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * xi
                    loot.center_y = self.settings['TILE_SIZE'] * 16 * y + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * yi
                    loot.pos = (xi, yi)
                    loot.type = data
                    loot.chunk = (x, y)
                    self.scene.add_sprite("Loot", loot)

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

        loot_hit_list = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Loot"]
        )
        for loot in loot_hit_list:
            self.scene["Loot"].remove(loot)
            loot.remove_from_sprite_lists()
            del self.map.get(loot.chunk).loot[loot.pos]
            del loot
            self.score += 1

        self.scene.update_animation(
            delta_time, ["Player"]
        )

    def on_draw(self):

        self.clear()

        self.camera.use()

        self.scene.draw()

        self.gui_camera.use()

        arcade.draw_text(
            f'Logs burn: {self.score}',
            10, 10,
            arcade.csscolor.WHITE,
            18
        )