from card import Card
from player import Player
from game_engine import GameEngine
from utils import load_deck
from tkinter import Tk, filedialog


def choose_deck_file(name="x"):
    Tk().withdraw()
    return filedialog.askopenfilename(
        title=f"Choose a deck file for {name}",
        filetypes=[("Text files", "*.txt")]
    )

def main():
    # Example 1: load from file
    print(f"Search for Alice")
    deck1_path = choose_deck_file("Alice")
    deck1, commander1 = load_deck(deck1_path)

    print(f"Search for Bob")
    deck2_path = choose_deck_file("Bob")
    deck2, commander2 = load_deck(deck2_path)

    p1 = Player("Alice", deck1, commander1)
    p2 = Player("Bob", deck2, commander2)

    game = GameEngine([p1, p2])
    game.start_game()

if __name__ == "__main__":
    main()
