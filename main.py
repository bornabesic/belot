#!/usr/bin/python3

from model import *
from players.PlayerRandom import PlayerRandom
#from players.PlayerKeyboard import PlayerKeyboard
from players.PlayerRL import PlayerRL

import stdout

# reinforcement learning pair
# TODO save & load policy networks
# TODO share policy networks across all RL players
playerA1 = PlayerRL("Borna")
playerA2 = PlayerRL("Mislav")
pairA = Pair(playerA1, playerA2)

# random pair
playerB1 = PlayerRandom("Luka")
playerB2 = PlayerRandom("Lovro")
pairB = Pair(playerB1, playerB2)

stdout.disable()

games = 1000
wins=list()
for i in range(games):
    game = Game(pairA, pairB)
    pointsA, pointsB = game.play()
    wins.append("A" if pointsA>pointsB else "B")

last=50
winningPercentage=wins[-last:].count("A")/last*100

stdout.enable()
print("[RL] {} - postotak pobjeda (u zadnjih {} igara): {}%".format(pairA, last, winningPercentage))
