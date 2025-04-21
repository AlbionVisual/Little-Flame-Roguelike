from graphics import RoguelikeView
from main_menu import *
import arcade
import json


def main():
    """ Main function """

    settings = json.load(open('settings.json', 'r'))
    window = arcade.Window(settings["SCREEN_WIDTH"], settings["SCREEN_HEIGHT"], settings["SCREEN_TITLE"], resizable=True)
    window.set_minimum_size(width=400 * 2,height=300 * 2)
    game_view = RoguelikeView(**settings)
    start_view = StartView(game_view,**settings)
    window.show_view(start_view)
    # game = RoguelikeView(-1, **settings)
    # game.setup()
    # window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()