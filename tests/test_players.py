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

    def test_player_starts_as_own_team(self, hand: set[Card]):
        player = Player(self.name, hand)
        assert player.team == {player}
        assert player.opponent_team == set()

    def test_team_score_sums_scores_and_bonuses(self, hand: set[Card]):
        player = Player(self.name, hand)
        teammate = Player("Teammate", set())
        player.team.add(teammate)
        player.score = 20
        player.bonus_score = 20
        teammate.score = 13
        teammate.bonus_score = 40
        assert player.team_score == 93

    def test_team_score_is_zero_when_team_only_has_bonuses(self, hand: set[Card]):
        player = Player(self.name, hand)
        teammate = Player("Teammate", set())
        player.team.add(teammate)
        player.score = 0
        player.bonus_score = 20
        teammate.score = 0
        teammate.bonus_score = 40
        assert player.team_score == 0

    def test_opponent_team_score_sums_scores_and_bonuses(self, hand: set[Card]):
        player = Player(self.name, hand)
        opponent = Player("Opponent", set())
        player.opponent_team.add(opponent)
        opponent.score = 11
        opponent.bonus_score = 20
        assert player.opponent_team_score == 31
