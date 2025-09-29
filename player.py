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

    def play_land(self):
        if self.lands_played_this_turn >= 1:
            return False

        for card in self.hand:
            if card.is_land():
                self.hand.remove(card)
                self.battlefield.append(card)
                self.lands_played_this_turn += 1
                print(f"{self.name} plays land: {card.name}")
                return True
        return False

    def cast_creature(self):
        for card in self.hand:
            if card.is_creature():
                # skipping mana payment for now
                self.hand.remove(card)
                self.battlefield.append(card)
                print(f"{self.name} casts creature: {card.name}")
                return True
        return False

    def new_turn(self):
        """Resets turn-based limits like lands per turn"""
        self.lands_played_this_turn = 0

    def show_state(self):
        print(f"\n📜 {self.name}'s State:")
        print(f"   Life: {self.life_total}")
        if self.command_zone:
            print(f"   Commander: {', '.join([c.name for c in self.command_zone])}")
        print(f"   Hand ({len(self.hand)}): {[c.name for c in self.hand]}")
        print(f"   Battlefield ({len(self.battlefield)}): {[c.name for c in self.battlefield]}")
        print(f"   Graveyard ({len(self.graveyard)}): {[c.name for c in self.graveyard]}")
        print(f"   Library: {len(self.deck)} cards left")