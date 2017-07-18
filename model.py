import belot
from players.PlayerKeyboard import PlayerKeyboard


class Pair:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        self.iter=-1

    def __eq__(self, other):
        if other==None:
            return False

        return self.player1==other.player1 and self.player2==other.player2

    def __str__(self):
        return "{} i {}".format(self.player1, self.player2)

    def __repr__(self):
        return self.__str__()

    def __contains__(self, other):
        return other==self.player1 or other==self.player2

    def __iter__(self):
        self.iter = -1
        return self

    def __next__(self):
        self.iter+=1

        if self.iter==0:
            return self.player1
        elif self.iter==1:
            return self.player2
        elif self.iter>=2:
            raise StopIteration


class Hand:
    def __init__(self, game):
        self.game = game

        # štihovi u obliku tuple-a (karta1, karta2, karta3, karta4)
        self.tricksA = list()
        self.tricksB = list()

        self.pointsA = 0 # skupljeni bodovi para A
        self.pointsB = 0 # skupljeni bodovi para B

        self.declarations = dict()

        # preslikavanje igrača u indeks
        self.sittingIndices = dict()
        for i, player in enumerate(game.sitting):
            self.sittingIndices[player]=i

        # tablica za gradnju lokalnog 'table' stanja koje se predaje agentu
        self.mapTableToLocal = dict()
        for player in self.game.sitting:
            self.mapTableToLocal[player]=dict()
            self.setCurrentPlayer(player)
            self.mapTableToLocal[player][player]=belot.PlayerRole.ME
            self.mapTableToLocal[player][self.whoWasPreviousPlayer()]=belot.PlayerRole.LEFT_OPPONENT
            self.mapTableToLocal[player][self.whoIsNextPlayer()]=belot.PlayerRole.RIGHT_OPPONENT
            self.mapTableToLocal[player][self.getTeammate(player)]=belot.PlayerRole.TEAMMATE

        self.currentPlayer=None
        self.resetToFirstPlayer()

    def resetToFirstPlayer(self):
        self.playerIndex=self.game.dealerIndex
        self.nextPlayer()

    def setCurrentPlayer(self, player):
        self.playerIndex=self.sittingIndices[player]
        self.currentPlayer=player

    def previousIndex(self):
        return (self.playerIndex-1)%4

    def whoWasPreviousPlayer(self):
        return self.game.sitting[self.previousIndex()]

    def nextIndex(self):
        return (self.playerIndex+1)%4

    def whoIsNextPlayer(self):
        return self.game.sitting[self.nextIndex()]

    def nextPlayer(self):
        self.currentPlayer=self.whoIsNextPlayer()
        self.playerIndex=self.nextIndex()

    def getTeammate(self, player):
        if player in self.game.pairA:
            for p in self.game.pairA:
                if p!=player:
                    return p
        elif player in self.game.pairB:
            for p in self.game.pairB:
                if p!=player:
                    return p

    def updatePlayersCards(self, cards1, cards2, cards3, cards4):
        self.game.sitting[0].updateCards(cards1)
        self.game.sitting[1].updateCards(cards2)
        self.game.sitting[2].updateCards(cards3)
        self.game.sitting[3].updateCards(cards4)

    def play(self):
        print("Karte dijeli {}".format(self.game.sitting[self.game.dealerIndex]))
        pairA = self.game.pairA
        pairB = self.game.pairB
        playerA1 = pairA.player1
        playerA2 = pairA.player2
        playerB1 = pairB.player1
        playerB2 = pairB.player2
        cards1, cards2, cards3, cards4 = belot.dealCards()

        # uruči igračima prvih 6 karata za zvanje aduta
        self.updatePlayersCards(cards1[:-2], cards2[:-2], cards3[:-2], cards4[:-2])

        # zvanje aduta
        biddingPair=None
        while True:
            print("---------- {} ----------".format(self.currentPlayer))
            must = (self.playerIndex == self.game.dealerIndex)
            suit = self.currentPlayer.bid(must=must)
            if suit in belot.suits:
                print("{} zove {}".format(self.currentPlayer, suit))
                if self.currentPlayer in pairA: biddingPair=pairA
                elif self.currentPlayer in pairB: biddingPair=pairB
                trumpSuit = suit
                bidder = self.currentPlayer
                break
            else:
                if must: raise ValueError("{} nije zvao na mus!".format(self.currentPlayer))

                print(self.currentPlayer, "kaže dalje")
            self.nextPlayer()


        for player in self.game.sitting:
            localBidder = self.mapTableToLocal[player][bidder]
            player.notifyTrumpSuit(trumpSuit, localBidder)

        self.resetToFirstPlayer() # igra prvi igrač desno od djelitelja

        # uruči igračima sve karte
        self.updatePlayersCards(cards1, cards2, cards3, cards4)

        # zvanja
        declaredCardsA1, declaredValuesA1 = playerA1.declare()
        declaredCardsA2, declaredValuesA2 = playerA2.declare()
        maxDeclaredA1 = max(declaredValuesA1) if len(declaredValuesA1)!=0 else 0
        maxDeclaredA2 = max(declaredValuesA2) if len(declaredValuesA2)!=0 else 0
        maxDeclaredA = max([maxDeclaredA1, maxDeclaredA2])

        declaredCardsB1, declaredValuesB1 = playerB1.declare()
        declaredCardsB2, declaredValuesB2 = playerB2.declare()
        maxDeclaredB1 = max(declaredValuesB1) if len(declaredValuesB1)!=0 else 0
        maxDeclaredB2 = max(declaredValuesB2) if len(declaredValuesB2)!=0 else 0
        maxDeclaredB = max([maxDeclaredB1, maxDeclaredB2])

        declareA=False
        declareB=False

        print("Zvanja:")
        if maxDeclaredA==0 and maxDeclaredB==0:
            print("\tNema zvanja")
        elif maxDeclaredA>maxDeclaredB:
            declareA=True
        elif maxDeclaredA<maxDeclaredB:
            declareB=True
        else:
            nextPlayer = self.whoIsNextPlayer()
            if nextPlayer in pairA:
                declareA=True
            elif nextPlayer in pairB:
                declareB=True

        handValue = belot.handValue

        if declareA:
            declarationsTotalA=sum(declaredValuesA1+declaredValuesA2)
            handValue+=declarationsTotalA
            self.pointsA+=declarationsTotalA
            if len(declaredCardsA1)!=0:
                self.declarations[playerA1]=declaredCardsA1
                print("\t{}: {}".format(playerA1, declaredCardsA1))
            if len(declaredCardsA2)!=0:
                self.declarations[playerA2]=declaredCardsA2
                print("\t{}: {}".format(playerA2, declaredCardsA2))
        elif declareB:
            declarationsTotalB=sum(declaredValuesB1+declaredValuesB2)
            handValue+=declarationsTotalB
            self.pointsB+=declarationsTotalB
            if len(declaredCardsB1)!=0:
                self.declarations[playerB1]=declaredCardsB1
                print("\t{}: {}".format(playerB1, declaredCardsB1))
            if len(declaredCardsB2)!=0:
                self.declarations[playerB2]=declaredCardsB2
                print("\t{}: {}".format(playerB2, declaredCardsB2))

        for player in self.game.sitting:
            localDeclarations=dict()
            for playerKey in self.declarations:
                declaredCards = self.declarations[playerKey]
                localKey = self.mapTableToLocal[player][playerKey]
                localDeclarations[localKey]=declaredCards
            player.notifyDeclarations(localDeclarations)

        # započni igru
        print()
        while len(self.tricksA)+len(self.tricksB)<8:
            if self.game.humanPlayer: input()

            trick=list() # štih
            table=dict() # karte na stolu
            lastTrick = (len(self.tricksA)+len(self.tricksB) == 7)
            dominantSuit=None

            while len(table)<4:
                print("---------- {} ----------".format(self.currentPlayer))

                localTable=dict()
                for player in table:
                    card = table[player]
                    localKey = self.mapTableToLocal[self.currentPlayer][player]
                    localTable[localKey]=card

                playerLegalCards = belot.getLegalCards(self.currentPlayer.cards, table, dominantSuit, trumpSuit)
                card = self.currentPlayer.playCard(localTable, playerLegalCards)
                if card not in playerLegalCards:
                    raise ValueError("{} je bacio kartu koju ne može baciti!".format(self.currentPlayer))

                self.currentPlayer.cards.remove(card)

                suit, rank = card.split(belot.separator)
                if suit==trumpSuit:
                    queenAndKing = (rank=="DAMA" and belot.card(suit, "KRALJ") in self.currentPlayer.cards)
                    kingAndQueen = (rank=="KRALJ" and belot.card(suit, "DAMA") in self.currentPlayer.cards)
                    if (queenAndKing or kingAndQueen) and self.currentPlayer.declareBela(localTable):
                        print("BELA!")
                        handValue+=belot.belaValue
                        if self.currentPlayer in pairA:
                            self.pointsA+=belot.belaValue
                        elif self.currentPlayer in pairB:
                            self.pointsB+=belot.belaValue

                        for player in self.game.sitting:
                            if player!=self.currentPlayer:
                                player.notifyBela(self.currentPlayer, card) 
                print(suit, rank)

                if dominantSuit==None:
                    dominantSuit = suit

                table[self.currentPlayer]=card
                trick.append(card)

                self.nextPlayer()

            trickWinner = belot.trickWinner(table, dominantSuit, trumpSuit)
            trickValue = belot.trickValue(table, trumpSuit, lastTrick)
            print("> Štih ({}) kupi {}".format(trickValue, trickWinner))

            if trickWinner in pairA:
                self.tricksA.append(tuple(trick))
                self.pointsA+=trickValue
                for playerA in pairA:
                    playerA.notifyTrick(trick, trickValue)
                for playerB in pairB:
                    playerB.notifyTrick(trick, -trickValue)

            elif trickWinner in pairB:
                self.tricksB.append(tuple(trick))
                self.pointsB+=trickValue
                for playerA in pairA:
                    playerA.notifyTrick(trick, -trickValue)
                for playerB in pairB:
                    playerB.notifyTrick(trick, trickValue)

            self.setCurrentPlayer(trickWinner)

        print("Bodovi u dijeljenju:")
        print("\t{}: {}".format(pairA, self.pointsA))
        print("\t{}: {}".format(pairB, self.pointsB))

        if biddingPair==pairA and self.pointsA<handValue//2+1:
                print("{} nisu prošli!".format(pairA))
                self.pointsB+=self.pointsA
                self.pointsA=0
        elif biddingPair==pairB and self.pointsB<handValue//2+1:
                print("{} nisu prošli!".format(pairB))
                self.pointsA+=self.pointsB
                self.pointsB=0

        return self.pointsA, self.pointsB


