import arcade
import arcade.gui

class MainMenuView(arcade.View):
    """ View to show instructions """

    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.v_box = arcade.gui.UIBoxLayout()

        play_button = arcade.gui.UIFlatButton(text="play", width=200)
        settings_button = arcade.gui.UIFlatButton(text="Settings", width=200)
        game_mode_1_button = arcade.gui.UIFlatButton(text="Run mode", width=200)
        game_mode_2_button = arcade.gui.UIFlatButton(text="Infinite mode", width=200)
        back_button = arcade.gui.UIFlatButton(text="Back", width=200)

        self.v_box.add(play_button.with_space_around(bottom=20))
        self.v_box.add(settings_button.with_space_around(bottom=20))

        @game_mode_1_button.event("on_click")
        def on_click_game_mode_1(event):
            ...

        @game_mode_2_button.event("on_click")
        def on_click_game_mode_2(event):
            self.manager.disable()
            self.game_view.setup()
            self.window.show_view(self.game_view)
        
        @back_button.event("on_click")
        def on_click_back(event):
            self.clear_vbox()
            self.v_box.add(play_button.with_space_around(bottom=20))
            self.v_box.add(settings_button.with_space_around(bottom=20))

        @play_button.event("on_click")
        def on_click_play(event):
            self.clear_vbox()
            self.v_box.add(game_mode_1_button.with_space_around(bottom=20))
            self.v_box.add(game_mode_2_button.with_space_around(bottom=20))
            self.v_box.add(back_button.with_space_around(bottom=20))


        @settings_button.event("on_click")
        def on_click_settings(event):
            print("Settings:", event)
        
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x",
                anchor_y="center_y",
                child=self.v_box)
        )

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.TAN)
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_draw(self):
        """ Draw this view """
        self.clear()
        self.manager.draw()
    
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        ...

    def clear_vbox(self):
        while len(self.v_box.children) > 0:
            child = self.v_box.children[0]
            self.v_box.remove(child)

            if child in self.manager.children: self.manager.children.remove(child)