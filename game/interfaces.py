from abc import ABCMeta, abstractmethod
import game.belot as belot

class IPlayer(metaclass=ABCMeta):
    '''
    Apstraktni razred koji predstavlja sučelje jednog igrača (agenta) prema igri
    '''

    def __init__(self, name, human=False):
        self.name=name
        self.human=human
        self.initialize()

    def __eq__(self, other):
        if other==None:
            return False

        return self.name==other.name

    def __hash__(self):
        return self.name.__hash__()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def updateCards(self, cards):
        '''
        Metoda koja uručuje karte igraču.
        '''

        # self.cards = sorted(cards)
        self.cards = cards
        self.notifyCards()

    def declare(self):
        '''
        Metoda koja vraća dvije liste:
        listu (list) skupova (set) karata koji čine zvanja te
        listu (list) vrijednosti (int) svakog pojedinog zvanja.
        '''

        declarationCards=belot.declarationCards
        declarationValues=belot.declarationValues

        foundCards=[]
        foundValues=[]

        for i in range(len(declarationCards)):
            setOfCards=declarationCards[i]
            setValue=declarationValues[i]
            if setOfCards.issubset(self.cards):
                foundCards.append(setOfCards)
                foundValues.append(setValue)

        uniqueDeclarations=[]
        uniqueValues=[]
        for i in range(len(foundCards)):
            subset=False
            for j in range(len(foundCards)):
                if i!=j:
                    if foundCards[i].issubset(foundCards[j]):
                        subset=True
                        break
            if not subset:
                uniqueDeclarations.append(foundCards[i])
                uniqueValues.append(foundValues[i])

        return uniqueDeclarations, uniqueValues

    @abstractmethod
    def initialize(self):
        '''
        Metoda koja služi za inicijalizaciju svih potrebnih atributa.
        '''
        pass

    @abstractmethod
    def notifyCards(self):
        '''
        Metoda koja dojavljuje da su karte podijeljene i da se nalaze
        u self.cards.
        '''
        pass

    @abstractmethod
    def notifyTrumpSuit(self, trumpSuit, bidder):
        '''
        Metoda koja dojavljuje koja boja je zvana kao adut (trumpSuit) te koji igrač ju je zvao (bidder).
        trumpSuit je jedna od vrijednosti iz belot.suits.
        bidder je jedna od vrijednosti belot.PlayerRole:
        - belot.PlayerRole.ME -> ja
        - belot.PlayerRole.LEFT_OPPONENT -> protivnik s lijeva
        - belot.PlayerRole.RIGHT_OPPONENT -> protivnik s desna
        - belot.PlayerRole.TEAMMATE -> suigrač
        '''
        pass

    @abstractmethod
    def notifyDeclarations(self, declarations):
        '''
        Metoda dojavljuje zvanja svih igrača.
        'declarations' je rječnik (dict) kojemu je ključ igrač,
        a vrijednost lista (list) skupova (set) karata koje čine zvanje.
        Ključevi:
        - belot.PlayerRole.ME -> ja
        - belot.PlayerRole.LEFT_OPPONENT -> protivnik s lijeva
        - belot.PlayerRole.RIGHT_OPPONENT -> protivnik s desna
        - belot.PlayerRole.TEAMMATE -> suigrač
        '''
        pass

    @abstractmethod
    def notifyTrick(self, cards, value):
        '''
        Metoda dojavljuje kraj štiha.
        'cards' su karte sadržane u štihu, a 'value' je vrijednost štiha.
        Ako je value > 0 štih je dobiven, a ako je value < 0 štih je izgubljen.
        '''
        pass

    @abstractmethod
    def notifyHand(self, pointsUs, pointsThem):
        '''
        Metoda dojavljuje kraj dijeljenja.
        'pointsUs' su zarađeni bodovi vlastite ekipe, a 'pointsThem' su zarađeni bodovi protivničke ekipe.
        '''
        pass

    @abstractmethod
    def notifyGame(self, pointsUs, pointsThem):
        '''
        Metoda dojavljuje kraj igre.
        'pointsUs' su zarađeni bodovi vlastite ekipe, a 'pointsThem' su zarađeni bodovi protivničke ekipe.
        '''
        pass

    @abstractmethod
    def notifyBela(self, player, card):
        '''
        Metoda dojavljuje kada neki igrač zove belu.
        'player' je igrač koji je zvao belu, a 'card' je karta koja je bačena.
        '''
        pass

    @abstractmethod
    def bid(self, must):
        '''
        Metoda za zvanje aduta. Mora vratiti jednu od vrijednosti iz liste belot.suits ili
        None ukoliko igrač ne želi zvati.
        Ako je 'must' postavljen na True, igrač mora zvati (na mus).
        '''
        return None

    @abstractmethod
    def playCard(self, table, legalCards):
        '''
        Metoda za odigravanje karte. Mora vratiti jednu od vrijednosti iz legalCards.
        legalCards predstavlja podskup karata u ruci koji igrač može odigrati u danom trenutku.
        'table' je riječnik (dict) koji predstavlja stanje karata na stolu. Ključ je
        igrač, a vrijednost je karta koju je taj igrač bacio.
        Ključevi:
        - belot.PlayerRole.LEFT_OPPONENT -> protivnik s lijeva
        - belot.PlayerRole.RIGHT_OPPONENT -> protivnik s desna
        - belot.PlayerRole.TEAMMATE -> suigrač
        '''
        return None

    @abstractmethod
    def declareBela(self, table):
        '''
        Metoda koja određuje hoće li igrač zvati belu ili ne. Mora vratiti True ili False.
        'table' je riječnik (dict) koji predstavlja stanje karata na stolu. Ključ je
        igrač, a vrijednost je karta koju je taj igrač bacio.
        Ključevi:
        - belot.PlayerRole.LEFT_OPPONENT -> protivnik s lijeva
        - belot.PlayerRole.RIGHT_OPPONENT -> protivnik s desna
        - belot.PlayerRole.TEAMMATE -> suigrač
        '''
        return False
