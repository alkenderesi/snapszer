from snapszer.cards import Card, Rank, Suit
from snapszer.players import Player


class TestPlayer:
    def test_defaults(self):
        player = Player("A", {Card(Suit.PIROS, Rank.ASZ)})
        assert player.score == 0
        assert player.bonus_score == 0
        assert player.previous is None
        assert player.next is None
        assert player.team == {player}
        assert player.opponent_team == set()

    def test_team_score_sums_scores_and_bonuses(self):
        player = Player("A", set())
        teammate = Player("B", set())
        player.team.add(teammate)
        player.score = 20
        player.bonus_score = 20
        teammate.score = 13
        teammate.bonus_score = 40
        assert player.team_score == 93

    def test_team_score_ignores_bonuses_without_hits(self):
        player = Player("A", set())
        teammate = Player("B", set())
        player.team.add(teammate)
        player.bonus_score = 20
        teammate.bonus_score = 40
        assert player.team_score == 0

    def test_opponent_team_score_sums_scores_and_bonuses(self):
        player = Player("A", set())
        opponent = Player("B", set())
        player.opponent_team.add(opponent)
        opponent.score = 11
        opponent.bonus_score = 20
        assert player.opponent_team_score == 31
