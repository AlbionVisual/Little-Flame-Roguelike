import arcade
from map import *
from sprites import *
from field_gen_paths import MapPaths
from puase_menu import PauseMenuView
from game_over_view import GameOverView
from PIL import ImageFilter


class RoguelikeView(arcade.View):
    def __init__(self, **new_settings):
        self.settings = default_settings
        for option in new_settings:
            self.settings[option] = new_settings[option]
        super().__init__()
        # super().__init__(self.settings['SCREEN_WIDTH'], self.settings['SCREEN_HEIGHT'], self.settings['SCREEN_TITLE'])
        arcade.set_background_color(arcade.csscolor.BLACK)
        self.scene = None
        self.player_sprite = None
        self.mouse_sprite = None
        self.dragging_item_sprite = None
        self.taken_item_sprite = None
        self.camera = None
        self.physics_engine = None
        self.lighten = None
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.mouse_clicked = False
        self.gui_camera = None
        self.score = None
        self.active_loot = None
        self.debug_show = False
        self.loot_textures = [
            arcade.load_texture('Textures/Loot/book.png'),
            arcade.load_texture('Textures/Loot/wood_axe.png'),
            arcade.load_texture('Textures/Loot/stick.png'),
            arcade.load_texture('Textures/Loot/log_oak.png'),
            arcade.load_texture('Textures/Loot/ladder.png'),
            arcade.load_texture('Textures/Loot/jungle_boat.png'),
            arcade.load_texture('Textures/Loot/birch_boat.png'),
            arcade.load_texture('Textures/Loot/door_birch.png'),
            arcade.load_texture('Textures/Loot/carrot.png'),
            arcade.load_texture('Textures/Loot/feather.png'),
            arcade.load_texture('Textures/Loot/apple.png'),
            arcade.load_texture('Textures/Loot/fish.png'),
            arcade.load_texture('Textures/Loot/jukebox_side.png'),
            arcade.load_texture('Textures/Loot/crafting_table_front.png'),
            arcade.load_texture('Textures/Loot/bookshelf.png'),
            arcade.load_texture('Textures/Loot/stone_sword.png'),
        ]
        self.interface_textures = {
            "selector": arcade.load_texture('Textures/frame.png')
        }
        self.player_textures = [
            load_texture_pair("Textures/flame/flame_{0:02d}.png".format(i)) for i in range(self.settings['PLAYER_ANIM_FRAMES'])
        ]
        self.enemies_textures = [
            load_texture_pair("Textures/soul/soul-{0:02d}.png".format(i)) for i in range(self.settings['ENEMY_ANIM_FRAMES'])
        ]
        self.atack_textures = [
            arcade.load_texture("Textures/swoop/swoop-{0:02d}.png".format(i)) for i in range(self.settings['ARC_ANIM_FRAMES'])
        ]
        self.tile_textures = self.settings['TILE_TYPES']
        for _, tile in self.tile_textures.items():
            tile['texture'] = arcade.load_texture(tile['texture'])
            tile['lighten_texture'] = arcade.load_texture(tile['lighten_texture'])

        self.scene = arcade.Scene()

        self.scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.scene.add_sprite_list("Loot", use_spatial_hash=True)
        self.scene.add_sprite_list("Items", use_spatial_hash=True)
        self.scene.add_sprite_list("Testables", use_spatial_hash=True)
        self.scene.add_sprite_list("Player")
        self.scene.add_sprite_list("Enemies")
        self.scene.add_sprite_list("Effects")

    def setup(self, seed = -1, **new_settings):

        for option in new_settings:
            self.settings[option] = new_settings[option]

        PlayerCharacter.settings = self.settings
        EnemyCharacter.settings = self.settings
        TileSprite.settings = self.settings
        LootSprite.settings = self.settings
        AtackArc.settings = self.settings

        EnemyCharacter.walk_textures = self.enemies_textures
        AtackArc.swoop_textures = self.atack_textures

        arcade.set_background_color(arcade.csscolor.BLACK)

        if self.settings["GAME_TYPE"] == "INFINITE":
            self.settings["BORDERS"] = {
                'LEFT': -1,
                'RIGHT': -1,
                'UP': -1,
                'DOWN': -1
            }
        elif self.settings["GAME_TYPE"] == "RUN":
            ...
   
        self.scene.get_sprite_list("Enemies").clear()
        self.scene.get_sprite_list("Loot").clear()
        self.scene.get_sprite_list("Items").clear()
        self.scene.get_sprite_list("Walls").clear()
        self.scene.get_sprite_list("Floor").clear()
        self.scene.get_sprite_list("Effects").clear()

        self.scene.get_sprite_list("Player").clear()
        self.player_sprite = PlayerCharacter(self.player_textures)
        self.player_sprite.center_x = self.settings['TILE_SIZE'] * 7 + self.settings['TILE_SIZE'] // 2
        self.player_sprite.center_y = self.settings['TILE_SIZE'] * 7 + self.settings['TILE_SIZE'] // 2
        self.scene.add_sprite("Player", self.player_sprite)


        self.mouse_sprite = arcade.SpriteSolidColor(
            width=self.settings['MOUSE_HIT_BOX_SIZE'][0],
            height=self.settings['MOUSE_HIT_BOX_SIZE'][1],
            color=(0, 0, 0, 0)
        )
        self.mouse_sprite.center_x = 0
        self.mouse_sprite.center_y = 0

        
        Algorithm_class = globals()[self.settings["ALGORITHM_NAME"]]
        Map.settings = self.settings
        self.map = Algorithm_class(seed)
        print('Seed: ', self.map.seed)

        self.gen_map()
        self.drawn_chunks = set()
        self.draw_map()
        self.lighten = (set(), set())
        self.change_lights(
            self.map.gen_light(
                (self.player_sprite.center_x // self.settings['TILE_SIZE'], self.player_sprite.center_y // self.settings['TILE_SIZE'])
            )
        )

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

        self.interface = arcade.Scene()
        self.interface.add_sprite_list("Icons", use_spatial_hash=True)
        self.interface.add_sprite_list("Indicators", use_spatial_hash=True)
        self.interface.add_sprite_list("Floatings")

        self.selector_sprite = arcade.Sprite(scale=1.25)
        self.selector_sprite.texture = self.interface_textures["selector"]
        self.selector_sprite.center_x = self.settings["TILE_SIZE"] // 2 + 4
        self.selector_sprite.center_y = self.settings["TILE_SIZE"] // 2 + 4
        self.selector_sprite.slot = 0
        self.interface.add_sprite("Indicators", self.selector_sprite)

        self.taken_item_sprite = None
        self.dragging_item_sprite = LootSprite(pickable=False)
        self.interface.add_sprite("Floatings", self.dragging_item_sprite)

        self.timer_value: float = 0.0
        self.timer_text = arcade.Text(
            text="00:00:00",
            x=self.settings["SCREEN_WIDTH"]-10,
            y=self.settings["SCREEN_HEIGHT"]-10,
            color=arcade.color.WHITE,
            font_size=12,
            anchor_x="right",
            anchor_y="top"
        )

        self.labels = []

        self.camera = arcade.Camera2D()
        self.gui_camera = arcade.Camera2D()

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
                    loot_collision = arcade.check_for_collision_with_list(self.mouse_sprite, self.scene['Loot'])
                    items_collisions = arcade.check_for_collision_with_list(self.mouse_sprite, self.scene['Items'])
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
                    elif self.taken_item_sprite in self.scene['Loot'] or self.taken_item_sprite in self.scene['Items']:
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
                            self.scene.add_sprite("Items", self.taken_item_sprite)
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

    def gen_map(self):
        chunk_x, chunk_y = self.player_sprite.get_chunk()
        self.map.genArea((chunk_x, chunk_y))

        self.player_sprite.chunk = self.player_sprite.get_chunk()
    
    def change_lights(self, new_lights):
        for i in range(2):
            for cell in self.lighten[i] - new_lights[i]:
                if not cell.is_visible: cell.set_tile( self.tile_textures[map_types_relation[i+1]] )
                cell.change_texture(light = False)
                self.map.chunks[(cell.center_x // self.settings['TILE_SIZE'] // 16, cell.center_y // self.settings['TILE_SIZE'] // 16)].field[cell.center_y // self.settings['TILE_SIZE'] % 16][cell.center_x // self.settings['TILE_SIZE'] % 16][0] -= 4
            for cell in new_lights[i] - self.lighten[i]:
                if not cell.is_visible: cell.set_tile( self.tile_textures[map_types_relation[i+1]] ) 
                cell.change_texture(light = True)
        
        for loot in self.scene["Loot"]:
            if map_types_relation[self.map.get(loot.chunk).field[loot.pos[1]][loot.pos[0]][0]] == 'lighten_floor':
                loot.change_texture(self.loot_textures[loot.type])
        
        for enemy in self.scene["Enemies"]:
            if map_types_relation[self.map.get(enemy.chunk).field[enemy.pos[1]][enemy.pos[0]][0]] == 'lighten_floor':
                enemy.visible = True


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
                'amount': 1,

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
            min_amount = 0
            min_coords = ()
            for i, line in enumerate(reversed(craft)):
                if field[x - 1][y + i]: return False
                if field[x + len(craft[0])][y + i]: return False
                for j, patt in enumerate(line):
                    if field[x + j][y - 1]: return False
                    if field[x + j][y + len(craft)]: return False
                    if patt == '*': 
                        if field[x + j][y + i]: return False
                    else:
                        if not field[x + j][y + i]: return False
                        if patt in sym_types and field[x + j][y + i][0] != sym_types[patt]: return False
                        else: 
                            if field[x + j][y + i][0] in sym_types.values() and patt not in sym_types: return False
                            else:
                                sym_types[patt] = field[x + j][y + i][0]
                                if not min_amount:
                                    min_amount = field[x + j][y + i][1]
                                    min_coords = (x + j, y + i)
                                elif min_amount > field[x + j][y + i][1]:
                                    min_amount = field[x+j][y+i][1]
                                    min_coords = (x + j, y + i)
            return min_coords, min_amount

        def bring_back(pattern):
            nonlocal min_y, min_x, max_x, max_y, start_y, start_x
            for i in range(min_x, max_x - len(pattern[0]) + 1):
                for j in range(min_y, max_y - len(pattern) + 1):
                    res = check_for_colision(pattern, i - start_x, j - start_y)
                    if res: return (i, j, res[0][0] + start_x, res[0][1] + start_y, res[1])
            return False

        for coord, loot in self.active_loot.items():
            if coord[0] > max_x: max_x = coord[0]
            if coord[0] < min_x: min_x = coord[0]
            if coord[1] > max_y: max_y = coord[1]
            if coord[1] < min_y: min_y = coord[1]
            field[coord[0] - start_x][coord[1] - start_y] = [loot.type, loot.amount]
        
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
                            if loot.amount <= res[4]:
                                del self.active_loot[cords]
                                loot.remove_from_sprite_lists()
                                del self.map.get(loot.chunk).loot[loot.pos]
                            else: loot.amount -= res[4]
                
                amount = res[4]
                res = (res[2], res[3])
                x, y = (i // 16 for i in res)
                xi, yi = (i % 16 for i in res)
                chunk = self.map.get((x, y))
                loot = LootSprite(self.loot_textures[temp['res']], pickable=True)
                # loot.set_hit_box(self.settings['LOOT_HIT_BOX'])
                loot.center_x = self.settings['TILE_SIZE'] * 16 * x + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * xi
                loot.center_y = self.settings['TILE_SIZE'] * 16 * y + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * yi
                loot.pos = (xi, yi)
                loot.type = temp['res']
                loot.amount = temp['amount'] * amount
                loot.chunk = (x, y)
                chunk.loot[(xi, yi)] = {'type': temp['res'], 'sprite': loot}
                self.scene.add_sprite("Loot", loot)

                return
        
    def draw_map(self, chunk_x = None, chunk_y = None):

        # self.scene.get_sprite_list("Enemies").clear()
        self.scene.get_sprite_list("Loot").clear()
        self.scene.get_sprite_list("Items").clear()

        # Count player's chunk as center one 
        if chunk_x == None: chunk_x = self.player_sprite.chunk[0]
        if chunk_y == None: chunk_y = self.player_sprite.chunk[1]

        # For every chunk placed in distance not greater than R from center
        R = self.settings['DISPLAY_RANGE']
        drawn_chunks = set()
        for x in range(int(chunk_x - R), int(chunk_x + R + 1)):
            for y in range(int(chunk_y - R), int(chunk_y + R + 1)):
                chunk = self.map.get((x, y))

                # for every loot in chunk
                for coord, data in chunk.loot.items():                      
                    xi, yi = coord
                    if chunk.field[yi][xi][0] in (1, 5): loot = LootSprite(self.loot_textures[data['type']], pickable=data['pickable'])
                    else: loot = LootSprite(pickable=data['pickable'])
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
                
                # for every enemy in chunk
                to_remove = []
                for (xi, yi), data in chunk.enemies.items():
                    if 'sprite' not in data.keys():
                        enemy = EnemyCharacter()
                        if chunk.field[yi][xi][0] in (1, 5):
                            enemy.visible = True
                        enemy.center_x = self.settings['TILE_SIZE'] * 16 * x + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * xi
                        enemy.center_y = self.settings['TILE_SIZE'] * 16 * y + self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * yi
                        enemy.pos = (xi, yi)
                        enemy.chunk = (x, y)
                        chunk.enemies[(xi, yi)]['sprite'] = enemy
                        self.scene.add_sprite("Enemies", enemy)
                    else:
                        enemy = data['sprite']
                        # self.scene.add_sprite("Enemies", enemy)
                        to_remove+=[(xi,yi)]
                        # self.map.get(enemy.get_chunk()).enemies[enemy.pos]
                        # enemy.chunk = enemy.get_chunk()
                        
                for key in to_remove:
                    del chunk.enemies[key]
                
                
                if (x - chunk_x)**2 + (y - chunk_y)**2 > R**2: continue # skip chunks not in a circle
                drawn_chunks.add((x, y))
                if (x, y) in self.drawn_chunks: continue # skip already drawn chunks

                # for all cells in chunk
                for i, line in enumerate(chunk.field):
                    for j, cell in enumerate(line):
                        tile_type = map_types_relation[cell[0]]
                        if tile_type != 'nothing': # if cell has sth
                            if len(cell) == 1:                              # create new sprite if there isn't one yet
                                cell += [TileSprite()]
                                cell[1].center_x = self.settings['TILE_SIZE'] // 2 + j * self.settings['TILE_SIZE'] + self.settings['TILE_SIZE'] * 16 * x
                                cell[1].center_y = self.settings['TILE_SIZE'] // 2 + i * self.settings['TILE_SIZE'] + self.settings['TILE_SIZE'] * 16 * y
                            if tile_type[:7] == 'lighten': 
                                print('err: lighten tile tried to generate!')
                                continue
                            if tile_type[:3] == 'inv':                      # set hitbox for invisibles
                                # cell[1].set_hit_box(self.settings['TILE_HIT_BOX'])
                                ...
                            else:
                                cell[1].change_texture(light = 0)           # or set texture for visibles
                            if tile_type[-4:] == 'wall':
                                if cell[1] in self.scene.get_sprite_list("Floor"):
                                    print('err: drawing the wall already in sprite list')
                                else: 
                                    self.scene.add_sprite("Walls", cell[1])
                            else:
                                if cell[1] in self.scene.get_sprite_list("Floor"):
                                    print('err: drawing the floor already in sprite list!')
                                else: 
                                    self.scene.add_sprite("Floor", cell[1])

        for x, y in self.drawn_chunks - drawn_chunks:                       # for every far chunk
            chunk = self.map.get((x, y))
            for i, line in enumerate(chunk.field):
                for j, cell in enumerate(line):
                    if len(cell) == 2:                                      # for every cell with tile sprite
                        tile_type = map_types_relation[cell[0]]
                        if tile_type[-4:] == 'wall':
                            self.scene.get_sprite_list("Walls").remove(cell[1])
                        else:
                            self.scene.get_sprite_list("Floor").remove(cell[1])

        self.drawn_chunks = drawn_chunks

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
            self.timer_text.text = f"{minutes:02d}:{seconds:02d}:{seconds_100s:02d}"
        
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
                if len(self.active_loot) > 1: self.check_crafts()

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
    
    def drop(self, all = False, coords = 'player'):
        slot = self.selector_sprite.slot
        if coords == 'player': coords = self.player_sprite.position
        posx, posy = (int(i // self.settings['TILE_SIZE']) for i in coords)
        chunk = self.map.get((posx // 16, posy // 16))
        if len(self.score) > slot and self.score[slot] > 0:
            if (posx % 16, posy % 16) not in chunk.loot:
                texture = self.loot_textures[self.labels[slot]['type']]
                loot = LootSprite(texture, pickable=False)
                # loot.set_hit_box(self.settings['LOOT_HIT_BOX'])

                loot.center_x = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * posx
                loot.center_y = self.settings['TILE_SIZE'] // 2 + self.settings['TILE_SIZE'] * posy
                loot.pos = (posx % 16, posy % 16)
                loot.type = self.labels[slot]['type']
                loot.chunk = tuple(chunk.pos)
                if all: loot.amount = self.score[slot]
                self.scene.add_sprite("Items", loot)
                chunk.loot[(posx % 16, posy % 16)] = {'type': self.labels[slot]['type'], 'pickable': False, 'sprite': loot}
                
                
                if all: self.score[slot] = 0
                else: self.score[slot] -= 1

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
                chunk.loot[(posx % 16, posy % 16)]['sprite'].amount += self.score[slot] if all else 1
                if not all: self.score[slot] -= 1
                else: self.score[slot] = 0

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

    def pickup(self, scene = 'Loot', sprites = None):
        if sprites is None: sprites = []                            # Selecting sprites
        if scene:
            sprites += arcade.check_for_collision_with_list(
                self.player_sprite, self.scene[scene]
            )
        for loot in sprites:                                        # for every sprite in list

            self.player_sprite.health += self.settings["HEALTH_BOOST"] # Add health
            if self.player_sprite.health > 1.2: self.player_sprite.health = 1.2

            if loot.is_active:                                      # if active remove from active list
                cords = tuple(loot.pos[i] + val * 16 for i, val in enumerate(loot.chunk))
                del self.active_loot[cords]
                if len(self.active_loot) > 1: self.check_crafts()
                loot.is_active = False

            if scene: self.scene[scene].remove(loot)                # remove sprite from field
            if not loot.is_in_inventory(): del self.map.get(loot.chunk).loot[loot.pos]
            else: continue                                          # skip if dragged from inventory

            loot.remove_from_sprite_lists()
            for i, item in enumerate(self.labels):                  # if inventory has one += amount
                if item['type'] == loot.type:
                    self.score[i] += loot.amount
                    item['label'].text = str(self.score[i])
                    del loot
                    break
            else:                                                   # otherwise add new slot
                loot.center_x = 20
                loot.center_y = len(self.score) * 40 + 20
                loot.pos = None
                loot.chunk = None
                loot.pickable = False
                loot.scale = LootSprite.settings['LOOT_SCALING']
                self.interface.add_sprite("Icons",loot)
                self.score += [loot.amount]
                self.labels += [{'type': loot.type, 'label': arcade.Text(str(loot.amount), 32, (len(self.score) - 1) * 40 + 4, font_size=10), 'sprite': loot}]

    def enemy_collision(self):
        collided = arcade.check_for_collision_with_list(
            self.player_sprite, self.scene["Enemies"]
        )
        for enemy in collided:
            if enemy.striking:
                self.player_sprite.health -= self.settings["ENEMY_HEAT_POINTS"]
                enemy.striking = False

    def atack(self):
        mouse_x = self.mouse_sprite.position[0] + self.camera.position[0] - self.window.width / 2
        mouse_y = self.mouse_sprite.position[1] + self.camera.position[1] - self.window.height / 2
        shoot_x = mouse_x - self.player_sprite.center_x
        shoot_y = mouse_y - self.player_sprite.center_y
        arc = AtackArc(
            pos = self.player_sprite.position, 
            vec = (shoot_x, shoot_y), 
            scale=PlayerCharacter.settings["PLAYER_ATACK_RANGE"]
        )
        self.scene.add_sprite("Effects", arc)
        collided = arcade.check_for_collision_with_list(
            arc,
            self.scene["Enemies"]
        )
        for enemy in collided: # finally remove that enemies from the game
            ans = None
            chunk_enemies = self.map.get(enemy.get_chunk()).enemies
            for key in chunk_enemies:
                if chunk_enemies[key]['sprite'] == enemy:
                    ans = key
            if ans: del chunk_enemies[ans]
            enemy.killed()

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