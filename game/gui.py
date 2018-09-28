from threading import Thread
import pygame
pygame.init()

_background = (15, 105, 25)
_screen_size = (800, 600)

class GUI(Thread):

    def run(self):
        screen = pygame.display.set_mode(_screen_size)
        while True:
            exit = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True
                    break
            if exit:
                break

            screen.fill(_background)
            pygame.display.flip()

if __name__ == "__main__":
    gui = GUI()
    gui.start()

    i = 0
    while True:
        i += 1
        print(i)
