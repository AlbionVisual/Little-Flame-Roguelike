import arcade
import arcade.gui
from main_menu import StartView

class PauseMenuView(arcade.View):
    """Main menu view class."""

    def __init__(self, main_view, background_texture = None):
        super().__init__()

        if background_texture is not None:
            self.background_texture = background_texture

        self.manager = arcade.gui.UIManager()

        resume_button = arcade.gui.UIFlatButton(text="Resume", width=150)
        start_new_game_button = arcade.gui.UIFlatButton(text="Start New Game", width=150)
        volume_button = arcade.gui.UIFlatButton(text="Volume", width=150)
        options_button = arcade.gui.UIFlatButton(text="Options", width=150)

        exit_button = arcade.gui.UIFlatButton(text="To main menu", width=320)

        self.grid = arcade.gui.UIGridLayout(
            column_count=2, row_count=3, horizontal_spacing=20, vertical_spacing=20
        )

        # Adding the buttons to the layout.
        self.grid.add(resume_button, column=0, row=0)
        self.grid.add(start_new_game_button, column=1, row=0)
        self.grid.add(volume_button, column=0, row=1)
        self.grid.add(options_button, column=1, row=1)
        self.grid.add(exit_button, column=0, row=2, column_span=2)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.grid,
        )

        self.main_view = main_view
        
        @resume_button.event("on_click")
        def on_click_resume_button(event):
            # Pass already created view because we are resuming.
            self.window.show_view(self.main_view)

        @start_new_game_button.event("on_click")
        def on_click_start_new_game_button(event):
            # Create a new view because we are starting a new game.
            # game = main_view.__class__(-1, **main_view.settings)
            main_view.setup()
            self.window.show_view(main_view)

        @exit_button.event("on_click")
        def on_click_exit_button(event):
            start_view = StartView(main_view, **main_view.settings)
            self.window.show_view(start_view)

        @volume_button.event("on_click")
        def on_click_volume_button(event):
            # volume_menu = SubMenu(
            #     "Volume Menu",
            #     "How do you like your volume?",
            #     ["Play: Rock", "Play: Punk", "Play: Pop"],
            # )
            # self.manager.add(volume_menu, layer=1)
            ...

        @options_button.event("on_click")
        def on_click_options_button(event):
            # options_menu = SubMenu(
            #     "Funny Menu",
            #     "Too much fun here",
            #     ["Make Fun", "Enjoy Fun", "Like Fun"],
            # )
            # self.manager.add(options_menu, layer=1)
            ...


    def on_hide_view(self):
        self.manager.disable()

    def on_show_view(self):
        """This is run once when we switch to this view"""

        # arcade.set_background_color(arcade.color.BLACK)

        self.manager.enable()

    def on_draw(self):
        """Render the screen."""
        self.clear()
        if self.background_texture:
            arcade.draw_texture_rect(
                self.background_texture,
                arcade.LBWH(0, 0, self.window.width, self.window.height),
            )
        self.manager.draw()
