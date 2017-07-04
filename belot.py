from random import sample, shuffle

# ključevi za lokalne riječnike
leftOpponent=-1
rightOpponent=1
teammate=0
me=None

belaValue=20
lastTrickValue=10

separator = "_"
def card(suit, rank):
    return "{}{}{}".format(suit, separator, rank)

suits = [ "KARO", "HERC", "PIK", "TREF" ]
ranks = [ "VII", "VIII", "IX", "X", "DECKO", "DAMA", "KRALJ", "AS" ]

values = {"VII": 0, "VIII": 0, "IX": 0, "X": 10, "DECKO": 2, "DAMA": 3, "KRALJ": 4, "AS": 11}
valuesTrump = {"VII": 0, "VIII": 0, "IX": 14, "X": 10, "DECKO": 20, "DAMA": 3, "KRALJ": 4, "AS": 11}

declarationCards = []
declarationValues = []

cards = list()
for suit in suits:
    suitCards = []
    for rank in ranks:
        suitCards.append(card(suit, rank))

    for stride, value in [(3, 20), (4, 50), (5, 100), (6, 100), (7, 100)]:
        for i in range(0, len(suitCards)-stride):
            declarationCards.append(set(suitCards[i:i+stride]))
            declarationValues.append(value)
    cards+=suitCards

jokers = set(filter(lambda k: k.split(separator)[1]=="DECKO", cards))
declarationCards.append(jokers)
declarationValues.append(200)

nines = set(filter(lambda k: k.split(separator)[1]=="IX", cards))
declarationCards.append(nines)
declarationValues.append(150)

aces = set(filter(lambda k: k.split(separator)[1]=="AS", cards))
declarationCards.append(aces)
tens = set(filter(lambda k: k.split(separator)[1]=="X", cards))
declarationCards.append(tens)
kings = set(filter(lambda k: k.split(separator)[1]=="KRALJ", cards))
declarationCards.append(kings)
queens = set(filter(lambda k: k.split(separator)[1]=="DAMA", cards))
declarationCards.append(queens)
declarationValues+=[100, 100, 100, 100]

# vrijednost dijeljenja
handValue=0
for c in cards:
    suit, rank = c.split(separator)
    if suit=="HERC":
        handValue+=valuesTrump[rank]
    else:
        handValue+=values[rank]
handValue+=lastTrickValue

def dealCards():
    deck = list(cards)
    shuffle(deck)
    deck = set(deck)

    cardsPerPlayer=len(deck)//4

    cards1 = sample(deck, cardsPerPlayer)
    deck-=set(cards1)
    cards2 = sample(deck, cardsPerPlayer)
    deck-=set(cards2)
    cards3 = sample(deck, cardsPerPlayer)
    deck-=set(cards3)
    cards4 = sample(deck, cardsPerPlayer)
    deck-=set(cards4)
    return cards1, cards2, cards3, cards4

# TODO napisati funkciju koja uspoređuje karte

def getLegalCards(cards, table, dominantSuit, trumpSuit):
    if not dominantSuit or len(cards)==1:
        return cards

    dominants = list()
    higherDominants = list()
    trumps = list()
    higherTrumps = list()

    highestTrump, highestTrumpValue=None,0
    highestDominant, highestDominantValue=None,0
    trumpPresent=False
    # prođi kroz karte na stolu
    for card in table.values():
        suit, rank = card.split(separator)
        if suit==dominantSuit:
            value = values[rank]
            if highestDominant==None or value>highestDominantValue or (value==highestDominantValue and ranks.index(rank)>ranks.index(highestDominant.split(separator)[1])):
                highestDominantValue=value
                highestDominant=card
        if suit==trumpSuit:
            trumpPresent=True
            value = valuesTrump[rank]
            if highestTrump==None or value>highestTrumpValue or (value==highestTrumpValue and ranks.index(rank)>ranks.index(highestTrump.split(separator)[1])):
                highestTrumpValue=value
                highestTrump=card

    # prođi kroz karte u rukama
    for card in cards:
        suit, rank = card.split(separator)
        if suit==dominantSuit:
            dominants.append(card)
            value = values[rank]
            if highestDominant==None or value>highestDominantValue or (value==highestDominantValue and ranks.index(rank)>ranks.index(highestDominant.split(separator)[1])):
                higherDominants.append(card)

        if suit==trumpSuit:
            trumps.append(card)
            value = valuesTrump[rank]
            if highestTrump==None or value>highestTrumpValue or (value==highestTrumpValue and ranks.index(rank)>ranks.index(highestTrump.split(separator)[1])):
                higherTrumps.append(card)

    if len(dominants)>0 and dominantSuit!=trumpSuit:
        if not trumpPresent and len(higherDominants)>0:
            return higherDominants
        else:
            return dominants
    elif len(trumps)>0:
        if trumpPresent and len(higherTrumps)>0:
            return higherTrumps
        else:
            return trumps
    else:
        return cards

# vraća vrijednost štiha (zbroj karata)
def trickValue(table, trumpSuit, lastTrick):
    s = 0
    for card in table.values():
        suit, rank = card.split(separator)
        if suit==trumpSuit:
            s+=valuesTrump[rank]
        else:
            s+=values[rank]
    return s+(lastTrickValue if lastTrick else 0)


# vraća igrača koji kupi štih
def trickWinner(table, dominantSuit, trumpSuit):
    winner=None
    highestTrump=None
    highestDominant=None
    for player in table:
        card = table[player]
        suit, rank = card.split(separator)
        if winner==None:
            winner=player
            if suit==trumpSuit: highestTrump=card
            elif suit==dominantSuit: highestDominant=card
            else: winner=None

        else:
            if highestTrump:
                highestTrumpRank = highestTrump.split(separator)[1]
                highestTrumpValue = valuesTrump[highestTrumpRank]
                if suit==trumpSuit and (valuesTrump[rank]>highestTrumpValue or (valuesTrump[rank]==highestTrumpValue and ranks.index(rank)>ranks.index(highestTrumpRank))):
                    winner=player
                    highestTrump=card
            elif highestDominant:
                highestDominantRank = highestDominant.split(separator)[1]
                highestDominantValue = values[highestDominantRank]
                if suit==trumpSuit:
                    winner=player
                    highestTrump=card
                elif suit==dominantSuit and (values[rank]>highestDominantValue or (values[rank]==highestDominantValue and ranks.index(rank)>ranks.index(highestDominantRank))):
                    winner=player
                    highestDominant=card
    return winner
