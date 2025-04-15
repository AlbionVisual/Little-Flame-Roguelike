import arcade
import arcade.gui

class GameOverView(arcade.View):
    """Main menu view class."""

    def __init__(self, main_view, time_taken, background_texture = None):
        super().__init__()

        if background_texture is not None:
            self.background_texture = background_texture

        self.manager = arcade.gui.UIManager()

        start_new_game_button = arcade.gui.UIFlatButton(text="Start New Game", width=150)
        exit_button = arcade.gui.UIFlatButton(text="Exit", width=320)
        game_over_text = arcade.gui.UILabel(text="Game over",font_size=70)
        timer_text = arcade.gui.UILabel(text="Time taken: " + time_taken, font_size=18,text_color=arcade.color.LIGHT_GRAY)

        self.box = arcade.gui.UIBoxLayout(
            space_between=20
        )

        # Adding the buttons to the layout.
        self.box.add(game_over_text)
        self.box.add(timer_text)
        self.box.add(start_new_game_button)
        self.box.add(exit_button)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())

        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.box,
        )

        self.main_view = main_view

        @start_new_game_button.event("on_click")
        def on_click_start_new_game_button(event):
            # Create a new view because we are starting a new game.
            game = main_view.__class__(-1, **main_view.settings)
            game.setup()
            self.window.show_view(game)

        @exit_button.event("on_click")
        def on_click_exit_button(event):
            arcade.exit()

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
