import arcade
from PIL import ImageFilter
from .game_player_controller import GamePlayerController
from .game_camera import GameCamera
from .interfaces.puase_menu import PauseMenuView

class GameKeyboardBind(GamePlayerController, GameCamera):
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

    def on_key_press(self, key, mods):
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
        elif key == arcade.key.SPACE:
            self.atack()
        elif key == arcade.key.ESCAPE:
            blurred_image = arcade.get_image().filter(ImageFilter.GaussianBlur(radius=4))
            screenshot = arcade.Texture(blurred_image)
            menu_view = PauseMenuView(self, screenshot)
            self.window.show_view(menu_view)

        elif key == arcade.key.F4:
            self.map.debug_chunk(self.player_sprite.chunk)
        elif 49 <= key <= 57: # numbers
            self.selector_sprite.center_y = self.settings["TILE_SIZE"] // 2 + 4 + (self.settings["TILE_SIZE"] + 8) * (key - 49)
            self.selector_sprite.slot = key - 49
        elif key == arcade.key.F3:
            self.debug_show = not self.debug_show
        elif key == arcade.key.F11:
            self.window.set_fullscreen(not self.window.fullscreen)
            self.camera.viewport = self.window.rect
            self.camera.projection = arcade.LRBT(-self.width/2, self.width/2, -self.height/2, self.height/2)
            self.gui_camera.viewport = self.window.rect
            self.gui_camera.projection = arcade.LRBT(-self.width/2, self.width/2, -self.height/2, self.height/2)
        self.process_keychange()
    
    def on_key_release(self, key, mods):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right_pressed = False

        self.process_keychange()