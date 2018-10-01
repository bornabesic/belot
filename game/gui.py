from threading import Thread
from queue import Queue, Empty
import pygame
import time
from enum import Enum, auto
from belot import Suit, Rank, Card

_screenSize = _screenWidth, _screenHeight = (800, 800)

class Colors:
    BACKGROUND = (15, 105, 25)
    WHITE = (255, 255, 255)

# Card sprites
sprites = {
    # Herc
    Card(Suit.HERC, Rank.VII):   pygame.image.load("game/assets/cards/herc-7.png"),
    Card(Suit.HERC, Rank.VIII):  pygame.image.load("game/assets/cards/herc-8.png"),
    Card(Suit.HERC, Rank.IX):    pygame.image.load("game/assets/cards/herc-9.png"),
    Card(Suit.HERC, Rank.X):     pygame.image.load("game/assets/cards/herc-10.png"),
    Card(Suit.HERC, Rank.DECKO): pygame.image.load("game/assets/cards/herc-decko.png"),
    Card(Suit.HERC, Rank.DAMA):  pygame.image.load("game/assets/cards/herc-dama.png"),
    Card(Suit.HERC, Rank.KRALJ): pygame.image.load("game/assets/cards/herc-kralj.png"),
    Card(Suit.HERC, Rank.AS):    pygame.image.load("game/assets/cards/herc-as.png"),
    # Karo
    Card(Suit.KARO, Rank.VII):   pygame.image.load("game/assets/cards/karo-7.png"),
    Card(Suit.KARO, Rank.VIII):  pygame.image.load("game/assets/cards/karo-8.png"),
    Card(Suit.KARO, Rank.IX):    pygame.image.load("game/assets/cards/karo-9.png"),
    Card(Suit.KARO, Rank.X):     pygame.image.load("game/assets/cards/karo-10.png"),
    Card(Suit.KARO, Rank.DECKO): pygame.image.load("game/assets/cards/karo-decko.png"),
    Card(Suit.KARO, Rank.DAMA):  pygame.image.load("game/assets/cards/karo-dama.png"),
    Card(Suit.KARO, Rank.KRALJ): pygame.image.load("game/assets/cards/karo-kralj.png"),
    Card(Suit.KARO, Rank.AS):    pygame.image.load("game/assets/cards/karo-as.png"),
    # Pik
    Card(Suit.PIK, Rank.VII):   pygame.image.load("game/assets/cards/pik-7.png"),
    Card(Suit.PIK, Rank.VIII):  pygame.image.load("game/assets/cards/pik-8.png"),
    Card(Suit.PIK, Rank.IX):    pygame.image.load("game/assets/cards/pik-9.png"),
    Card(Suit.PIK, Rank.X):     pygame.image.load("game/assets/cards/pik-10.png"),
    Card(Suit.PIK, Rank.DECKO): pygame.image.load("game/assets/cards/pik-decko.png"),
    Card(Suit.PIK, Rank.DAMA):  pygame.image.load("game/assets/cards/pik-dama.png"),
    Card(Suit.PIK, Rank.KRALJ): pygame.image.load("game/assets/cards/pik-kralj.png"),
    Card(Suit.PIK, Rank.AS):    pygame.image.load("game/assets/cards/pik-as.png"),
    # Tref
    Card(Suit.TREF, Rank.VII):   pygame.image.load("game/assets/cards/tref-7.png"),
    Card(Suit.TREF, Rank.VIII):  pygame.image.load("game/assets/cards/tref-8.png"),
    Card(Suit.TREF, Rank.IX):    pygame.image.load("game/assets/cards/tref-9.png"),
    Card(Suit.TREF, Rank.X):     pygame.image.load("game/assets/cards/tref-10.png"),
    Card(Suit.TREF, Rank.DECKO): pygame.image.load("game/assets/cards/tref-decko.png"),
    Card(Suit.TREF, Rank.DAMA):  pygame.image.load("game/assets/cards/tref-dama.png"),
    Card(Suit.TREF, Rank.KRALJ): pygame.image.load("game/assets/cards/tref-kralj.png"),
    Card(Suit.TREF, Rank.AS):    pygame.image.load("game/assets/cards/tref-as.png")
}

