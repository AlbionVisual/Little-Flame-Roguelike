import arcade
from .game_on_load import GameOnLoad
from .utils.sprites import *
# from .utils.sprite_list_pull import ChunkSpriteListPull


class GameSetup(GameOnLoad):
    def setup(self, **new_settings):

        for option in new_settings: # Применить новые настройки (если таковые появились)
            self.settings[option] = new_settings[option]

        PlayerCharacter.settings = self.settings # Обновить настройки всем классам
        EnemyCharacter.settings = self.settings
        TileSprite.settings = self.settings
        LootSprite.settings = self.settings
        AtackArc.settings = self.settings

        EnemyCharacter.walk_textures = self.enemies_textures # Загруженные в init текстуры также передаём классам
        AtackArc.swoop_textures = self.atack_textures

        arcade.set_background_color(arcade.csscolor.BLACK)

        if self.settings["GAME_TYPE"] == "INFINITE": # Разные настройки случаи для разных режимов игры
            self.settings["BORDERS"] = {
                'LEFT': -1,
                'RIGHT': -1,
                'UP': -1,
                'DOWN': -1
            }
        elif self.settings["GAME_TYPE"] == "RUN":
            ...
   
        self.actor_scene.get_sprite_list("Enemies").clear() # Очистка списков спрайтов (на случай, если мы перезапускаем уровень)
        self.actor_scene.get_sprite_list("Loot").clear()
        self.actor_scene.get_sprite_list("Items").clear()
        self.actor_scene.get_sprite_list("Effects").clear()

        self.map_scene.get_sprite_list("Walls").clear()
        self.map_scene.get_sprite_list("Floor").clear()

        self.actor_scene.get_sprite_list("Player").clear() # Пересоздание игрока
        self.player_sprite = PlayerCharacter(self.player_textures)
        self.player_sprite.center_x = self.settings['TILE_SIZE'] * 7 + self.settings['TILE_SIZE'] // 2
        self.player_sprite.center_y = self.settings['TILE_SIZE'] * 7 + self.settings['TILE_SIZE'] // 2
        self.actor_scene.add_sprite("Player", self.player_sprite)
        
        self.mouse_sprite = arcade.SpriteSolidColor( # Для взаимодействия мыши с предметами, лежащими на карте
            width=self.settings['MOUSE_HIT_BOX_SIZE'][0],
            height=self.settings['MOUSE_HIT_BOX_SIZE'][1],
            color=(0, 0, 0, 0)
        )
        self.mouse_sprite.center_x = 0
        self.mouse_sprite.center_y = 0

        cell0 = TileSprite() # Показать движку с какими предметами работать
        cell0.center_x = self.settings['TILE_SIZE'] // 2
        cell0.center_y = self.settings['TILE_SIZE'] // 2
        self.map_scene.add_sprite("Walls", cell0)
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.map_scene.get_sprite_list("Walls")
        )
        cell0.remove_from_sprite_lists()

        # self.map_sprite_lists = ChunkSpriteListPull(self.map_scene, "map_tiles_", sprite_type=TileSprite, context_object=self)

        self.interface = arcade.Scene() # Создание сцены с интерфесом
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
        self.dragging_item_sprite = LootSprite(pickable=False) # Перетягиваемый предмет имеет другую прозрачность и размер
        self.interface.add_sprite("Floatings", self.dragging_item_sprite)

        self.timer_value: float = 0.0 # Таймер для Run режима
        self.timer_text = arcade.Text(
            text="00:00.00",
            x=self.window.width-10,
            y=self.window.height-10,
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