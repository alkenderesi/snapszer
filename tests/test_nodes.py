from types import SimpleNamespace

import pytest

from snapszer.nodes import Node


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
