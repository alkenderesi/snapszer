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
    def test_all_ranks_and_their_values_are_present(self):
        assert {rank: rank.value for rank in Rank} == {
            Rank.IX: 0,
            Rank.ALSO: 2,
            Rank.FELSO: 3,
            Rank.KIRALY: 4,
            Rank.X: 10,
            Rank.ASZ: 11,
        }


class TestCard:
    @pytest.mark.parametrize("rank", list(Rank), ids=lambda rank: rank.name)
    def test_card_value_matches_rank_value(self, rank: Rank):
        card = Card(Suit.PIROS, rank)
        assert card.value == rank.value

    def test_card_value_is_suit_independent(self):
        rank = Rank.ASZ
        values = {Card(suit, rank).value for suit in Suit}
        assert values == {rank.value}

    def test_cards_with_same_suit_and_rank_are_equal(self):
        card_a = Card(Suit.PIROS, Rank.ASZ)
        card_b = Card(Suit.PIROS, Rank.ASZ)
        assert card_a is not card_b
        assert card_a == card_b
        assert {card_a, card_b} == {card_a}

    def test_cards_with_different_suit_or_rank_are_not_equal(self):
        card = Card(Suit.PIROS, Rank.ASZ)
        assert card != Card(Suit.MAKK, Rank.ASZ)
        assert card != Card(Suit.PIROS, Rank.X)

    def test_card_is_read_only(self):
        card = Card(Suit.PIROS, Rank.ASZ)
        with pytest.raises(FrozenInstanceError):
            card.suit = Suit.ZOLD
        with pytest.raises(FrozenInstanceError):
            card.rank = Rank.X
        with pytest.raises(FrozenInstanceError):
            card.value = 10
        assert card.suit == Suit.PIROS
        assert card.rank == Rank.ASZ
        assert card.value == 11

    def test_card_string_is_suit_and_rank_names(self):
        card = Card(Suit.PIROS, Rank.ASZ)
        assert str(card) == "PIROS ASZ"


class TestDeck:
    def test_deck_has_every_suit_and_rank_combination(self):
        expected = {Card(suit, rank) for suit in Suit for rank in Rank}
        assert expected == DECK

    def test_deck_is_read_only(self):
        assert isinstance(DECK, frozenset)
