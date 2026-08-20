from itertools import islice

import pytest

from snapszer.cards import DECK, Card
from snapszer.players import Player


class TestPlayer:
    name = "Test Player"

    @pytest.fixture
    def starting_hand(self) -> set[Card]:
        return set(islice(DECK, 6))

    def test_player_name_is_read_only(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        with pytest.raises(AttributeError):
            player.name = "New Name"
        assert player.name == self.name

    def test_player_hand_size(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        assert player.hand_size == len(starting_hand)

    def test_player_starts_with_zero_scores(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        assert player.score == 0
        assert player.bonus_score == 0

    def test_player_starts_with_no_neighbors(self, starting_hand: set[Card]) -> None:
        player = Player(self.name, starting_hand)
        assert player.previous is None
        assert player.next is None
