from dataclasses import FrozenInstanceError

import pytest

from snapszer.cards import DECK, Card, Rank, Suit


class TestSuit:
    def test_all_suits_are_present(self):
        assert list(Suit) == [
            "PIROS",
            "ZOLD",
            "TOK",
            "MAKK",
        ]


class TestRank:
    def test_point_values(self):
        assert {rank: rank.value for rank in Rank} == {
            Rank.IX: 0,
            Rank.ALSO: 2,
            Rank.FELSO: 3,
            Rank.KIRALY: 4,
            Rank.X: 10,
            Rank.ASZ: 11,
        }


class TestCard:
    def test_is_a_frozen_value_object(self):
        card_a = Card(Suit.PIROS, Rank.ASZ)
        card_b = Card(Suit.PIROS, Rank.ASZ)
        assert card_a is not card_b
        assert card_a == card_b
        assert {card_a, card_b} == {card_a}
        assert card_a != Card(Suit.MAKK, Rank.ASZ)
        assert card_a != Card(Suit.PIROS, Rank.X)
        with pytest.raises(FrozenInstanceError):
            card_a.suit = Suit.ZOLD

    def test_str_is_suit_and_rank_names(self):
        assert str(Card(Suit.PIROS, Rank.ASZ)) == "PIROS ASZ"

    def test_beats_higher_same_suit(self):
        assert Card(Suit.ZOLD, Rank.ASZ).beats(Card(Suit.ZOLD, Rank.X), Suit.PIROS) is True

    def test_does_not_beat_lower_or_equal_same_suit(self):
        lower = Card(Suit.ZOLD, Rank.X)
        higher = Card(Suit.ZOLD, Rank.ASZ)
        assert lower.beats(higher, Suit.PIROS) is False
        assert higher.beats(higher, Suit.PIROS) is False

    def test_adu_beats_non_adu(self):
        assert Card(Suit.PIROS, Rank.IX).beats(Card(Suit.ZOLD, Rank.ASZ), Suit.PIROS) is True

    def test_non_adu_does_not_beat_adu(self):
        assert Card(Suit.ZOLD, Rank.ASZ).beats(Card(Suit.PIROS, Rank.IX), Suit.PIROS) is False

    def test_off_suit_non_adu_does_not_beat(self):
        assert Card(Suit.ZOLD, Rank.ASZ).beats(Card(Suit.TOK, Rank.IX), Suit.PIROS) is False


class TestDeck:
    def test_has_every_suit_and_rank_combination(self):
        expected = {Card(suit, rank) for suit in Suit for rank in Rank}
        assert expected == DECK

    def test_is_read_only(self):
        assert isinstance(DECK, frozenset)
