from itertools import islice

import pytest

from snapszer.cards import DECK, Card
from snapszer.players import Player


class TestPlayer:
    name = "Test Player"

    @pytest.fixture
    def starting_hand(self) -> set[Card]:
        return set(islice(DECK, 6))

    def test_players_are_never_equal(self, starting_hand: set[Card]) -> None:
        player_a = Player(self.name, starting_hand)
        player_b = Player(self.name, starting_hand)
        assert player_a.name == player_b.name
        assert player_a.hand == player_b.hand
        assert player_a is not player_b
        assert player_a != player_b

    def test_player_name_is_immutable(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        with pytest.raises(AttributeError):
            player.name = "New Name"
        assert player.name == self.name

    def test_player_keeps_the_given_hand(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        assert player.hand == starting_hand

    @pytest.mark.parametrize("hand_size", [0, 5, 7], ids=["empty", "small", "large"])
    def test_player_rejects_invalid_hand_size(self, hand_size: int) -> None:
        hand = set(islice(DECK, hand_size))
        with pytest.raises(
            ValueError,
            match=f"Hand size must be 6, got {hand_size}",
        ):
            Player(self.name, hand)

    def test_player_starts_with_zero_scores(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        assert player.score == 0
        assert player.bonus_score == 0

    def test_player_starts_with_no_neighbors(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        assert player.previous is None
        assert player.next is None
