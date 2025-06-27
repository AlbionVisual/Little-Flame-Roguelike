import arcade
from .game_keyboard_bind import GameKeyboardBind
from .game_mouse_bind import GameMouseBind
from PIL import ImageFilter
from .interfaces.gameover_view import GameOverView

class GameDrawer(GameKeyboardBind, GameMouseBind):
        
    def on_update(self, delta_time):

        self.physics_engine.update()
        self.process_keychange()

        # Updating camera and lights
        if self.settings['CAMERA_ALGORYTHM'] == 'OLD':
            self.center_camera_to_player_old()
        else: self.center_camera_to_player()

        if self.player_sprite.get_chunk() != self.player_sprite.chunk:
            self.gen_map()
            self.draw_map()


        arg = self.map.gen_light(
                (int(self.player_sprite.center_x // self.settings['TILE_SIZE']), int(self.player_sprite.center_y // self.settings['TILE_SIZE'])),
                self.player_sprite.health * (self.settings["MAX_LIGHT_STRENGTH"] - self.settings["MIN_LIGHT_STRENGTH"]) + self.settings["MIN_LIGHT_STRENGTH"]
        )
        if arg != self.lighten: self.change_lights(arg)


        # Updating things for Run gamemode
        if self.settings["GAME_TYPE"] == "RUN":
            self.player_sprite.health -= delta_time / self.settings["HEALTH_LOSS_COFF"]
            if self.player_sprite.health < 0:
                self.player_sprite.health = 0
                blurred_image = arcade.get_image().filter(ImageFilter.GaussianBlur(radius=4))
                screenshot = arcade.Texture(blurred_image)
                game_over_view = GameOverView(self, self.timer_text.text, screenshot)
                self.window.show_view(game_over_view)
            # Recalculating timer
            self.timer_value = self.timer_value + delta_time
            minutes = int(self.timer_value) // 60
            seconds = int(self.timer_value) % 60
            seconds_100s = int((self.timer_value - 60 * minutes - seconds) * 100)
            self.timer_text.text = f"{minutes:02d}:{seconds:02d}.{seconds_100s:02d}"
        
        # Check touchables
        self.pickup()
        if self.settings["GAME_TYPE"] == "RUN":
            self.enemy_collision()

        # Checking wether active loot still active (not in shadow)
        for cords, loot in list(self.active_loot.items()):
            if not self.map.get(loot.chunk).field[loot.pos[1]][loot.pos[0]][1].is_lighten:
                loot.is_active = False
                del self.active_loot[cords]

        # Add new active loot when player went through it
        footed_loot = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Items"] 
        )
        for loot in footed_loot:


            x, y = (loot.pos[i] + val * 16 for i, val in enumerate(loot.chunk))
            if (x, y) not in self.active_loot:
                loot.is_active = True
                self.active_loot[(x, y)] = loot
                if len(self.active_loot) > 1:
                    self.check_crafts()


        # Update sprites
        for enemy in self.scene["Enemies"]:
            enemy.center_x += enemy.change_x
            walls_hit = arcade.check_for_collision_with_list(enemy, self.scene["Walls"])
            for wall in walls_hit:
                if enemy.change_x > 0:
                    enemy.right = wall.left
                elif enemy.change_x < 0:
                    enemy.left = wall.right
            if len(walls_hit) > 0:
                enemy.change_x *= -1

            enemy.center_y += enemy.change_y
            walls_hit = arcade.check_for_collision_with_list(enemy, self.scene["Walls"])
            for wall in walls_hit:
                if enemy.change_y > 0:
                    enemy.top = wall.bottom
                elif enemy.change_y < 0:
                    enemy.bottom = wall.top
            if len(walls_hit) > 0:
                enemy.change_y *= -1
        
        self.scene["Enemies"].update(delta_time)

        self.scene.update_animation(
            delta_time, ["Player", "Loot", "Items", "Enemies", "Effects"]
        )

    def on_draw(self):

        self.clear()

        self.camera.use()
        # Draw map and sprites
        self.scene.draw()

        # self.scene.draw_hit_boxes(names=["Enemies","Player"]) # if you want to see hitboxes

        self.gui_camera.use()
        # Draw interface
        self.interface.draw()
        for item in self.labels: # labels for inventory
            if item['label']:
                item['label'].draw()

        # Draw player's health bar
        if self.settings["GAME_TYPE"] == "RUN":
            self.timer_text.draw()

            bar_width = 200
            bar_height = 30
            margin = 10
            bar_x = self.width - margin - bar_width
            bar_y = margin

            arcade.draw_rect_filled(arcade.rect.XYWH(bar_x, bar_y, bar_width, bar_height, arcade.Vec2(0,0)), arcade.color.GRAY)

            current_width = bar_width * (self.player_sprite.health if self.player_sprite.health < 1 and self.player_sprite.health >= 0 else 1)
            arcade.draw_rect_filled(arcade.rect.XYWH(bar_x, bar_y, current_width, bar_height, arcade.Vec2(0,0)), arcade.color.ORANGE_RED)
        
        # Draw debug info
        if self.debug_show:
            tile_size = self.settings['TILE_SIZE']
            info = [
                # f'x, y: {self.player_sprite.position[0], self.player_sprite.position[1]}',
                f'X, Y: {int(self.player_sprite.position[0] // tile_size), int(self.player_sprite.position[1] // tile_size)}',
                'In chunk x, y: ' + str(int(self.player_sprite.position[0] // tile_size) % 16) + ' ' + str(int(self.player_sprite.position[1] // tile_size) % 16),
                f'Chunk x, y: {self.player_sprite.chunk}',
                'Walls: ' + str(len(self.scene['Walls'])),
                'Floors: ' + str(len(self.scene['Floor']))
                # 'Standing on: ' + str(self.map.getCell(*[int(i/self.settings['TILE_SIZE']) for i in self.player_sprite.position]))
            ]
            line_height = 25
            start_x = 5
            start_y = self.height - line_height
            for line in info:
                arcade.draw_text(line,
                                start_x,
                                start_y,
                                arcade.color.WHITE,
                                20,
                                width=self.width)
                start_y -= line_height