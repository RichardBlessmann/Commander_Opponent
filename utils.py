import os
import requests
from card import Card

def fetch_card_from_scryfall(card_name):
    url = f"https://api.scryfall.com/cards/named"
    params = {"exact": card_name}
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Could not fetch {card_name} from Scryfall")
        return None

    data = response.json()
    return Card(
        name=data.get("name"),
        type_line=data.get("type_line"),
        mana_cost=data.get("mana_cost", ""),
        text=data.get("oracle_text", ""),
        power=data.get("power"),
        toughness=data.get("toughness"),
    )

def load_deck(source, local_db=None):
    deck = []
    commander = None

    lines = []

    if isinstance(source, str) and os.path.isfile(source):
        with open(source, "r", encoding="utf-8") as f:
            lines = f.readlines()
    elif isinstance(source, list):
        lines = source
    else:
        raise ValueError("Deck source must be a file path or a list of card names.")

    section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.lower().startswith("commander"):
            section = "commander"
            continue
        elif line.lower().startswith("mainboard"):
            section = "mainboard"
            continue
        elif line.lower().startswith("sideboard"):
            section = "sideboard"
            continue

        if "x" in line:
            parts = line.split("x")
            qty, card_name = parts[0].strip(), parts[1].strip()
        else:
            qty, card_name = "1", line

        qty = int(qty) if qty.isdigit() else 1

        # try local db first
        card_obj = None
        if local_db and card_name in local_db:
            card_obj = local_db[card_name]
        else:
            card_obj = fetch_card_from_scryfall(card_name)

        if not card_obj:
            continue

        if section == "commander":
            commander = card_obj
        elif section in ("mainboard", "sideboard", None):
            deck.extend([card_obj] * qty)

    return deck, commander
