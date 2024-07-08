from graphics import Roguelike
import arcade
import json

settings = json.load(open('settings.json', 'r'))

window = Roguelike(**settings)
window.setup()
arcade.run()