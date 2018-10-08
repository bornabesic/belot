
import unittest

from context import game

from game import aces, kings, queens, tens
from game import Card, Rank, Suit
from game import cards, dealCards

class Test(unittest.TestCase):

    def test_cards(self):
        # Aševi
        self.assertEqual(
            aces,
            set([
                Card(Suit.KARO, Rank.AS),
                Card(Suit.PIK,  Rank.AS),
                Card(Suit.TREF, Rank.AS),
                Card(Suit.HERC, Rank.AS)
            ])
        )

        # Kraljevi
        self.assertEqual(
            kings,
            set([
                Card(Suit.KARO, Rank.KRALJ),
                Card(Suit.PIK,  Rank.KRALJ),
                Card(Suit.TREF, Rank.KRALJ),
                Card(Suit.HERC, Rank.KRALJ)
            ])
        )

        # Dame
        self.assertEqual(
            queens,
            set([
                Card(Suit.KARO, Rank.DAMA),
                Card(Suit.PIK,  Rank.DAMA),
                Card(Suit.TREF, Rank.DAMA),
                Card(Suit.HERC, Rank.DAMA)
            ])
        )

        # Desetke
        self.assertEqual(
            tens,
            set([
                Card(Suit.KARO, Rank.X),
                Card(Suit.PIK,  Rank.X),
                Card(Suit.TREF, Rank.X),
                Card(Suit.HERC, Rank.X)
            ])
        )

    def test_dealCards(self):
        cards1, cards2, cards3, cards4 = dealCards()
        self.assertEqual(
            set(cards),
            set(cards1 + cards2 + cards3 + cards4)
        )


if __name__ == "__main__":
    unittest.main(verbosity = 2)
