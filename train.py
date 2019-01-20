#!/usr/bin/python3

from game.play import Pair, Game
from players.PlayerRandom import PlayerRandom
from players.PlayerKeyboard import PlayerKeyboard
from players.PlayerRL import PlayerRL

import stdout

# RL par
# TODO save & load policy networks
# TODO share policy networks across all RL players
playerA1 = PlayerRL("Borna")
playerA2 = PlayerRL("Mislav")
pairA = Pair(playerA1, playerA2)

# Par koji igra nasumično
playerB1 = PlayerRandom("Luka")
playerB2 = PlayerRandom("Lovro")
pairB = Pair(playerB1, playerB2)

# Treniraj
stdout.disable()

games = 10000
last = 100
wins = list()

for i in range(games):
    game = Game(pairA, pairB)
    pointsA, pointsB = game.play()
    wins.append("A" if pointsA > pointsB else "B")

    if i > 0 and i % last == 0:
        winsA = wins[-last:].count("A")
        winningPercentage = winsA / last * 100
        # if winningPercentage >= 90:
        #     break
        stdout.enable()
        print("[RL] {} - postotak pobjeda (u zadnjih {} igara): {}% ({} / {})".format(pairA, last, winningPercentage, winsA, last))
        stdout.disable()

# Igraj
stdout.enable()

playerA1.eval()
playerA2.eval()

playerMe = PlayerKeyboard("Ja")
playerFriend = PlayerRandom("On")

game = Game(
    Pair(playerMe, playerFriend),
    pairA
)

pointsA, pointsB = game.play()
