import arcade
from random import randint

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Simple roguelike graphics"

CHARACTER_SCALING = 0.5
TILE_SCALING = 0.5

PLAYER_MOVEMENT_SPEED = 5

class Roguelike(arcade.Window):

    def __init__(self):

        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        arcade.set_background_color(arcade.csscolor.DARK_GRAY)

        self.scene = None

        self.player_sprite = None

        self.camera = None

    def setup(self):

        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Walls", use_spatial_hash=True)

        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png", CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 120
        self.scene.add_sprite("Player", self.player_sprite)

        field = [[randint(0,1) if i != 0 and i != 15 and j != 0 and j != 15 else 1 for i in range(16)] for j in range(16)]
        field[1][1] = 0

        for i, line in enumerate(field):
            for j, cell in enumerate(line):
                if cell == 1:
                    wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
                    wall.center_x = 32 + j * 64
                    wall.center_y = 32 + i * 64
                    self.scene.add_sprite("Walls", wall)

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

        self.camera = arcade.Camera(self.width, self.height)
    
    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
    
    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.player_sprite.change_y = 0
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player_sprite.change_x = 0
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def center_camera_to_player(self):
        screen_center_x = self.player_sprite.center_x - self.camera.viewport_width / 2
        screen_center_y = self.player_sprite.center_y - self.camera.viewport_height / 2

        self.camera.move_to((screen_center_x, screen_center_y))

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.center_camera_to_player()


    def on_draw(self):

        self.clear()

        self.camera.use()

        self.scene.draw()



window = Roguelike()
window.setup()
arcade.run()