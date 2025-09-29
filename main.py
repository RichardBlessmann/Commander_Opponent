from card import Card
from player import Player
from game_engine import GameEngine
from utils import load_deck
from tkinter import Tk, filedialog


def choose_deck_file():
    Tk().withdraw()
    return filedialog.askopenfilename(title="Choose a deck file", filetypes=[("Text files", "*.txt")])

def main():
    # Example 1: load from file
    deck1_path = choose_deck_file()
    deck1 = load_deck(deck1_path, card_db)

    # Example 2: load directly from list
    deck2, commander2 = load_deck(
        ["Commander", "1x Atraxa, Praetors' Voice",
         "Mainboard", "2x Forest", "1x Llanowar Elves", "1x Grizzly Bears"]
    )

    p1 = Player("Alice", deck1)
    p2 = Player("Bob", deck2)

    game = GameEngine([p1, p2])
    game.start_game()

if __name__ == "__main__":
    main()
