import re
from itertools import islice

import pytest

from snapszer.cards import DECK, Card, Rank, Suit
from snapszer.game import Game
from snapszer.players import Player


class TestGame:
    adu = Card(Suit.PIROS, Rank.ASZ)

    @pytest.fixture
    def players(self) -> tuple[Player, ...]:
        cards = iter(DECK)
        return (
            Player("A", set(islice(cards, 6))),
            Player("B", set(islice(cards, 6))),
            Player("C", set(islice(cards, 6))),
            Player("D", set(islice(cards, 6))),
        )

    def test_adu_is_read_only(self, players: tuple[Player, ...]) -> None:
        game = Game(self.adu, players)
        with pytest.raises(AttributeError):
            game.adu = Card(Suit.MAKK, Rank.ASZ)
        assert game.adu == self.adu

    def test_players_are_read_only(self, players: tuple[Player, ...]) -> None:
        game = Game(self.adu, players)
        with pytest.raises(AttributeError):
            game.players = (Player("A", set(islice(DECK, 6))),)
        assert game.players == players

    @pytest.mark.parametrize("player_count", [0, 3, 5], ids=["empty", "small", "large"])
    def test_game_rejects_invalid_player_count(self, player_count: int) -> None:
        hand = set(islice(DECK, 6))
        players = tuple(Player(str(i), hand) for i in range(player_count))
        with pytest.raises(
            ValueError,
            match=re.escape(
                f"Player count must be one of {{4}}, got {player_count}",
            ),
        ):
            Game(self.adu, players)

    @pytest.mark.parametrize("hand_size", [0, 5, 7], ids=["empty", "small", "large"])
    def test_game_rejects_invalid_starting_hand_size(self, hand_size: int) -> None:
        cards = iter(DECK)
        players = (
            Player("A", set(islice(cards, hand_size))),
            Player("B", set(islice(cards, 6))),
            Player("C", set(islice(cards, 6))),
            Player("D", set(islice(cards, 6))),
        )
        with pytest.raises(
            ValueError,
            match=f"Player A has {hand_size} cards instead of 6",
        ):
            Game(self.adu, players)

    def test_game_rejects_duplicate_player_names(self) -> None:
        cards = iter(DECK)
        players = (
            Player("A", set(islice(cards, 6))),
            Player("B", set(islice(cards, 6))),
            Player("A", set(islice(cards, 6))),
            Player("D", set(islice(cards, 6))),
        )
        with pytest.raises(ValueError, match="Duplicate player name: A"):
            Game(self.adu, players)

    def test_game_rejects_duplicate_cards(self) -> None:
        duplicate_card = Card(Suit.MAKK, Rank.ASZ)
        cards = (card for card in DECK - {duplicate_card})
        players = (
            Player("A", {duplicate_card, *islice(cards, 5)}),
            Player("B", {duplicate_card, *islice(cards, 5)}),
            Player("C", set(islice(cards, 6))),
            Player("D", set(islice(cards, 6))),
        )
        with pytest.raises(
            ValueError,
            match=re.escape(f"Duplicate card: {duplicate_card}"),
        ):
            Game(self.adu, players)

    def test_players_are_linked_in_a_circle(self, players: tuple[Player, ...]) -> None:
        game = Game(self.adu, players)
        current = game.players[0]
        for expected in game.players:
            assert current is expected
            assert current.next.previous is current
            current = current.next
        assert current is game.players[0]
