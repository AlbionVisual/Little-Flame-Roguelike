import arcade
from random import randint
from field_gen import Map
from time import time

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Simple roguelike graphics"

CHARACTER_SCALING = 1 / 16
TILE_SCALING = 2
TILE_SIZE = 32

PLAYER_MOVEMENT_SPEED = 3
PLAYER_ANIM_FRAMES = 33
RIGHT_FACING = 0
LEFT_FACING = 1

def load_texture_pair(filename):
    flipped_img = arcade.load_texture(filename, flipped_horizontally=True)
    img = arcade.load_texture(filename)
    return [img, flipped_img]

class PlayerCharacter(arcade.Sprite):

    def __init__(self):
        super().__init__()
        self.character_face_direction = RIGHT_FACING
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING
        self.walk_textures = [
            load_texture_pair("Textures/flame/flame_{0:02d}.png".format(i)) for i in range(PLAYER_ANIM_FRAMES)
        ]
        self.texture = self.walk_textures[0][self.character_face_direction]
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
        self.cur_texture += 1
        if self.cur_texture >= PLAYER_ANIM_FRAMES:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class Roguelike(arcade.Window):

    def __init__(self):

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.scene = None
        self.player_sprite = None
        self.camera = None
        self.physics_engine = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

    def setup(self):

        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
    
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = TILE_SIZE * 7 + TILE_SIZE // 2
        self.player_sprite.center_y = TILE_SIZE * 7 + TILE_SIZE // 2
        self.scene.add_sprite("Player", self.player_sprite)

        self.map = Map(7687906)
        chunk_x, chunk_y = self.player_sprite.center_x // (16 * 64), self.player_sprite.center_y // (16 * 64)
        self.map.genArea((chunk_x, chunk_y))
        self.map.genArea((chunk_x - 1, chunk_y))
        self.map.genArea((chunk_x + 1, chunk_y))
        self.map.genArea((chunk_x, chunk_y - 1))
        self.map.genArea((chunk_x, chunk_y + 1))

        for x in range(chunk_x - 1, chunk_x + 2):
            for y in range(chunk_y - 1, chunk_y + 2):
                print(self.map.get((x, y)), self.map.get((x, y)).paths)
                chunk = self.map.get((x, y))
                for i, line in enumerate(chunk.field):
                    for j, cell in enumerate(line):
                        if cell == 2:
                            chunk.field[i][j] = arcade.Sprite("Textures/concrete_gray.png", TILE_SCALING)
                            chunk.field[i][j].center_x = TILE_SIZE // 2 + j * TILE_SIZE + TILE_SIZE * 16 * x
                            chunk.field[i][j].center_y = TILE_SIZE // 2 + i * TILE_SIZE + TILE_SIZE * 16 * y
                            self.scene.add_sprite("Walls", chunk.field[i][j])

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

        self.camera = arcade.Camera(self.width, self.height)
    
    def process_keychange(self):
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
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

    def player_chunk_coords(self):
        return self.player_sprite.center_x

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.center_camera_to_player()

        self.scene.update_animation(
            delta_time, ["Player", "Walls"]
        )

    def on_draw(self):

        self.clear()

        self.camera.use()

        self.scene.draw()



# window = Roguelike()
# window.setup()
# arcade.run()