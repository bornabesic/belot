from interfaces import IPlayer
from enum import Enum
import belot

import numpy as np

class CardState(Enum):
    UNKNOWN = 0
    AVAILABLE = 1
    TABLE = 2
    UNAVAILABLE = 3

class PlayerRL(IPlayer):

    def initialize(self):
        # odigrane karte
        self.playedCards = set()

        self.knowledge = dict()

        # inicijalno sve karte stavi u stanje UNKNOWN
        self.knowledge[CardState.UNKNOWN] = set(belot.cards)

        for player in [belot.PlayerRole.LEFT_OPPONENT, belot.PlayerRole.TEAMMATE, belot.PlayerRole.RIGHT_OPPONENT]:
            self.knowledge[player] = dict()
            for cardStatus in [CardState.AVAILABLE, CardState.UNAVAILABLE, CardState.TABLE]:
                self.knowledge[player][cardStatus] = set()

    def notifyCards(self):
        # makni iz UNKNOWN karte u svojoj ruci
        self.knowledge[CardState.UNKNOWN]-=set(self.cards)

    def notifyTrumpSuit(self, trumpSuit, bidder):
        self.trumpSuit=trumpSuit
        self.bidder = bidder

    def notifyDeclarations(self, declarations):
        knowledge = self.knowledge

        # sve karte poznate iz zvanja prebaci u stanje AVAILABLE
        for player in declarations:
            if player!=belot.PlayerRole.ME:
                for declaredSet in declarations[player]:
                    for card in declaredSet:
                        knowledge[CardState.UNKNOWN].remove(card)
                        knowledge[player][CardState.AVAILABLE].add(card)

    def playCard(self, table, legalCards):
        knowledge = self.knowledge

        # karte na stolu prebaci u stanje TABLE
        for player in table:
            card = player[table]

            if card in knowledge[player][CardState.AVAILABLE]:
                knowledge[player][CardState.AVAILABLE].remove(card)
            elif card in knowledge[CardState.UNKNOWN]:
                knowledge[CardState.UNKNOWN].remove(card)

            knowledge[player][CardState.TABLE].clear()
            knowledge[player][CardState.TABLE].add(card)

        # odredi potez na temelju cijelog stanja igre
        # TODO playing policy network
        cardToPlay = None

        # sve karte iz stanja TABLE prebaci u UNAVAILABLE
        for player in table:
            knowledgeTableCopy = set(knowledge[player][CardState.TABLE])
            for card in knowledgeTableCopy:
                knowledge[player][CardState.TABLE].remove(card)
                knowledge[player][CardState.UNAVAILABLE].add(card)

        self.playedCards.add(cardToPlay)
        return cardToPlay

    def bid(self, must):
        # TODO bidding policy network
        choice = None

        return choice

    def notifyHand(self, pointsUs, pointsThem):
        self.knowledge.clear()

    def notifyTrick(self, cards, value):
        pass

    def notifyBela(self, player, card):
        pass

    def declareBela(self, table):
        # TODO bela declaring policy network
        choice = None

        return choice

    def currentGameState(self):
        knowledge = self.knowledge
        cardStates = [CardState.AVAILABLE, CardState.TABLE, CardState.UNAVAILABLE]

        teammateState = np.zeros(
            shape=(len(cardStates), len(belot.cards)),
            dtype=np.float32
        )

        leftOpponentState = np.zeros(
            shape=(len(cardStates), len(belot.cards)),
            dtype=np.float32
        )

        rightOpponentState = np.zeros(
            shape=(len(cardStates), len(belot.cards)),
            dtype=np.float32
        )

        otherPlayersTuples = [(belot.PlayerRole.TEAMMATE, teammateState), (belot.PlayerRole.LEFT_OPPONENT, leftOpponentState), (belot.PlayerRole.RIGHT_OPPONENT, rightOpponentState)]
        for player, playerState in otherPlayersTuples:
            for i, cardState in enumerate(cardStates):
                for card in knowledge[player][cardState]:
                    j = belot.cards.index(card)
                    playerState[i][j]=1

                for unknownCard in knowledge[CardState.UNKNOWN]:
                    j = belot.cards.index(unknownCard)
                    playerState[0][j] = 1 / len(otherPlayersTuples)

        cardStates = [CardState.AVAILABLE, CardState.UNAVAILABLE]
        meState = np.zeros(
            shape=(len(cardStates), len(belot.cards)),
            dtype=np.float32
        )

        for i, t in enumerate([(self.cards, CardState.AVAILABLE), (self.playedCards, CardState.UNAVAILABLE)]):
            cards, state = t
            for card in cards:
                meState[i][belot.cards.index(card)]=1


        trumpState = np.zeros(
            shape=(1, len(belot.suits)),
            dtype=np.float32
        )
        trumpState[0][belot.suits.index(self.trumpSuit)]=1

        bidderState = np.zeros(
            shape=(1, len(belot.PlayerRole)),
            dtype=np.float32
        )
        bidderState[0][list(belot.PlayerRole).index(self.bidder)]=1

        gameState = np.concatenate([
            meState.flatten(),
            rightOpponentState.flatten(),
            teammateState.flatten(),
            leftOpponentState.flatten(),
            trumpState.flatten(),
            bidderState.flatten()
        ], axis=0)
        return gameState