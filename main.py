def load_deck(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    deck = []
    for line in lines:
        card_name = line.strip().split('x')[-1].strip()
        deck.append(card_name)
    return deck


