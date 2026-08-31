import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.nodes import Root, Round
from snapszer.players import Player


def four_players() -> list[Player]:
    return [Player(name, {Card(suit, rank) for rank in Rank}) for name, suit in zip("ABCD", Suit, strict=True)]


class GameFixtures:
    adu = Card(Suit.PIROS, Rank.ASZ)

    @pytest.fixture
    def players(self) -> list[Player]:
        return four_players()


class NodeFixtures(GameFixtures):
    @pytest.fixture
    def root(self, players: list[Player]) -> Root:
        return Root(self.adu, players)

    @pytest.fixture
    def round_node(self, root: Root) -> Round:
        root.activate()
        return root.choices[0]
