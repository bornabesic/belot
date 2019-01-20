import game.belot as belot
from game.interfaces import IPlayer

from enum import Enum
from .policy import BiddingPolicy
from .policy import PlayingPolicy

import numpy as np
from math import pow

"""
    Ulaz u neuronsku mrežu:
        LEFT_OPPONNENT: 32 x (AVAILABLE, TABLE, UNAVAILABLE): 96
        RIGHT_OPPONNENT: 32 x (AVAILABLE, TABLE, UNAVAILABLE): 96
        TEAMMATE: 32 x (AVAILABLE, TABLE, UNAVAILABLE): 96
        ME: 32 x (AVAILABLE, UNAVAILABLE): 64
        TRUMP: 4
        BIDDER: 4
    = 360
"""

class CardState(Enum):
    UNKNOWN = 0     # ne zna se gdje je karta
    AVAILABLE = 1   # netko ima kartu u ruci
    TABLE = 2       # karta je na stolu
    UNAVAILABLE = 3 # netko je kartu već odigrao

class PlayerRL(IPlayer):

    def initialize(self):
        self.train()

        # stanja i odgovarajuće nagrade
        # za neuronsku mrežu koja određuje slijedeću kartu
        self.playingDiscount = 0.95
        self.playingReward = 0
        self.trickNumber = 0

        self.playingPolicy = PlayingPolicy()
        # za neuronsku mrežu koja određuje zvanje aduta

        self.biddingPolicy = BiddingPolicy()

        # odigrane karte
        self.playedCards = set()

        # vlastito znanje o igri
        self.knowledge = dict()

        # inicijalno sve karte stavi u stanje UNKNOWN
        self.knowledge[CardState.UNKNOWN] = set(belot.cards)

        # inicijaliziraj skupove za svakog igrača
        for player in [belot.PlayerRole.LEFT_OPPONENT, belot.PlayerRole.TEAMMATE, belot.PlayerRole.RIGHT_OPPONENT]:
            self.knowledge[player] = dict()
            for cardStatus in [CardState.AVAILABLE, CardState.UNAVAILABLE, CardState.TABLE]:
                self.knowledge[player][cardStatus] = set()

    def notifyCards(self):
        # makni iz UNKNOWN karte u svojoj ruci
        self.knowledge[CardState.UNKNOWN] -= set(self.cards)

    def notifyTrumpSuit(self, trumpSuit, bidder):
        self.trumpSuit = trumpSuit
        self.bidder = bidder

    def notifyDeclarations(self, declarations):
        knowledge = self.knowledge

        # sve karte poznate iz zvanja prebaci u stanje AVAILABLE
        for player in declarations:
            if player != belot.PlayerRole.ME:
                for declaredSet in declarations[player]:
                    knowledge[CardState.UNKNOWN] -= declaredSet
                    knowledge[player][CardState.AVAILABLE] |= declaredSet

    def playCard(self, table, legalCards):
        knowledge = self.knowledge

        # karte na stolu prebaci u stanje TABLE
        for player in table:
            card = table[player]

            if card in knowledge[player][CardState.AVAILABLE]:
                knowledge[player][CardState.AVAILABLE].remove(card)
            elif card in knowledge[CardState.UNKNOWN]:
                knowledge[CardState.UNKNOWN].remove(card)

            knowledge[player][CardState.TABLE].clear()
            knowledge[player][CardState.TABLE].add(card)

        # playing policy network
        playingState, trumpIndex, bidderIndex = self.playingState

        action_idx, log_action_probability = self.playingPolicy(playingState, trumpIndex, bidderIndex, legalCards)

        cardToPlay = belot.cards[action_idx]

        # sve karte iz stanja TABLE prebaci u UNAVAILABLE
        for player in table:
            knowledgeTableCopy = set(knowledge[player][CardState.TABLE])
            for card in knowledgeTableCopy:
                knowledge[player][CardState.TABLE].remove(card)
                knowledge[player][CardState.UNAVAILABLE].add(card)

        self.playedCards.add(cardToPlay)
        return cardToPlay

    def bid(self, must):
        # bidding policy network
        biddingState = self.biddingState

        options = list(belot.Suit) + [None]
        action_idx, log_action_probability = self.biddingPolicy(biddingState, must)

        return options[action_idx]

    def notifyHand(self, pointsUs, pointsThem):
        # if len(self.biddingActions) == len(self.biddingRewards) + 1:
        #     normalizedReward = pointsUs / 81 - 1
        #     self.biddingRewards.append(normalizedReward)

        self.playingPolicy.updatePolicy()

        # resetiraj
        self.playedCards.clear()

        # inicijalno sve karte stavi u stanje UNKNOWN
        self.knowledge.clear()
        self.knowledge[CardState.UNKNOWN] = set(belot.cards)

        for player in [belot.PlayerRole.LEFT_OPPONENT, belot.PlayerRole.TEAMMATE, belot.PlayerRole.RIGHT_OPPONENT]:
            self.knowledge[player] = dict()
            for cardStatus in [CardState.AVAILABLE, CardState.UNAVAILABLE, CardState.TABLE]:
                self.knowledge[player][cardStatus] = set()

    def notifyTrick(self, cards, value):
        normalizedReward = value / 56
        self.playingPolicy.feedback(normalizedReward)

    def notifyGame(self, pointsUs, pointsThem):
        # treniraj mrežu za zvanje aduta
        self.biddingPolicy.updatePolicy()

    def notifyBela(self, player, card):
        pass

    def declareBela(self, table):
        # TODO bela declaring policy network
        choice = True

        return choice

    def train(self):
        self.train = True

    def eval(self):
        self.train = False

    @property
    def playingState(self) -> np.ndarray:
        knowledge = self.knowledge
        cardStates = [
            CardState.AVAILABLE,
            CardState.UNAVAILABLE,
            CardState.TABLE
        ]

        state = np.zeros(
            shape=(len(belot.PlayerRole), len(cardStates), len(belot.cards))
        )

        otherPlayers = [
            belot.PlayerRole.TEAMMATE,
            belot.PlayerRole.LEFT_OPPONENT,
            belot.PlayerRole.RIGHT_OPPONENT,
        ]
        for i, player in enumerate(otherPlayers):
            for j, cardState in enumerate(cardStates):
                # Za karte koje znaš gdje su, rasporedi ih sa
                # sigurnošću
                for card in knowledge[player][cardState]:
                    k = belot.cards.index(card)
                    state[i, j, k] = 1

                # Ako ne znaš gdje je karta, uniformno rasporedi
                # vjerojatnosti po igračima kao AVAILABLE (0)
                for unknownCard in knowledge[CardState.UNKNOWN]:
                    k = belot.cards.index(unknownCard)
                    state[i, 0, k] = 1 / len(otherPlayers)

        # Ja
        cardStates = [CardState.AVAILABLE, CardState.UNAVAILABLE]

        for cards, cardState in [(self.cards, CardState.AVAILABLE), (self.playedCards, CardState.UNAVAILABLE)]:
            for card in cards:
                j = cardStates.index(cardState)
                k = belot.cards.index(card)
                state[-1, j, k] = 1

        # Koja boja je adut
        trumpIndex = self.trumpSuit

        # Koji igrač je zvao
        bidderIndex = list(belot.PlayerRole).index(self.bidder)

        return state, trumpIndex, bidderIndex

    @property
    def biddingState(self) -> np.ndarray:
        suits = list(belot.Suit)
        ranks = list(belot.Rank)

        state = np.zeros(
            shape=(len(suits), len(ranks)),
            dtype=np.float32
        )

        for card in self.cards:
            i = suits.index(card.suit)
            j = ranks.index(card.rank)
            state[i][j]=1

        return state
