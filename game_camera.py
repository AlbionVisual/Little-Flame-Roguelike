import arcade
from game_setup import GameSetup

class GameCamera(GameSetup):

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.camera.viewport = self.window.rect
        self.camera.projection = arcade.LRBT(-self.width/2, self.width/2, -self.height/2, self.height/2)
        self.gui_camera.viewport = self.window.rect
        self.gui_camera.projection = arcade.LRBT(-self.width/2, self.width/2, -self.height/2, self.height/2)
        self.gui_camera.position = (self.window.center_x, self.window.center_y)
        self.timer_text.x = self.width - 10
        self.timer_text.y = self.height - 10

    def center_camera_to_player(self):
        # Move the camera to center on the player
        self.camera.position = arcade.math.smerp_2d(
            self.camera.position,
            self.player_sprite.position,
            self.window.delta_time,
            0.3,
        )

        # Constrain the camera's position to the camera bounds.
        
        # self.camera_bounds = arcade.LRBT(
        #     self.window.width/2.0,
        #     tile_map.width * GRID_PIXEL_SIZE - self.window.width/2.0,
        #     self.window.height/2.0,
        #     tile_map.height * GRID_PIXEL_SIZE
        # )
        # self.camera_sprites.view_data.position = arcade.camera.grips.constrain_xy(
        #     self.camera_sprites.view_data, self.camera_bounds
        # )
        
    def center_camera_to_player_old(self):
        # screen_center_x = self.player_sprite.center_x - self.camera.viewport_width / 2
        # screen_center_y = self.player_sprite.center_y - self.camera.viewport_height / 2

        self.camera.position = self.player_sprite.position
