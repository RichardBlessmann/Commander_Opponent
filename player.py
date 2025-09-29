class Player:
    def __init__(self, name, deck):
        self.name = name
        self.deck = deck
        self.hand = []
        self.battlefield = []
        self.graveyard = []
        self.life_total = 40
        self.command_zone = []
