import game.belot as belot
from game.interfaces import IPlayer

from enum import Enum
from players.PlayerRL.BiddingPolicyNetwork import BiddingPolicyNetwork
from players.PlayerRL.PlayingPolicyNetwork import PlayingPolicyNetwork

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
        self.playingActions = list()
        self.playingStates = list()
        self.playingRewards = list()

        self.playingDiscount = 0.95
        self.playingReward = 0
        self.trickNumber = 0

        self.playingNetwork = PlayingPolicyNetwork(name=self.name)
        # za neuronsku mrežu koja određuje zvanje aduta
        self.biddingActions = list()
        self.biddingStates = list()
        self.biddingRewards = list()

        self.biddingNetwork = BiddingPolicyNetwork(name=self.name)

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
        playingState = self.playingState()
        self.playingStates.append(playingState)

        probabilities, maxIndex = self.playingNetwork.feed(np.array([playingState]), np.array([legalCards]))

        if self.train == False: # igraj za pravo
            index = maxIndex
        else:
            sampledActionProbability = np.random.choice(probabilities, p=probabilities)
            index = np.argmax(probabilities == sampledActionProbability)
        cardToPlay = belot.cards[index]
        self.playingActions.append(index)

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
        biddingState = self.biddingState()
        self.biddingStates.append(biddingState)

        options = list(belot.Suit) + [None]
        probabilities, maxIndex = self.biddingNetwork.feed(biddingState, must)

        if self.train == False: # igraj za pravo
            index = maxIndex
        else:
            sampledActionProbability = np.random.choice(probabilities, p=probabilities)
            index = np.argmax(probabilities == sampledActionProbability)

        self.biddingActions.append(index)

        return options[index]

    def notifyHand(self, pointsUs, pointsThem):
        if len(self.biddingActions) == len(self.biddingRewards) + 1:
            normalizedReward = pointsUs / 81 - 1
            self.biddingRewards.append(normalizedReward)

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
        self.playingRewards.append(normalizedReward)

    def notifyGame(self, pointsUs, pointsThem):
        if self.train == False:
            # resetiraj
            self.playingActions.clear()
            self.playingStates.clear()
            self.playingRewards.clear()

            self.biddingActions.clear()
            self.biddingStates.clear()
            self.biddingRewards.clear()
            return

        # treniraj mrežu za bacanje karata
        discountedRewards = list()
        numRewards = len(self.playingRewards)
        for i in range(numRewards):
            realReward = 0

            for j in range(i, numRewards):
                reward = self.playingRewards[j]
                realReward += reward * pow(self.playingDiscount, j - i)

            k = int(len(self.biddingRewards) / len(self.playingRewards) * i)
            realReward += self.biddingRewards[k]
            discountedRewards.append(realReward)

        playingLoss = self.playingNetwork.train(
            action=np.array(self.playingActions),
            state=np.array(self.playingStates),
            reward=np.array(discountedRewards)
        )
        # print("Playing loss:", playingLoss)

        # treniraj mrežu za zvanje aduta
        if len(self.biddingStates)>0:
            biddingLoss = self.biddingNetwork.train(
                action=np.array(self.biddingActions),
                state=np.array(self.biddingStates)[0],
                reward=np.array(self.biddingRewards)
            )
            #print("Bidding loss:", biddingLoss)

        # resetiraj
        self.playingActions.clear()
        self.playingStates.clear()
        self.playingRewards.clear()

        self.biddingActions.clear()
        self.biddingStates.clear()
        self.biddingRewards.clear()

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

    def playingState(self):
        knowledge = self.knowledge
        cardStates = [
            CardState.AVAILABLE,
            CardState.TABLE,
            CardState.UNAVAILABLE
        ]

        # Stanja igrača
        teammateState = np.zeros(
            shape=(len(cardStates), len(belot.cards)), # 3 x 32 = 96
            dtype=np.float32
        )

        leftOpponentState = np.zeros(
            shape=(len(cardStates), len(belot.cards)), # 3 x 32 = 96
            dtype=np.float32
        )

        rightOpponentState = np.zeros(
            shape=(len(cardStates), len(belot.cards)), # 3 x 32 = 96
            dtype=np.float32
        )

        otherPlayersTuples = [
            (belot.PlayerRole.TEAMMATE, teammateState),
            (belot.PlayerRole.LEFT_OPPONENT, leftOpponentState),
            (belot.PlayerRole.RIGHT_OPPONENT, rightOpponentState)
        ]
        for player, playerState in otherPlayersTuples:
            for i, cardState in enumerate(cardStates):
                # Za karte koje znaš gdje su, rasporedi ih sa
                # sigurnošću
                for card in knowledge[player][cardState]:
                    j = belot.cards.index(card)
                    playerState[i][j] = 1

                # Ako ne znaš gdje je karta, uniformno rasporedi
                # vjerojatnosti po igračima kao AVAILABLE (0)
                for unknownCard in knowledge[CardState.UNKNOWN]:
                    j = belot.cards.index(unknownCard)
                    playerState[0][j] = 1 / len(otherPlayersTuples)

        # Ja
        cardStates = [CardState.AVAILABLE, CardState.UNAVAILABLE]
        meState = np.zeros(
            shape=(len(cardStates), len(belot.cards)),
            dtype=np.float32
        )

        for i, t in enumerate([(self.cards, CardState.AVAILABLE), (self.playedCards, CardState.UNAVAILABLE)]):
            cards, state = t
            for card in cards:
                meState[i][belot.cards.index(card)] = 1


        # Koja boja je adut
        trumpState = np.zeros(
            shape=(1, len(belot.Suit)),
            dtype=np.float32
        )
        trumpState[0][self.trumpSuit] = 1

        # Koji igrač je zvao
        bidderState = np.zeros(
            shape=(1, len(belot.PlayerRole)),
            dtype=np.float32
        )
        bidderState[0][list(belot.PlayerRole).index(self.bidder)]=1

        # Spoji sve
        playingInput = np.concatenate([
            meState.flatten(),
            rightOpponentState.flatten(),
            teammateState.flatten(),
            leftOpponentState.flatten(),
            trumpState.flatten(),
            bidderState.flatten()
        ], axis=0)

        return playingInput

    def biddingState(self):
        biddingInput = np.zeros(
            shape=(1, len(belot.cards)),
            dtype=np.float32
        )
        for card in self.cards:
            j = belot.cards.index(card)
            biddingInput[0][j]=1

        return biddingInput
