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

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(width=300, height=400, size_hint=None))
        frame.with_padding(all=20)

        # Add a background to the window.
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
        # The type of event listener we used earlier for the button will not work here.
        back_button.on_click = self.on_click_back_button

        title_label = arcade.gui.UILabel(text=title, align="center", font_size=20, multiline=False)
        # Adding some extra space around the title.
        title_label_space = arcade.gui.UISpace(height=30, color=arcade.color.DARK_BLUE_GRAY)

        # input_text_widget = arcade.gui.UIInputText(text=input_text, width=250).with_border()

        # dropdown = arcade.gui.UIDropdown(
        #     default=dropdown_options[0], options=dropdown_options, height=20, width=250
        # )

        # Internal widget layout to handle widgets in this class.
        widget_layout = arcade.gui.UIBoxLayout(align="left", space_between=10)

        widget_layout.add(title_label)
        widget_layout.add(title_label_space)

        for widget in placables:
            widget.size_hint = (1, None)
            widget_layout.add(widget)

        widget_layout.add(back_button)

        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")

    def on_click_back_button(self, event = []):
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent.remove(self)

class OptionsMenu(SubMenu):
    def __init__(self, parent):

        width_label = arcade.gui.UILabel(text="Window width:")
        width_input = arcade.gui.UIInputText(text=str(parent.settings.get("width", 800)))
        v_box_width = arcade.gui.UIBoxLayout(space_between=5).add(width_label).add(width_input)

        height_label = arcade.gui.UILabel(text="Window height:")
        height_input = arcade.gui.UIInputText(text=str(parent.settings.get("height", 600)))
        v_box_height = arcade.gui.UIBoxLayout(space_between=5).add(height_label).add(height_input)

        algorithm_label = arcade.gui.UILabel(text="Select algorithm (default is random):")
        algorithm_dropdown = arcade.gui.UIDropdown(
            options=["Map", "MapPaths"],
            default=parent.settings["ALGORITHM_NAME"]
        )
        v_box_algorithm = arcade.gui.UIBoxLayout(space_between=5).add(algorithm_label).add(algorithm_dropdown)

        save_button = arcade.gui.UIFlatButton(text="Save")
        @save_button.event("on_click")
        def on_click_save(event):            
            parent.settings["ALGORITHM_NAME"] = algorithm_dropdown.value
            super(OptionsMenu, self).on_click_back_button()

        super().__init__(
            "Options",
            [
                v_box_width,
                v_box_height,
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







# Deprecated
class MainMenuView(arcade.View):
    """ View to show instructions """

    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view
        self.manager = arcade.gui.UIManager()
        self.grid = arcade.gui.UIGridLayout(
            column_count=1, row_count=4, horizontal_spacing=20, vertical_spacing=20
        )

        self.play_button = arcade.gui.UIFlatButton(text="play", width=200)
        self.settings_button = arcade.gui.UIFlatButton(text="Settings", width=200)
        game_mode_1_button = arcade.gui.UIFlatButton(text="Run mode", width=200)
        game_mode_2_button = arcade.gui.UIFlatButton(text="Infinite mode", width=200)
        back_button = arcade.gui.UIFlatButton(text="Back", width=200)

        self.show_main_menu()

        @game_mode_1_button.event("on_click")
        def on_click_game_mode_1(event):
            ...

        @game_mode_2_button.event("on_click")
        def on_click_game_mode_2(event):
            # self.manager.disable()
            self.game_view.setup()
            self.window.show_view(self.game_view)
        
        @back_button.event("on_click")
        def on_click_back(event):
            self.show_main_menu()

        @self.play_button.event("on_click")
        def on_click_play(event):
            self.clear_grid()
            self.v_box.add(game_mode_1_button)
            self.v_box.add(game_mode_2_button)
            self.v_box.add(back_button)


        @self.settings_button.event("on_click")
        def on_click_settings(event):
            self.show_settings()
        

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.grid,
        )
    
    def show_main_menu(self):
        self.clear_grid()
        self.grid.add(self.play_button, column=0, row=0)
        self.grid.add(self.settings_button, column=0, row=1)


    def show_settings(self):
        self.settings = self.game_view.settings

        width_input = arcade.gui.UIInputText(text=str(self.settings.get("width", 800)), width=200)
        height_input = arcade.gui.UIInputText(text=str(self.settings.get("height", 600)), width=200)
        width_label = arcade.gui.UILabel(text="Window width:")
        height_label = arcade.gui.UILabel(text="Window height:")


        algorithm_options = [("Fully random placing", "Map"), ("Generate rooms with hallways","MapPaths")]
        algorithm_dropdown = arcade.gui.UIDropdown(
            options=algorithm_options,
            width=200
        )
        algorithm_label = arcade.gui.UILabel(text="Select algorithm (default is random):")


        save_button = arcade.gui.UIFlatButton(text="Save", width=200, height=40)
        @save_button.event("on_click")
        def on_click_save(event):            
            self.settings["ALGORITHM_NAME"] = self.algorithm_dropdown.text
            self.show_main_menu()
        


        self.clear_grid()
        self.grid.add(width_label,row=0)
        self.grid.add(width_input, row=0)
        self.grid.add(height_label,row=1)
        self.grid.add(height_input,row=1)
        self.grid.add(algorithm_dropdown, row=2)
        self.grid.add(algorithm_label, row=2)
        self.grid.add(save_button, row=3)

    def on_show_view(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.TAN)
        self.manager.enable()

    def on_hide_view(self):
        # Disable the UIManager when the view is hidden.
        self.manager.disable()

    def on_draw(self):
        """ Draw this view """
        self.clear()
        self.manager.draw()

    def clear_grid(self):
        while len(self.grid.children) > 0:
            child = self.grid.children[0]
            self.grid.remove(child)

            if child in self.grid.children: self.grid.children.remove(child)