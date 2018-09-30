from threading import Thread
from queue import Queue
import pygame
import time
from enum import Enum, auto
from belot import Suit, Rank, Card

_background = (15, 105, 25)
_screen_size = _screen_width, _screen_height = (800, 800)

# Card sprites
sprites = {
    # Herc
    Card(Suit.HERC, Rank.VII): pygame.image.load("game/assets/cards/herc-7.png"),
    Card(Suit.HERC, Rank.VIII): pygame.image.load("game/assets/cards/herc-8.png"),
    Card(Suit.HERC, Rank.IX): pygame.image.load("game/assets/cards/herc-9.png"),
    Card(Suit.HERC, Rank.X): pygame.image.load("game/assets/cards/herc-10.png"),
    Card(Suit.HERC, Rank.DECKO): pygame.image.load("game/assets/cards/herc-decko.png"),
    Card(Suit.HERC, Rank.DAMA): pygame.image.load("game/assets/cards/herc-dama.png"),
    Card(Suit.HERC, Rank.KRALJ): pygame.image.load("game/assets/cards/herc-kralj.png"),
    Card(Suit.HERC, Rank.AS): pygame.image.load("game/assets/cards/herc-as.png"),
    # Karo
    Card(Suit.KARO, Rank.VII): pygame.image.load("game/assets/cards/karo-7.png"),
    Card(Suit.KARO, Rank.VIII): pygame.image.load("game/assets/cards/karo-8.png"),
    Card(Suit.KARO, Rank.IX): pygame.image.load("game/assets/cards/karo-9.png"),
    Card(Suit.KARO, Rank.X): pygame.image.load("game/assets/cards/karo-10.png"),
    Card(Suit.KARO, Rank.DECKO): pygame.image.load("game/assets/cards/karo-decko.png"),
    Card(Suit.KARO, Rank.DAMA): pygame.image.load("game/assets/cards/karo-dama.png"),
    Card(Suit.KARO, Rank.KRALJ): pygame.image.load("game/assets/cards/karo-kralj.png"),
    Card(Suit.KARO, Rank.AS): pygame.image.load("game/assets/cards/karo-as.png"),
    # Pik
    Card(Suit.PIK, Rank.VII): pygame.image.load("game/assets/cards/pik-7.png"),
    Card(Suit.PIK, Rank.VIII): pygame.image.load("game/assets/cards/pik-8.png"),
    Card(Suit.PIK, Rank.IX): pygame.image.load("game/assets/cards/pik-9.png"),
    Card(Suit.PIK, Rank.X): pygame.image.load("game/assets/cards/pik-10.png"),
    Card(Suit.PIK, Rank.DECKO): pygame.image.load("game/assets/cards/pik-decko.png"),
    Card(Suit.PIK, Rank.DAMA): pygame.image.load("game/assets/cards/pik-dama.png"),
    Card(Suit.PIK, Rank.KRALJ): pygame.image.load("game/assets/cards/pik-kralj.png"),
    Card(Suit.PIK, Rank.AS): pygame.image.load("game/assets/cards/pik-as.png"),
    # Tref
    Card(Suit.TREF, Rank.VII): pygame.image.load("game/assets/cards/tref-7.png"),
    Card(Suit.TREF, Rank.VIII): pygame.image.load("game/assets/cards/tref-8.png"),
    Card(Suit.TREF, Rank.IX): pygame.image.load("game/assets/cards/tref-9.png"),
    Card(Suit.TREF, Rank.X): pygame.image.load("game/assets/cards/tref-10.png"),
    Card(Suit.TREF, Rank.DECKO): pygame.image.load("game/assets/cards/tref-decko.png"),
    Card(Suit.TREF, Rank.DAMA): pygame.image.load("game/assets/cards/tref-dama.png"),
    Card(Suit.TREF, Rank.KRALJ): pygame.image.load("game/assets/cards/tref-kralj.png"),
    Card(Suit.TREF, Rank.AS): pygame.image.load("game/assets/cards/tref-as.png")
}

class GUI(Thread):

    class MessageType(Enum):
        SHOW_LEFT = auto()
        SHOW_DOWN = auto()
        SHOW_RIGHT = auto()
        SHOW_UP = auto()
        EMPTY = auto()

    def empty(self):
        self.queue.put((GUI.MessageType.EMPTY,))

    def showLeft(self, cardImage):
        self.queue.put((GUI.MessageType.SHOW_LEFT, cardImage))

    def showDown(self, cardImage):
        self.queue.put((GUI.MessageType.SHOW_DOWN, cardImage))

    def showRight(self, cardImage):
        self.queue.put((GUI.MessageType.SHOW_RIGHT, cardImage))

    def showUp(self, cardImage):
        self.queue.put((GUI.MessageType.SHOW_UP, cardImage))

    def run(self):
        self.queue = Queue()

        pygame.init()
        self.screen = pygame.display.set_mode(_screen_size)
        self.screen.fill(_background)
        while True:
            # Events
            exit = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True
                    break
            if exit:
                break

            # Message queue
            item = self.queue.get()
            messageType = item[0]
            if messageType in (
                GUI.MessageType.SHOW_LEFT,
                GUI.MessageType.SHOW_DOWN,
                GUI.MessageType.SHOW_RIGHT,
                GUI.MessageType.SHOW_UP
            ):
                position, cardImage = item
                image_width, image_height = cardImage.get_size()

                if position is GUI.MessageType.SHOW_LEFT:
                    x = _screen_width // 4 - image_width // 2
                    y = _screen_height // 2 - image_height // 2
                elif position is GUI.MessageType.SHOW_DOWN:
                    x = _screen_width // 2 - image_width // 2
                    y = (_screen_height * 3) // 4 - image_height // 2
                elif position is GUI.MessageType.SHOW_RIGHT:
                    x = (_screen_width * 3) // 4 - image_width // 2
                    y = _screen_height // 2 - image_height // 2
                elif position is GUI.MessageType.SHOW_UP:
                    x = _screen_width // 2 - image_width // 2
                    y = _screen_height // 4 - image_height // 2

                self.screen.blit(cardImage, (x, y))
            elif messageType is GUI.MessageType.EMPTY:
                self.screen.fill(_background)

            pygame.display.flip()

if __name__ == "__main__":
    gui = GUI()
    gui.start()

    for card in sprites:
        suit, rank = card
        if suit is Suit.HERC:
            gui.showLeft(sprites[card])
        elif suit is Suit.KARO:
            gui.showDown(sprites[card])
        elif suit is Suit.PIK:
            gui.showRight(sprites[card])
        elif suit is Suit.TREF:
            gui.showUp(sprites[card])
        time.sleep(1)

    gui.empty()
