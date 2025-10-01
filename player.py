from tkinter import Tk, Label
from PIL import Image, ImageTk
import requests
from io import BytesIO
import random

import utils


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
        self.mana_pool = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        self.images = []

        if commander:
            self.command_zone.append(commander)
        random.shuffle(self.deck)

    def tap_card(self, card):
        """Tap any card. If it's a land, add mana accordingly."""
        if card.tap():
            print(f"{self.name} taps {card.name}")
            if card.is_land():
                self.add_mana_from_land(card)

    def add_mana_from_land(self, card):
        """Very simplified: parse land type to decide mana color."""
        if "Forest" in card.name:
            self.mana_pool["G"] += 1
        elif "Island" in card.name:
            self.mana_pool["U"] += 1
        elif "Swamp" in card.name:
            self.mana_pool["B"] += 1
        elif "Mountain" in card.name:
            self.mana_pool["R"] += 1
        elif "Plains" in card.name:
            self.mana_pool["W"] += 1
        else:
            self.mana_pool["C"] += 1  # default colorless

    def can_pay_cost(self, card):
        """Check if player has enough mana to pay for card."""
        cost = parse_mana_cost(card.mana_cost)
        pool = self.mana_pool.copy()

        # Pay colored costs first
        for color in ["W", "U", "B", "R", "G"]:
            if cost[color] > pool[color]:
                return False  # not enough colored mana
            pool[color] -= cost[color]
            cost[color] = 0

        # Pay generic cost with any leftover mana
        total_available = sum(pool.values())
        if total_available < cost["C"]:
            return False

        return True

    def pay_cost(self, card):
        """Actually deduct mana if possible. Returns True if successful."""
        if not self.can_pay_cost(card):
            print(f"{self.name} cannot pay for {card.name} ({card.mana_cost})")
            return False

        cost = utils.parse_mana_cost(card.mana_cost)
        # Deduct colored mana
        for color in ["W", "U", "B", "R", "G"]:
            self.mana_pool[color] -= cost[color]

        # Deduct generic mana with any remaining
        generic_needed = cost["C"]
        for color in ["W", "U", "B", "R", "G", "C"]:
            while generic_needed > 0 and self.mana_pool[color] > 0:
                self.mana_pool[color] -= 1
                generic_needed -= 1

        print(f"{self.name} paid {card.mana_cost} for {card.name}")
        return True

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

    def cast_spell(self):
        """
        Try to cast the first castable nonland spell in hand.
        Permanents go to the battlefield, instants/sorceries to the graveyard.
        """
        for card in self.hand:
            if card.is_land():
                continue  # lands are not cast, they are played separately

            # try to auto-tap lands if not enough mana yet
            if not self.can_pay_cost(card):
                self.auto_tap_lands_for(card)

            if self.can_pay_cost(card) and self.pay_cost(card):
                self.hand.remove(card)

                if any(t in card.type_line for t in [
                    "Creature", "Artifact", "Enchantment", "Planeswalker", "Battle", "Tribal"
                ]):
                    # All permanents enter battlefield
                    self.battlefield.append(card)
                    card.tapped = False
                    print(f"{self.name} casts permanent: {card.name} ({card.mana_cost}) -> battlefield")

                elif "Sorcery" in card.type_line or "Instant" in card.type_line:
                    # Spells resolve then go to graveyard
                    self.graveyard.append(card)
                    print(f"{self.name} casts spell: {card.name} ({card.mana_cost}) -> graveyard")

                else:
                    print(f"{self.name} cast an unknown spell type: {card.name} ({card.type_line})")

                return True

            else:
                print(f"{self.name} cannot pay cost for {card.name} ({card.mana_cost}).")

        return False

    def auto_tap_lands_for(self, card):
        """Naive land tapping: tap untapped lands until we can pay for the card."""
        needed = utils.parse_mana_cost(card.mana_cost)

        # Try to cover colored mana first
        for color in ["W", "U", "B", "R", "G"]:
            while needed[color] > self.mana_pool[color]:
                # find an untapped land that produces this color
                for land in self.battlefield:
                    if land.is_land() and not land.tapped and color in land.text:
                        self.tap_card(land)
                        break
                else:
                    break  # no more of this color available

        # Then try to cover generic (colorless) mana
        while not self.can_pay_cost(card):
            for land in self.battlefield:
                if land.is_land() and not land.tapped:
                    self.tap_card(land)
                    break
            else:
                break  # no more lands to tap

    def declare_attackers(self):
        attackers = []
        for card in self.battlefield:
            if card.is_creature() and not card.tapped:
                # Simple heuristic: only attack with power >= 2
                if int(card.power) >= 2:
                    attackers.append(card)

        for card in attackers:
            card.tapped = True
        return attackers

    def declare_blockers(self, incoming_attackers):
        blockers = {}
        for attacker in incoming_attackers:
            # Possible blockers based on keywords
            if "Flying" in attacker.keywords:
                possible_blockers = [c for c in self.battlefield
                                     if c.is_creature() and not c.tapped and (
                                                 "Flying" in c.keywords or "Reach" in c.keywords)]
            else:
                possible_blockers = [c for c in self.battlefield if c.is_creature() and not c.tapped]

            if possible_blockers:
                # Simple heuristic: block the strongest toughness creature
                best_blocker = max(possible_blockers, key=lambda c: int(c.toughness))
                blockers[attacker] = best_blocker
                best_blocker.tapped = True
        return blockers

    def new_turn(self):
        """Resets turn-based limits like lands per turn"""
        self.lands_played_this_turn = 0

    def show_state(self):
        root = Tk()
        root.title(f"{self.name}'s Battlefield")

        # Keep a list of references so images don't get garbage collected
        self.images = []

        for i, card in enumerate(self.battlefield):
            if card.image_url:
                try:
                    response = requests.get(card.image_url, timeout=10)
                    img_data = Image.open(BytesIO(response.content))

                    # Rotate tapped cards
                    if getattr(card, "tapped", False):
                        img_data = img_data.rotate(90, expand=True)

                    # Resize to fit screen better (optional)
                    img_data = img_data.resize((150, 210))

                    img = ImageTk.PhotoImage(img_data)

                    lbl = Label(root, image=img)
                    lbl.image = img  # attach to label to prevent GC
                    lbl.grid(row=0, column=i, padx=5, pady=5)

                    self.images.append(img)  # keep in player object

                except Exception as e:
                    print(f"⚠️ Could not load image for {card.name}: {e}")
                    # fallback text
                    lbl = Label(root, text=card.name)
                    lbl.grid(row=0, column=i, padx=5, pady=5)

        root.mainloop()