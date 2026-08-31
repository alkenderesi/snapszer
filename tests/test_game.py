import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.players import Player
from tests.fixtures import GameFixtures, four_players


class TestGame(GameFixtures):
    def test_rejects_wrong_player_count(self, players: list[Player]):
        with pytest.raises(ValueError, match="Number of players must be 4, got 3"):
            Game(self.adu, players[:3])

    def test_rejects_wrong_hand_size(self, players: list[Player]):
        players[0].hand.remove(Card(Suit.PIROS, Rank.ASZ))
        with pytest.raises(ValueError, match="Player A must have 6 cards, got 5"):
            Game(self.adu, players)

    def test_rejects_undealt_cards(self, players: list[Player]):
        players[0].hand.remove(Card(Suit.PIROS, Rank.ASZ))
        players[0].hand.add(Card(Suit.ZOLD, Rank.ASZ))
        with pytest.raises(ValueError, match="Undealt cards: PIROS ASZ"):
            Game(self.adu, players)

    def test_adu_starts_in(self, players: list[Player]):
        game = Game(self.adu, players)
        assert game.is_adu_out is False

    def test_adu_team_has_one_player(self, players: list[Player]):
        game = Game(self.adu, players)
        assert game.adu_team == {players[0]}
        assert game.non_adu_team == {players[1], players[2], players[3]}
        assert players[0].team is game.adu_team
        assert players[0].opponent_team is game.non_adu_team
        for player in players[1:]:
            assert player.team is game.non_adu_team
            assert player.opponent_team is game.adu_team

    def test_adu_team_has_two_players(self):
        players = four_players()
        a, b, c, d = players
        other = Card(Suit.ZOLD, Rank.ASZ)
        a.hand.remove(self.adu)
        a.hand.add(other)
        b.hand.remove(other)
        b.hand.add(self.adu)
        game = Game(self.adu, players)
        assert game.adu_team == {a, b}
        assert game.non_adu_team == {c, d}
        assert a.team is game.adu_team
        assert a.opponent_team is game.non_adu_team
        assert b.team is game.adu_team
        assert b.opponent_team is game.non_adu_team
        assert c.team is game.non_adu_team
        assert c.opponent_team is game.adu_team
        assert d.team is game.non_adu_team
        assert d.opponent_team is game.adu_team

    def test_players_are_linked_in_a_circle(self, players: list[Player]):
        game = Game(self.adu, players)
        current = game.players[0]
        for expected in game.players:
            assert current is expected
            assert current.next.previous is current
            current = current.next
        assert current is game.players[0]
