import arcade
import arcade.gui


class StartView(arcade.View):

    def __init__(self, game_view_class, settings):
        super().__init__()
        self.settings = settings
        self.game_view_class = game_view_class
        self.manager = arcade.gui.UIManager()

        play_button = arcade.gui.UIFlatButton(text="Play", width=250)

        @play_button.event("on_click")
        def on_click_switch_button(event):
            menu_view = PlayMenu(self)
            self.manager.add(menu_view, layer=1)

        settings_button = arcade.gui.UIFlatButton(text="Settings", width=250)

        @settings_button.event("on_click")
        def on_click_switch_button(event):
            menu_view = OptionsMenu(self)
            self.manager.add(menu_view, layer=1)

        self.v_box = arcade.gui.UIBoxLayout(space_between=20)
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(anchor_x="center_x", anchor_y="center_y", child=self.v_box)


        self.v_box.add(anchor_x="center_x", anchor_y="center_y", child=play_button)
        self.v_box.add(anchor_x="center_x", anchor_y="center_y", child=settings_button)

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)
        self.manager.enable()

    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        self.manager.disable()

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
        self.clear()

        self.manager.draw()

class MenuView(arcade.View):
    """Main menu view class."""

    def __init__(self, main_view):
        super().__init__()

        self.manager = arcade.gui.UIManager()

        resume_button = arcade.gui.UIFlatButton(text="Resume", width=150)
        start_new_game_button = arcade.gui.UIFlatButton(text="Start New Game", width=150)
        volume_button = arcade.gui.UIFlatButton(text="Volume", width=150)
        options_button = arcade.gui.UIFlatButton(text="Options", width=150)

        exit_button = arcade.gui.UIFlatButton(text="Exit", width=320)

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
            self.window.show_view(self.main_view.game_view)

        @start_new_game_button.event("on_click")
        def on_click_start_new_game_button(event):
            # Create a new view because we are starting a new game.
            
            self.window.show_view(self.main_view.game_view)

        @exit_button.event("on_click")
        def on_click_exit_button(event):
            arcade.exit()

        @volume_button.event("on_click")
        def on_click_volume_button(event):
            volume_menu = SubMenu(
                "Volume Menu",
                "How do you like your volume?",
                ["Play: Rock", "Play: Punk", "Play: Pop"],
            )
            self.manager.add(volume_menu, layer=1)

        @options_button.event("on_click")
        def on_click_options_button(event):
            options_menu = SubMenu(
                "Funny Menu",
                "Too much fun here",
                ["Make Fun", "Enjoy Fun", "Like Fun"],
            )
            self.manager.add(options_menu, layer=1)


    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        self.manager.disable()

    def on_show_view(self):
        """This is run once when we switch to this view"""

        # Makes the background darker
        arcade.set_background_color([rgb - 50 for rgb in arcade.color.DARK_BLUE_GRAY])

        self.manager.enable()

    def on_draw(self):
        """Render the screen."""

        # Clear the screen
        self.clear()
        self.manager.draw()

class SubMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    """Acts like a fake view/window."""

    def __init__(
        self,
        title: str,
        placables: list[arcade.gui.UIWidget]
    ):
        super().__init__(size_hint=(1, 1))

        frame = self.add(arcade.gui.UIAnchorLayout(width=300, height=400, size_hint=None))
        frame.with_padding(all=20)

        frame.with_background(
            texture=arcade.gui.NinePatchTexture(
                left=7,
                right=7,
                bottom=7,
                top=7,
                texture=arcade.load_texture(
                    ":resources:gui_basic_assets/window/dark_blue_gray_panel.png"
                ),
            )
        )

        back_button = arcade.gui.UIFlatButton(text="Back", width=250)
        back_button.on_click = self.on_click_back_button

        title_label = arcade.gui.UILabel(text=title, align="center", font_size=20, multiline=False)
        title_label_space = arcade.gui.UISpace(height=30, color=arcade.color.DARK_BLUE_GRAY)

        widget_layout = arcade.gui.UIBoxLayout(align="center", space_between=10, size_hint_max=(245,None))

        widget_layout.add(title_label)
        widget_layout.add(title_label_space)

        for widget in placables:
            widget_layout.add(widget)

        widget_layout.add(back_button)
        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")

    def on_click_back_button(self, event = []):
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent.remove(self)

class OptionsMenu(SubMenu):
    def __init__(self, parent):

        left_input = arcade.gui.UIInputText(text=str(parent.settings.get('BORDERS', {'LEFT':-1})['LEFT']), width=50)
        up_input = arcade.gui.UIInputText(text=str(parent.settings.get('BORDERS', {'UP':-1})['UP']), width=50)
        right_input = arcade.gui.UIInputText(text=str(parent.settings.get('BORDERS', {'RIGHT':-1})['RIGHT']), width=50)
        down_input = arcade.gui.UIInputText(text=str(parent.settings.get('BORDERS', {'DOWN':-1})['DOWN']), width=50)

        grid_label = arcade.gui.UILabel(text="Select border distances")
        grid = arcade.gui.UIGridLayout(
            column_count=3, row_count=3, horizontal_spacing=5, vertical_spacing=5
        )
        grid.add(left_input, column=0, row=1)
        grid.add(up_input, column=1, row=0)
        grid.add(right_input, column=2, row=1)
        grid.add(down_input, column=1, row=2)
        v_box_grid = arcade.gui.UIBoxLayout(space_between=5)
        v_box_grid.add(grid_label)
        v_box_grid.add(grid)

        algorithm_label = arcade.gui.UILabel(text="Select algorithm (default is random):")
        algorithm_dropdown = arcade.gui.UIDropdown(
            options=["Map", "MapPaths"],
            default=parent.settings["ALGORITHM_NAME"]
        )
        v_box_algorithm = arcade.gui.UIBoxLayout(space_between=5)
        v_box_algorithm.add(algorithm_label)
        v_box_algorithm.add(algorithm_dropdown)

        save_button = arcade.gui.UIFlatButton(text="Save")
        @save_button.event("on_click")
        def on_click_save(event):
            parent.settings["ALGORITHM_NAME"] = algorithm_dropdown.value
            parent.settings["BORDERS"] = {
                'LEFT': int(left_input.text),
                'RIGHT': int(right_input.text),
                'UP': int(up_input.text),
                'DOWN': int(down_input.text)
            }
            super(OptionsMenu, self).on_click_back_button()

        super().__init__(
            "Options",
            [
                v_box_grid,
                v_box_algorithm,
                save_button
            ]
        )

class PlayMenu(SubMenu):
    def __init__(self, parent):
        game_mode_1_button = arcade.gui.UIFlatButton(text="Run mode")
        game_mode_2_button = arcade.gui.UIFlatButton(text="Infinite mode")

        @game_mode_1_button.event("on_click")
        def on_click_game_mode_1(event):
            ...
            super(PlayMenu, self).on_click_back_button()


        @game_mode_2_button.event("on_click")
        def on_click_game_mode_2(event):
            # self.manager.disable()
            self.game_view = parent.game_view_class(**parent.settings)
            super(PlayMenu, self).on_click_back_button()
            parent.window.show_view(self.game_view)
            self.game_view.setup()

        super().__init__(
            "Start game",
            [
                game_mode_1_button,
                game_mode_2_button
            ]
            )