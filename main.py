from game import RoguelikeView
from game.interfaces.main_menu import StartView
import arcade
import json


def main():
    settings = json.load(open('settings.json', 'r'))
    window = arcade.Window(settings["SCREEN_WIDTH"], settings["SCREEN_HEIGHT"], settings["SCREEN_TITLE"], resizable=True)
    window.set_minimum_size(width=400 * 2,height=300 * 2)
    game_view = RoguelikeView(**settings)
    start_view = StartView(game_view,**settings)
    window.show_view(start_view)
    arcade.run()

if __name__ == "__main__":
    main()