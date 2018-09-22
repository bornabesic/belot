from random import sample, shuffle
from enum import IntEnum, auto, unique
from collections import defaultdict

@unique
class PlayerRole(IntEnum):
    ME             = 0
    RIGHT_OPPONENT = 1
    TEAMMATE       = 2
    LEFT_OPPONENT  = 3

@unique
class Suit(IntEnum):
    KARO = 0
    HERC = 1
    PIK  = 2
    TREF = 3

@unique
class Rank(IntEnum):
    VII   = 0
    VIII  = 1
    IX    = 2
    X     = 3
    DECKO = 4
    DAMA  = 5
    KRALJ = 6
    AS    = 7

belaValue = 20
lastTrickValue = 10
stihMacValue = 90

# Vrijednosti karata
values = {
    Rank.VII:    0,
    Rank.VIII:   0,
    Rank.IX:     0,
    Rank.X:     10,
    Rank.DECKO:  2,
    Rank.DAMA:   3,
    Rank.KRALJ:  4,
    Rank.AS:    11
}

# Vrijednosti karata u adutu
valuesTrump = {
    Rank.VII:    0,
    Rank.VIII:   0,
    Rank.IX:    14,
    Rank.X:     10,
    Rank.DECKO: 20,
    Rank.DAMA:   3,
    Rank.KRALJ:  4,
    Rank.AS:    11
}

class Card:

    def __init__ (self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.hash = (2 ** suit) * (3 ** rank)

    def __str__(self):

        suitRepresentation = {
            Suit.KARO: "KARO ♦",
            Suit.HERC: "HERC ♥",
            Suit.PIK:  "PIK ♠",
            Suit.TREF: "TREF ♣"
        }

        rankRepresentation = {
            Rank.VII:   "VII",
            Rank.VIII:  "VIII",
            Rank.IX:    "IX",
            Rank.X:     "X",
            Rank.DECKO: "DEČKO",
            Rank.DAMA:  "DAMA",
            Rank.KRALJ: "KRALJ",
            Rank.AS:    "AS"
        }

        return "{} {}".format(
            suitRepresentation[self.suit],
            rankRepresentation[self.rank]
        )

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, index):
        return (self.suit, self.rank)[index]

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return self.hash

    def value(self, trumpSuit):
        if self.suit == trumpSuit:
            return valuesTrump[self.rank]

        return values[self.rank]

# Zvanja - karte i vrijednosti
declarationCards = []
declarationValues = []

# Sve karte
cards = list()

for suit in Suit:
    # Sve karte u trenutnoj boji
    suitCards = list(map(lambda r: Card(suit, r), Rank))

    # Dodaj u sve karte
    cards += suitCards

    # Zvanja u trenutnoj boji
    for stride, value in [(3, 20), (4, 50), (5, 100), (6, 100), (7, 100), (8, 1001)]:
        for i in range(0, len(suitCards) - stride):
            declarationCards.append(set(suitCards[i : i + stride]))
            declarationValues.append(value)

# Kroz različite boje
# 4 dečka
jokers = set(filter(lambda c: c.rank == Rank.DECKO, cards))
declarationCards.append(jokers)
declarationValues.append(200)

# 4 devetke
nines = set(filter(lambda c: c.rank == Rank.IX, cards))
declarationCards.append(nines)
declarationValues.append(150)

# 4 asa
aces = set(filter(lambda c: c.rank == Rank.AS, cards))
declarationCards.append(aces)
# 4 desetke
tens = set(filter(lambda c: c.rank == Rank.X, cards))
declarationCards.append(tens)
# 4 kralja
kings = set(filter(lambda c: c.rank == Rank.KRALJ, cards))
declarationCards.append(kings)
# 4 dame
queens = set(filter(lambda c: c.rank == Rank.DAMA, cards))
declarationCards.append(queens)

declarationValues += [100, 100, 100, 100]

