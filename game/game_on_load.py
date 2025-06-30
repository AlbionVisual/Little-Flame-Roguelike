import arcade
from .utils.sprites import *

class GameOnLoad(arcade.View):
    def __init__(self, **new_settings):
        self.settings = default_settings
        for option in new_settings:
            self.settings[option] = new_settings[option]
        super().__init__()
        arcade.set_background_color(arcade.csscolor.BLACK)

        self.map_sprite_lists = None
        self.player_sprite = None
        self.selector_sprite = None
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
            arcade.load_texture('Textures/Loot/crafting_table_front.png'),
            arcade.load_texture('Textures/Loot/bookshelf.png'),
            arcade.load_texture('Textures/Loot/carrot.png'),
            arcade.load_texture('Textures/Loot/feather.png'),
            arcade.load_texture('Textures/Loot/apple.png'),
            arcade.load_texture('Textures/Loot/fish.png'),
            arcade.load_texture('Textures/Loot/door_birch.png'),
            arcade.load_texture('Textures/Loot/jukebox_side.png'),
            arcade.load_texture('Textures/Loot/birch_boat.png'),
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

        self.actor_scene = arcade.Scene()
        self.map_scene = arcade.Scene()

        self.map_scene.add_sprite_list("Walls", use_spatial_hash=True)
        self.map_scene.add_sprite_list("Floor", use_spatial_hash=True)
        self.actor_scene.add_sprite_list("Loot", use_spatial_hash=True)
        self.actor_scene.add_sprite_list("Items", use_spatial_hash=True)
        self.actor_scene.add_sprite_list("Testables", use_spatial_hash=True)
        self.actor_scene.add_sprite_list("Player")
        self.actor_scene.add_sprite_list("Enemies")
        self.actor_scene.add_sprite_list("Effects")