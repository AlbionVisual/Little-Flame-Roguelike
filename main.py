from graphics import RoguelikeView
from main_menu import MainMenuView
import arcade
import json

settings = json.load(open('settings.json', 'r'))

def main():
    """ Main function """

    window = arcade.Window(settings["SCREEN_WIDTH"], settings["SCREEN_HEIGHT"], settings["SCREEN_TITLE"])
    game_view = RoguelikeView(**settings)
    start_view = MainMenuView(game_view)
    window.show_view(start_view)
    arcade.run()

# window = Roguelike(**settings)
# window.setup()
# arcade.run()

if __name__ == "__main__":
    main()