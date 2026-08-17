from dataclasses import FrozenInstanceError

import pytest

from snapszer.cards import DECK, Card, Rank, Suit


class TestSuit:
    def test_all_suits_are_present(self) -> None:
        assert Suit.PIROS == "PIROS"
        assert Suit.ZOLD == "ZOLD"
        assert Suit.TOK == "TOK"
        assert Suit.MAKK == "MAKK"
        assert len(Suit) == 4


class TestRank:
    def test_all_ranks_are_present(self) -> None:
        assert Rank.IX == 0
        assert Rank.ALSO == 2
        assert Rank.FELSO == 3
        assert Rank.KIRALY == 4
        assert Rank.X == 10
        assert Rank.ASZ == 11
        assert len(Rank) == 6


class TestCard:
    def test_card_value_matches_rank_value(self) -> None:
        suit = Suit.PIROS
        rank = Rank.ASZ
        card = Card(suit, rank)
        assert card.value == rank.value

    def test_card_value_is_suit_independent(self) -> None:
        card_a = Card(Suit.MAKK, Rank.ASZ)
        card_b = Card(Suit.ZOLD, Rank.ASZ)
        assert card_a.value == card_b.value

    def test_card_equality(self) -> None:
        card_a = Card(Suit.PIROS, Rank.ASZ)
        card_b = Card(Suit.PIROS, Rank.ASZ)
        assert card_a is not card_b
        assert card_a == card_b

    def test_card_is_immutable(self) -> None:
        card = Card(Suit.PIROS, Rank.ASZ)
        with pytest.raises(FrozenInstanceError):
            card.suit = Suit.ZOLD
        with pytest.raises(FrozenInstanceError):
            card.rank = Rank.X

    def test_card_string(self) -> None:
        suit = Suit.PIROS
        rank = Rank.ASZ
        card = Card(suit, rank)
        assert str(card) == f"{suit.name} {rank.name}"


class TestDeck:
    def test_all_cards_are_present(self) -> None:
        for suit in Suit:
            for rank in Rank:
                assert Card(suit, rank) in DECK
        assert len(DECK) == 24

    def test_deck_subtraction(self) -> None:
        hand = {Card(Suit.PIROS, Rank.ASZ)}
        diff = DECK - hand
        assert isinstance(diff, frozenset)
        assert len(diff) == 23

    def test_deck_is_immutable(self) -> None:
        card = Card(Suit.PIROS, Rank.ASZ)
        with pytest.raises(AttributeError):
            DECK.add(card)
        with pytest.raises(AttributeError):
            DECK.remove(card)
