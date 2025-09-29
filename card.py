class Card:
    def __init__(self, name, type_line, mana_cost, text, power=None, toughness=None):
        self.name = name
        self.type_line = type_line
        self.mana_cost = mana_cost
        self.text = text
        self.power = power
        self.toughness = toughness

    def is_land(self):
        return "Land" in self.type_line

    def is_creature(self):
        return "Creature" in self.type_line

    def is_enchantment(self):
        return "Enchantment" in self.type_line