class GUI(Thread):

    class MessageType(Enum):
        SURFACE = auto()
        EMPTY = auto()

    def __init__(self):
        Thread.__init__(self)

        pygame.init()
        pygame.font.init()

        self.queue = Queue()
        self.screen = pygame.display.set_mode(_screenSize)
        pygame.display.set_caption("Belot")
        self.screen.fill(Colors.BACKGROUND)

    def clear(self):
        self.queue.put((GUI.MessageType.EMPTY,))

    # Render cards
    def cardLeft(self, cardImage):
        imageWidth, imageHeight = cardImage.get_size()
        x = _screenWidth // 4 - imageWidth // 2
        y = _screenHeight // 2 - imageHeight // 2
        self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y)))

    def cardDown(self, cardImage):
        imageWidth, imageHeight = cardImage.get_size()
        x = _screenWidth // 2 - imageWidth // 2
        y = (_screenHeight * 3) // 4 - imageHeight // 2
        self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y)))

    def cardRight(self, cardImage):
        imageWidth, imageHeight = cardImage.get_size()
        x = (_screenWidth * 3) // 4 - imageWidth // 2
        y = _screenHeight // 2 - imageHeight // 2
        self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y)))

    def cardUp(self, cardImage):
        imageWidth, imageHeight = cardImage.get_size()
        x = _screenWidth // 2 - imageWidth // 2
        y = _screenHeight // 4 - imageHeight // 2
        self.queue.put((GUI.MessageType.SURFACE, cardImage, (x, y)))

    # Render names
    def nameLeft(self, name):
        nameFont = pygame.font.SysFont("Comic Sans MS", 30)
        nameSurface = nameFont.render(name, False, Colors.WHITE)
        nameSurface = pygame.transform.rotate(nameSurface, 90)
        surface_width, surface_height = nameSurface.get_size()
        x = 10
        y = _screenHeight // 2 - surface_height // 2
        self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

    def nameDown(self, name):
        nameFont = pygame.font.SysFont("Comic Sans MS", 30)
        nameSurface = nameFont.render(name, False, Colors.WHITE)
        surface_width, surface_height = nameSurface.get_size()
        x = _screenWidth // 2 - surface_width // 2
        y = _screenHeight - surface_height - 10
        self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

    def nameRight(self, name):
        nameFont = pygame.font.SysFont("Comic Sans MS", 30)
        nameSurface = nameFont.render(name, False, Colors.WHITE)
        nameSurface = pygame.transform.rotate(nameSurface, -90)
        surface_width, surface_height = nameSurface.get_size()
        x = _screenWidth - surface_width - 10
        y = _screenHeight // 2 - surface_height // 2
        self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

    def nameUp(self, name):
        nameFont = pygame.font.SysFont("Comic Sans MS", 30)
        nameSurface = nameFont.render(name, False, Colors.WHITE)
        surface_width, surface_height = nameSurface.get_size()
        x = _screenWidth // 2 - surface_width // 2
        y = 10
        self.queue.put((GUI.MessageType.SURFACE, nameSurface, (x, y)))

    def run(self):
        while True:
            # Events
            close = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close = True
                    break
            if close:
                break

            # Message queue
            try:
                item = self.queue.get(block = False)
                messageType = item[0]
                # Draw a surface
                if messageType is GUI.MessageType.SURFACE:
                    surface = item[1]
                    x, y = item[2]
                    self.screen.blit(surface, (x, y))
                # Clear the screen
                elif messageType is GUI.MessageType.EMPTY:
                    self.screen.fill(Colors.BACKGROUND)
            except Empty:
                pass

            pygame.display.flip()

        pygame.display.quit()

if __name__ == "__main__":
    gui = GUI()
    gui.start()

    gui.nameDown("Borna")
    gui.nameUp("Mislav")

    gui.nameLeft("Luka")
    gui.nameRight("Lovro")

    for card in sprites:
        if not gui.is_alive():
            break
        suit, rank = card
        if suit is Suit.HERC:
            gui.cardLeft(sprites[card])
        elif suit is Suit.KARO:
            gui.cardDown(sprites[card])
        elif suit is Suit.PIK:
            gui.cardRight(sprites[card])
        elif suit is Suit.TREF:
            gui.cardUp(sprites[card])
        time.sleep(1)

    gui.clear()
