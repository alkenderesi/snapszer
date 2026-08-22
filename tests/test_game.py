import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.players import Player


class TestGame:
    adu = Card(Suit.PIROS, Rank.ASZ)

    @pytest.fixture
    def players(self) -> list[Player]:
        return [
            Player(
                "A",
                {
                    Card(Suit.PIROS, Rank.ASZ),
                    Card(Suit.PIROS, Rank.X),
                    Card(Suit.PIROS, Rank.KIRALY),
                    Card(Suit.PIROS, Rank.FELSO),
                    Card(Suit.PIROS, Rank.ALSO),
                    Card(Suit.PIROS, Rank.IX),
                },
            ),
            Player(
                "B",
                {
                    Card(Suit.ZOLD, Rank.ASZ),
                    Card(Suit.ZOLD, Rank.X),
                    Card(Suit.ZOLD, Rank.KIRALY),
                    Card(Suit.ZOLD, Rank.FELSO),
                    Card(Suit.ZOLD, Rank.ALSO),
                    Card(Suit.ZOLD, Rank.IX),
                },
            ),
            Player(
                "C",
                {
                    Card(Suit.TOK, Rank.ASZ),
                    Card(Suit.TOK, Rank.X),
                    Card(Suit.TOK, Rank.KIRALY),
                    Card(Suit.TOK, Rank.FELSO),
                    Card(Suit.TOK, Rank.ALSO),
                    Card(Suit.TOK, Rank.IX),
                },
            ),
            Player(
                "D",
                {
                    Card(Suit.MAKK, Rank.ASZ),
                    Card(Suit.MAKK, Rank.X),
                    Card(Suit.MAKK, Rank.KIRALY),
                    Card(Suit.MAKK, Rank.FELSO),
                    Card(Suit.MAKK, Rank.ALSO),
                    Card(Suit.MAKK, Rank.IX),
                },
            ),
        ]

    def test_wrong_player_count(self, players: list[Player]):
        with pytest.raises(ValueError, match="Number of players must be 4, got 3"):
            Game(self.adu, players[:3])

    def test_wrong_hand_size(self, players: list[Player]):
        players[0].hand.remove(Card(Suit.PIROS, Rank.ASZ))
        with pytest.raises(ValueError, match="Player A must have 6 cards, got 5"):
            Game(self.adu, players)

    def test_undealt_cards(self, players: list[Player]):
        players[0].hand.remove(Card(Suit.PIROS, Rank.ASZ))
        players[0].hand.add(Card(Suit.ZOLD, Rank.ASZ))
        with pytest.raises(ValueError, match="Undealt cards: PIROS ASZ"):
            Game(self.adu, players)

    def test_adu_team_has_one_player(self, players: list[Player]):
        game = Game(self.adu, players)
        assert game.adu_team == {players[0]}
        assert game.non_adu_team == {players[1], players[2], players[3]}

    def test_adu_team_has_two_players(self, players: list[Player]):
        other = Card(Suit.ZOLD, Rank.ASZ)
        players[0].hand.remove(self.adu)
        players[0].hand.add(other)
        players[1].hand.remove(other)
        players[1].hand.add(self.adu)
        game = Game(self.adu, players)
        assert game.adu_team == {players[0], players[1]}
        assert game.non_adu_team == {players[2], players[3]}

    def test_players_are_linked_in_a_circle(self, players: list[Player]):
        game = Game(self.adu, players)
        current = game.players[0]
        for expected in game.players:
            assert current is expected
            assert current.next.previous is current
            current = current.next
        assert current is game.players[0]
