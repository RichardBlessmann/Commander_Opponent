class GameEngine:
    def __init__(self, players):
        self.players = players
        self.turn = 0

    def start_game(self):
        for player in self.players:
            # draw opening 7
            for _ in range(7):
                player.draw_card()

        while all(p.life_total > 0 for p in self.players):
            self.next_turn()

    def next_turn(self):
        player = self.players[self.turn % len(self.players)]
        print(f"\n=== {player.name}'s turn ===")

        self.untap_step(player)
        self.upkeep_step(player)
        self.draw_step(player)
        self.main_phase(player)
        self.combat_phase(player)
        self.second_main_phase(player)
        self.end_step(player)
        self.show_table_state()

        self.turn += 1

    def untap_step(self, player):
        player.untap_all()
        print(f"{player.name} untaps permanents.")

    def upkeep_step(self, player):
        print(f"{player.name}'s upkeep step.")

    def draw_step(self, player):
        player.draw_card()

    def main_phase(self, player):
        print(f"{player.name}'s main phase.")

        if player.lands_played_this_turn == 0:
            player.play_land()

        # 2. Cast creatures until the player has no more creatures in hand
        while player.cast_spell():
            pass

    def combat_phase(self, player):
        print(f"{player.name}'s combat phase.")

        target_player = self.players[(self.players.index(player) + 1) % len(self.players)]

        attackers = player.declare_attackers()
        if not attackers:
            print(f"{player.name} has no attackers.")
            return

        print(f"{player.name} attacks with: {[c.name for c in attackers]}")

        blockers = target_player.declare_blockers(attackers)
        if blockers:
            for attacker, blocker in blockers.items():
                print(f"{target_player.name} blocks {attacker.name} with {blocker.name}")

        self.damage_step(attackers, blockers, target_player)


        for p in [player, target_player]:
            dead = [c for c in p.battlefield if c.is_creature() and (c.damage == c.toughness or c.damage >= c.toughness)]
            for c in dead:
                p.battlefield.remove(c)
                p.graveyard.append(c)
                print(f"{c.name} dies and goes to graveyard {p.name}")

    def second_main_phase(self, player):
        print(f"{player.name}'s second main phase.")
        if player.lands_played_this_turn == 0:
            player.play_land()

    def end_step(self, player):
        print(f"{player.name}'s end step.")

        # 1. Reset lands played this turn
        player.lands_played_this_turn = 0

        # 2. Remove summoning sickness for creatures that have been on battlefield since last turn
        # (optional, if you track it per creature)
        for card in player.battlefield:
            if card.is_creature():
                card.summoning_sickness = False  # you need to add this to Card class
                card.damage = 0

        # 3. Print end-of-turn state for debugging
        print(f"End of {player.name}'s turn:")
        print(f"  Life: {player.life_total}")
        print(f"  Hand: {[c.name for c in player.hand]}")
        print(f"  Battlefield: {[c.name for c in player.battlefield]}")
        print(f"  Graveyard: {[c.name for c in player.graveyard]}")
        print(f"  Command Zone: {[c.name for c in player.command_zone]}")

    def show_table_state(self):
        print("\nCurrent Game State:")
        for p in self.players:
            p.show_state()

    def damage_step(self, attackers, blockers, target_player):
        for attacker in attackers:
            if attacker in blockers:
                blocker = blockers[attacker]

                # Assign damage
                blocker.damage += int(attacker.power)
                if "Deathtouch" in attacker.keywords:
                    blocker.damage = int(blocker.toughness)  # any damage kills

                attacker.damage += int(blocker.power)
                if "Deathtouch" in blocker.keywords:
                    attacker.damage = int(attacker.toughness)

                # Trample excess damage
                if "Trample" in attacker.keywords:
                    excess = int(attacker.power) - int(blocker.toughness)
                    if excess > 0:
                        target_player.life_total -= excess
            else:
                # unblocked attacker deals damage to player
                target_player.life_total -= int(attacker.power)
