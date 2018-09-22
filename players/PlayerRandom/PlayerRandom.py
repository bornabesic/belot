from random import choice, choices

import game.belot as belot
from game.interfaces import IPlayer


class PlayerRandom(IPlayer):

    def initialize(self):
        pass

    def notifyCards(self):
        pass

    def notifyTrumpSuit(self, trumpSuit, bidder):
        pass

    def notifyDeclarations(self, declarations):
        pass

    def notifyTrick(self, cards, value):
        pass

    def notifyHand(self, pointsUs, pointsThem):
        pass

    def notifyGame(self, pointsUs, pointsThem):
        pass

    def notifyBela(self, player, card):
        pass

    def bid(self, must):
        suits = list(belot.Suit)
        if must:
            return choice(suits)

        options = suits + [None]
        weights = [1/8, 1/8, 1/8, 1/8, 1/2]
        return choices(options, weights = weights)[0]

    def playCard(self, table, legalCards):
        return choice(legalCards)

    def declareBela(self, table):
        return choice([True, False])
