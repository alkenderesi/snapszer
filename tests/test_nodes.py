from types import SimpleNamespace

import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.nodes import Node, Root
from snapszer.players import Player


class TestNode:
    @pytest.fixture
    def previous(self) -> SimpleNamespace:
        return SimpleNamespace(game=object())

    @pytest.fixture
    def node(self, previous: SimpleNamespace) -> Node:
        return Node(previous)

    def test_node_starts_with_previous(self, node: Node, previous: SimpleNamespace):
        assert node.previous is previous
        assert node.next is None
        assert node.choices == []

    def test_game_delegates_to_previous(self, node: Node, previous: SimpleNamespace):
        assert node.game is previous.game

    def test_activate_is_not_implemented(self, node: Node):
        with pytest.raises(NotImplementedError):
            node.activate()

    def test_deactivate_is_not_implemented(self, node: Node):
        with pytest.raises(NotImplementedError):
            node.deactivate()


class TestRoot:
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

    @pytest.fixture
    def root(self, players: list[Player]) -> Root:
        return Root(self.adu, players)

    def test_root_starts_without_previous(self, root: Root):
        assert root.previous is None
        assert root.next is None
        assert root.choices == []

    def test_game_is_owned_by_root(self, root: Root, players: list[Player]):
        assert isinstance(root.game, Game)
        assert root.game.adu is self.adu
        assert root.game.players is players