# Vrijednost minimalnog dijeljenja (bez zvanja)
handValue = 0
for card in cards:
    handValue += card.value(trumpSuit = Suit.HERC) # Može biti bilo koja boja
handValue += lastTrickValue

def dealCards():
    deck = list(cards)
    shuffle(deck)
    deck = set(deck)

    cardsPerPlayer = len(deck) // 4

    cards1 = sample(deck, cardsPerPlayer)
    deck -= set(cards1)
    cards2 = sample(deck, cardsPerPlayer)
    deck -= set(cards2)
    cards3 = sample(deck, cardsPerPlayer)
    deck -= set(cards3)
    cards4 = sample(deck, cardsPerPlayer)
    deck -= set(cards4)
    return cards1, cards2, cards3, cards4

# TODO napisati funkciju koja uspoređuje karte

def getLegalCards(cards, table, dominantSuit, trumpSuit):
    if not dominantSuit or len(cards) == 1:
        return cards

    dominants = list()
    higherDominants = list()
    trumps = list()
    higherTrumps = list()

    highestTrump, highestTrumpValue = None, 0
    highestDominant, highestDominantValue = None, 0
    trumpPresent = False
    # prođi kroz karte na stolu
    for card in table.values():
        suit, rank = card
        if suit == dominantSuit:
            value = values[rank]
            if highestDominant is None or value > highestDominantValue or (value == highestDominantValue and rank > highestDominant.rank):
                highestDominantValue = value
                highestDominant = card
        if suit == trumpSuit:
            trumpPresent = True
            value = valuesTrump[rank]
            if highestTrump is None or value > highestTrumpValue or (value == highestTrumpValue and rank > highestTrump.rank):
                highestTrumpValue = value
                highestTrump = card

    # prođi kroz karte u rukama
    for card in cards:
        suit, rank = card
        if suit == dominantSuit:
            dominants.append(card)
            value = values[rank]
            if highestDominant is None or value > highestDominantValue or (value == highestDominantValue and rank > highestDominant.rank):
                higherDominants.append(card)

        if suit == trumpSuit:
            trumps.append(card)
            value = valuesTrump[rank]
            if highestTrump is None or value > highestTrumpValue or (value == highestTrumpValue and rank > highestTrump.rank):
                higherTrumps.append(card)

    if len(dominants) > 0 and dominantSuit != trumpSuit:
        if not trumpPresent and len(higherDominants) > 0:
            return higherDominants
        else:
            return dominants
    elif len(trumps) > 0:
        if trumpPresent and len(higherTrumps) > 0:
            return higherTrumps
        else:
            return trumps
    else:
        return cards

# vraća vrijednost štiha (zbroj karata)
def trickValue(table, trumpSuit, lastTrick):
    s = 0
    for card in table.values():
        suit, rank = card
        s += card.value(trumpSuit)
    return s + (lastTrickValue if lastTrick else 0)

# vraća igrača koji kupi štih
def trickWinner(table, dominantSuit, trumpSuit):
    winner = None
    highestTrump = None
    highestDominant = None
    for player in table:
        card = table[player]
        suit, rank = card
        if winner is None:
            winner = player
            if suit == trumpSuit: highestTrump = card
            elif suit == dominantSuit: highestDominant = card
            else: winner = None

        else:
            if highestTrump:
                highestTrumpRank = highestTrump.rank
                highestTrumpValue = valuesTrump[highestTrumpRank]
                if suit == trumpSuit and (valuesTrump[rank] > highestTrumpValue or (valuesTrump[rank] == highestTrumpValue and rank > highestTrumpRank)):
                    winner = player
                    highestTrump = card
            elif highestDominant:
                highestDominantRank = highestDominant.rank
                highestDominantValue = values[highestDominantRank]
                if suit == trumpSuit:
                    winner = player
                    highestTrump = card
                elif suit == dominantSuit and (values[rank] > highestDominantValue or (values[rank] == highestDominantValue and rank > highestDominantRank)):
                    winner = player
                    highestDominant = card
    return winner
