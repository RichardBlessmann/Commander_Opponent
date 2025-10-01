class Card:
    def __init__(self, name, type_line, mana_cost, text, power=None, toughness=None, image_url=None):
        self.name = name
        self.type_line = type_line
        self.mana_cost = mana_cost
        self.text = text
        self.power = power
        self.toughness = toughness
        self.tapped = False
        self.summoning_sickness = True
        self.image_url = image_url
        self.damage = 0
        self.keywords = self.parse_keywords()

    def parse_keywords(self):
        keywords_list = ["Flying", "Trample", "Deathtouch", "Reach", "Haste", "Lifelink"]
        return [kw for kw in keywords_list if kw.lower() in self.text.lower()]

    def tap(self):
        if not self.tapped:
            self.tapped = True
            return True
        return False  # already tapped

    def untap(self):
        self.tapped = False



    def is_land(self):
        return "Land" in self.type_line

    def is_creature(self):
        return "Creature" in self.type_line

    def is_enchantment(self):
        return "Enchantment" in self.type_line