class Game:
    '''
    Razred koji predstavlja igru dva protivnička para do 1001 bod
    '''

    def __init__(self, pairA, pairB):
        self.pairA = pairA
        self.pairB = pairB

        # ukupni bodovi kroz sva dijeljenja
        self.pointsA = 0
        self.pointsB = 0

        self.sitting = [pairA.player1, pairB.player1, pairA.player2, pairB.player2]
        self.dealerIndex = 0

        self.humanPlayer=False
        # osiguraj da svi igrači imaju različita imena
        for i in range(len(self.sitting)):
            player = self.sitting[i]

            if player.human:
                self.humanPlayer=True

            if player in self.sitting[i+1:]:
                raise ValueError("Ne mogu postojati dva igrača s istim imenom ({})!".format(player))

    def nextDealer(self):
        self.dealerIndex=(self.dealerIndex+1)%4

    def play(self):
        winA=False
        winB=False

        print("PAR A:", self.pairA)
        print("PAR B:", self.pairB)

        while True:
            if self.humanPlayer: input()
            print("================= DIJELJENJE =================")
            hand = Hand(self)
            newPointsA, newPointsB = hand.play()

            for playerA in self.pairA:
                playerA.notifyHand(newPointsA, newPointsB)
            for playerB in self.pairB:
                playerB.notifyHand(newPointsB, newPointsA)

            self.nextDealer()

            self.pointsA+=newPointsA
            self.pointsB+=newPointsB
            print("Ukupni bodovi:")
            print("\t{}: {}".format(self.pairA, self.pointsA))
            print("\t{}: {}".format(self.pairB, self.pointsB))

            if self.pointsA>=1001 and self.pointsB>=1001:
                if self.pointsA>self.pointsB:
                    winA=True
                elif self.pointsA<self.pointsB:
                    winB=True
                break
            elif self.pointsA>=1001:
                winA=True
                break
            elif self.pointsB>=1001:
                winB=True
                break

        if winA:
            print("{} su pobjedili!".format(self.pairA))
        elif winB:
            print("{} su pobjedili!".format(self.pairB))

        return self.pointsA, self.pointsB
