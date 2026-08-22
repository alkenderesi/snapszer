import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.players import Player


class TestPlayer:
    name = "Test Player"

    @pytest.fixture
    def hand(self) -> set[Card]:
        return {
            Card(Suit.PIROS, Rank.ASZ),
            Card(Suit.PIROS, Rank.X),
            Card(Suit.ZOLD, Rank.KIRALY),
            Card(Suit.ZOLD, Rank.FELSO),
            Card(Suit.TOK, Rank.ALSO),
            Card(Suit.MAKK, Rank.IX),
        }

    def test_player_hand_size(self, hand: set[Card]):
        player = Player(self.name, hand)
        assert player.hand_size == len(hand)

    def test_player_starts_with_zero_scores(self, hand: set[Card]):
        player = Player(self.name, hand)
        assert player.score == 0
        assert player.bonus_score == 0

    def test_player_starts_with_no_neighbors(self, hand: set[Card]):
        player = Player(self.name, hand)
        assert player.previous is None
        assert player.next is None
