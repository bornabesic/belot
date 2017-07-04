#!/usr/bin/python3

from model import *
from players.PlayerRandom import PlayerRandom
from players.PlayerKeyboard import PlayerKeyboard

playerA1 = PlayerKeyboard("Borna", human=True)
playerA2 = PlayerRandom("Mislav")
pairA = Pair(playerA1, playerA2)

playerB1 = PlayerRandom("Luka")
playerB2 = PlayerRandom("Lovro")
pairB = Pair(playerB1, playerB2)

game = Game(pairA, pairB)
game.play()
