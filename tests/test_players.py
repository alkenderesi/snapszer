from snapszer.cards import Card, Rank, Suit
from snapszer.players import Player


class TestPlayer:
    def test_player_equality(self) -> None:
        player_a = Player("Test Player", {Card(Suit.PIROS, Rank.ASZ)})
        player_b = Player("Test Player", {Card(Suit.PIROS, Rank.ASZ)})
        assert player_a is not player_b
        assert player_a != player_b

    def test_player_string(self) -> None:
        name = "Test Player"
        player = Player(name, {Card(Suit.PIROS, Rank.ASZ)})
        assert str(player) == name
