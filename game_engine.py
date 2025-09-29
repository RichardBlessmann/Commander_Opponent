class GameEngine:
    def __init__(self, players):
        self.players = players
        self.turn = 0

    def start_game(self):
        for p in self.players:
            p.draw_card(7)
            print(f"{p.name} starts with {len(p.hand)} cards.")

        while all(p.life_total > 0 for p in self.players):
            self.play_turn(self.players[self.turn % len(self.players)])
            self.turn += 1
            if self.turn > 20:  # safety stop for now
                break

    def play_turn(self, player):
        print(f"\n=== Turn {self.turn + 1}: {player.name}'s turn ===")
        player.new_turn()
        player.draw_card()
        player.play_land()
        player.cast_creature()

        self.show_table_state()

    def show_table_state(self):
        print("\nCurrent Game State:")
        for p in self.players:
            p.show_state()
