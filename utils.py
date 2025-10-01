import os
import requests
from card import Card
import re


def parse_mana_cost(mana_cost):
    """
    Convert mana cost string like '2GGU' into a dict:
    {'C': 2, 'G': 2, 'U': 1}
    """
    cost = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}

    # Match groups like "2", "G", "U", etc.
    tokens = re.findall(r"\d+|[WUBRGC]", mana_cost)

    for token in tokens:
        if token.isdigit():
            cost["C"] += int(token)  # generic mana
        else:
            cost[token] += 1

    return cost


def fetch_card_from_scryfall(card_name):
    url = "https://api.scryfall.com/cards/named"
    params = {"exact": card_name}
    print(f"Fetching: {card_name}")  # debug

    try:
        response = requests.get(url, params=params, timeout=10)
    except Exception as e:
        print(f"Network error while fetching {card_name}: {e}")
        return None

    if response.status_code != 200:
        print(f"Failed to fetch {card_name} (status {response.status_code})")
        try:
            print("Scryfall says:", response.json())  # show API error
        except:
            print("Raw response:", response.text)
        return None

    data = response.json()
    image_url_float = data.get("image_uris", {}).get("normal")
    return Card(
        name=data.get("name"),
        type_line=data.get("type_line"),
        mana_cost=data.get("mana_cost", ""),
        text=data.get("oracle_text", ""),
        power=data.get("power"),
        toughness=data.get("toughness"),
        image_url=image_url_float,
    )
def parse_deck_line(line: str):
    line = line.strip()
    if not line:
        return None, None

    if "x" in line and line[0].isdigit():
        qty, card_name = line.split("x",1)
        qty = qty.strip()
        card_name = card_name.strip()
    else:
        qty, card_name = "1", line

    try:
        qty = int(qty)
    except ValueError:
        qty = 1

    return qty, card_name
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

    section_headers = (
        "commander", "mainboard", "sideboard",
        "anthem", "blink", "artifact", "enchantment", "sorcery",
        "instant", "planeswalker", "creatures", "land",
        "draw", "protection", "ramp", "removal", "recursion",
        "tokens", "proliferate", "pump", "evasion"
    )

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.lower() in section_headers:
            section = line.lower()
            continue

        qty, card_name = parse_deck_line(line)
        if not card_name:
            continue

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
