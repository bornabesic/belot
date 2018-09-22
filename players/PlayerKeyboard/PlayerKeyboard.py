import game.belot as belot
from game.interfaces import IPlayer

class PlayerKeyboard(IPlayer):

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
        suits = len(belot.Suit)
        print("KARTE: ", self.cards)
        while True:
            for i, suit in enumerate(suits):
                print("[{}] {}".format(i+1, suit))

            choice = input("Broj boje (ENTER za dalje): ")
            if choice=="" and not must:
                return None

            try:
                choice = int(choice)
            except ValueError:
                continue

            if choice in range(1, len(suits)+1):
                break

        return suits[choice-1]

    def playCard(self, table, legalCards):
        print("KARTE: ", self.cards)
        while True:
            for i, card in enumerate(legalCards):
                print("[{}] {}".format(i+1, card))

            choice = input("Broj karte: ")

            try:
                choice = int(choice)
            except ValueError:
                continue

            if choice in range(1, len(legalCards)+1):
                break

        return legalCards[choice-1]

    def declareBela(self, table):
        while True:
            choice = input("Zvati belu (da / ne)? ")
            if choice=="da":
                return True
            elif choice=="ne":
                return False