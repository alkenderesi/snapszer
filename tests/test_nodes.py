from types import SimpleNamespace

import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.nodes import Bonus, Node, Play, Root
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

    def test_activate_adds_play_choices_for_each_card(self, root: Root, players: list[Player]):
        starting_player = players[0]
        root.activate()
        plays = [choice for choice in root.choices if isinstance(choice, Play)]
        assert {play.card for play in plays} == starting_player.hand
        assert all(play.player is starting_player for play in plays)
        assert all(play.previous is root for play in plays)

    def test_activate_adds_one_bonus_choice(self, root: Root, players: list[Player]):
        starting_player = players[0]
        root.activate()
        bonuses = [choice for choice in root.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
        }
        assert all(bonus.player is starting_player for bonus in bonuses)
        assert all(bonus.previous is root for bonus in bonuses)

    def test_activate_adds_multiple_bonus_choices(self, players: list[Player]):
        extra_felso = Card(Suit.ZOLD, Rank.FELSO)
        extra_kiraly = Card(Suit.ZOLD, Rank.KIRALY)
        replacements = [Card(Suit.PIROS, Rank.IX), Card(Suit.PIROS, Rank.ALSO)]
        players[0].hand.difference_update(replacements)
        players[0].hand.update([extra_felso, extra_kiraly])
        players[1].hand.difference_update([extra_felso, extra_kiraly])
        players[1].hand.update(replacements)
        root = Root(self.adu, players)
        root.activate()
        bonuses = [choice for choice in root.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
            extra_felso,
            extra_kiraly,
        }

    def test_activate_adds_no_bonus_choices(self, players: list[Player]):
        kiraly = Card(Suit.PIROS, Rank.KIRALY)
        other = Card(Suit.ZOLD, Rank.ASZ)
        players[0].hand.remove(kiraly)
        players[0].hand.add(other)
        players[1].hand.remove(other)
        players[1].hand.add(kiraly)
        root = Root(self.adu, players)
        root.activate()
        assert not any(isinstance(choice, Bonus) for choice in root.choices)

    def test_deactivate_clears_choices(self, root: Root):
        root.activate()
        assert root.choices
        root.deactivate()
        assert root.choices == []
