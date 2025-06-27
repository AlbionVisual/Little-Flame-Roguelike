import arcade
from .game_map_generator import GameMapGenerator

class GameMouseBind(GameMapGenerator):
    def on_mouse_press(self, x, y, button, mods):
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.mouse_clicked = True
            icons_collision = arcade.check_for_collision_with_list(self.mouse_sprite, self.interface['Icons'])
            if icons_collision:
                self.taken_item_sprite = icons_collision[0]
            else:
                self.mouse_sprite.center_x += self.player_sprite.center_x - self.camera.viewport_width / 2
                self.mouse_sprite.center_y += self.player_sprite.center_y - self.camera.viewport_height / 2
                posx, posy = (int(i // self.settings['TILE_SIZE']) for i in self.mouse_sprite.position)
                chunk = self.map.get((posx // 16, posy // 16))
                cell = chunk.field[posy % 16][posx % 16]
                if len(cell) > 1 and cell[1].is_lighten:
                    loot_collision = arcade.check_for_collision_with_list(self.mouse_sprite, self.actor_scene['Loot'])
                    items_collisions = arcade.check_for_collision_with_list(self.mouse_sprite, self.actor_scene['Items'])
                    if loot_collision: self.taken_item_sprite = loot_collision[0]
                    elif items_collisions: self.taken_item_sprite = items_collisions[0]
                self.mouse_sprite.center_x -= self.player_sprite.center_x - self.camera.viewport_width / 2
                self.mouse_sprite.center_y -= self.player_sprite.center_y - self.camera.viewport_height / 2
            
            if self.taken_item_sprite:
                self.taken_item_sprite.alpha = 120
                self.dragging_item_sprite.center_x = x
                self.dragging_item_sprite.center_y = y
                self.dragging_item_sprite.change_texture(self.taken_item_sprite.texture)

    def on_mouse_release(self, x, y, button, mods):

        if button == arcade.MOUSE_BUTTON_LEFT and self.mouse_clicked and self.taken_item_sprite:
            self.mouse_clicked = False
            
            self.mouse_sprite.center_x += self.player_sprite.center_x - self.camera.viewport_width / 2
            self.mouse_sprite.center_y += self.player_sprite.center_y - self.camera.viewport_height / 2
            posx, posy = (int(i // self.settings['TILE_SIZE']) for i in self.mouse_sprite.position)
            self.mouse_sprite.center_x -= self.player_sprite.center_x - self.camera.viewport_width / 2
            self.mouse_sprite.center_y -= self.player_sprite.center_y - self.camera.viewport_height / 2
            chunk = self.map.get((posx // 16, posy // 16))
            cell = chunk.field[posy % 16][posx % 16]

            if len(cell) > 1 and self.mouse_sprite.center_x > 40:
                if cell[1].is_lighten:
                    if self.taken_item_sprite in self.interface['Icons']:
                        before = self.selector_sprite.slot
                        for i, icon in enumerate(self.labels):
                            if icon['sprite'].texture == self.taken_item_sprite.texture:
                                self.selector_sprite.slot = i
                                break
                        self.drop(all = True, coords = (posx * self.settings['TILE_SIZE'], posy * self.settings['TILE_SIZE']))
                        self.selector_sprite.slot = before
                    elif self.taken_item_sprite in self.actor_scene['Loot'] or self.taken_item_sprite in self.actor_scene['Items']:
                        coords = (posx * self.settings['TILE_SIZE'], posy * self.settings['TILE_SIZE'])
                        pos_x, pos_y = (int(i // self.settings['TILE_SIZE']) for i in coords)
                        chunk = self.map.get((pos_x // 16, pos_y // 16))
                        if (pos_x % 16, pos_y % 16) not in chunk.loot:
                            if self.taken_item_sprite.is_active:
                                cords = tuple(self.taken_item_sprite.pos[i] + val * 16 for i, val in enumerate(self.taken_item_sprite.chunk))
                                del self.active_loot[cords]
                                if len(self.active_loot) > 1: self.check_crafts()
                                self.taken_item_sprite.is_active = False
                            self.taken_item_sprite.center_x = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * pos_x
                            self.taken_item_sprite.center_y = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * pos_y
                            del self.map.get(self.taken_item_sprite.chunk).loot[self.taken_item_sprite.pos]
                            self.taken_item_sprite.pos = (pos_x % 16, pos_y % 16)
                            self.taken_item_sprite.chunk = tuple(chunk.pos)
                            self.taken_item_sprite.pickable = False
                            self.taken_item_sprite.remove_from_sprite_lists()
                            self.actor_scene.add_sprite("Items", self.taken_item_sprite)
                            chunk.loot[(posx % 16, posy % 16)] = {'type': self.taken_item_sprite.type, 'pickable': False, 'sprite': self.taken_item_sprite}
                        elif chunk.loot[(posx % 16, posy % 16)]['type'] == self.taken_item_sprite.type:
                            chunk.loot[(posx % 16, posy % 16)]['sprite'].amount += self.taken_item_sprite.amount
            else:
                self.pickup(scene=False, sprites=[self.taken_item_sprite])

            self.taken_item_sprite.alpha = 255
            self.taken_item_sprite = None
            self.dragging_item_sprite.texture = arcade.Texture.create_empty("blank", (self.settings['TILE_SIZE'], ) * 2)
    
    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_sprite.center_x = x
        self.mouse_sprite.center_y = y
        if self.mouse_clicked and self.taken_item_sprite:
            self.dragging_item_sprite.center_x = x
            self.dragging_item_sprite.center_y = y
