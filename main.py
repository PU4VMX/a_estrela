from game import TuxGame
from mapa import create_default_map

if __name__ == "__main__":
    game_map = create_default_map()
    game = TuxGame(game_map)
    game.run()
