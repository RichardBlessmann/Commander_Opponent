from tkinter import Tk, Label
from PIL import Image, ImageTk
import requests
from io import BytesIO
import random

class Player:
    def __init__(self, name, deck, commander=None):
        self.name = name
        self.deck = deck[:]  # copy
        self.commander = commander
        self.hand = []
        self.battlefield = []
        self.graveyard = []
        self.life_total = 40
        self.command_zone = []
        self.lands_played_this_turn = 0

        if commander:
            self.command_zone.append(commander)
        random.shuffle(self.deck)

    def draw_card(self, n=1):
        for _ in range(n):
            if self.deck:
                self.hand.append(self.deck.pop(0))
            else:
                print(f"{self.name} tried to draw from empty library!")

    def untap_all(self):
        for card in self.battlefield:
            card.tapped = False
        print(f"{self.name} untapped {len(self.battlefield)} cards.")
    def untap(self, card):
        card.tapped = False
        print(f"{self.name} untapped {card.name} card.")

    def play_land(self):
        if self.lands_played_this_turn >= 1:
            return False

        for card in self.hand:
            if card.is_land():
                self.hand.remove(card)
                self.battlefield.append(card)
                self.lands_played_this_turn += 1
                card.tapped = False
                print(f"{self.name} plays land: {card.name}")
                return True
        return False

    def cast_creature(self):
        for card in self.hand:
            if card.is_creature():
                self.hand.remove(card)
                self.battlefield.append(card)
                card.tapped = False  # creatures enter untapped
                print(f"{self.name} casts creature: {card.name}")
                return True
        return False
    def declare_attackers(self):
        attackers = []
        for card in self.battlefield:
            if card.is_creature() and not card.tapped:
                attackers.append(card)

        for card in attackers:
            card.tapped = True
        return attackers

    def declare_blockers(self, incoming_attackers):
        blockers = {}  # attacker -> blocker
        for attacker in incoming_attackers:
            for card in self.battlefield:  # loop over your creatures
                if card.is_creature() and not card.tapped:
                    blockers[attacker] = card
                    card.tapped = True
                    break  # only block with one creature
        return blockers

    def new_turn(self):
        """Resets turn-based limits like lands per turn"""
        self.lands_played_this_turn = 0

    def show_state(self):
        root = Tk()
        root.title(f"{self.name}'s Battlefield")

        for i, card in enumerate(self.battlefield):
            if card.image_url:
                response = requests.get(card.image_url)
                img_data = Image.open(BytesIO(response.content))

                if card.tapped:
                    img_data = img_data.rotate(90, expand=True)  # rotate tapped cards

                img = ImageTk.PhotoImage(img_data)
                lbl = Label(root, image=img)
                lbl.image = img  # keep reference
                lbl.grid(row=0, column=i)

        root.mainloop()