from types import SimpleNamespace

import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.nodes import Bonus, GameEval, Node, Play, Root, RoundEval
from snapszer.players import Player
from tests.fixtures import NodeFixtures


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


class TestRoot(NodeFixtures):
    def test_root_starting_values(self, root: Root):
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


class TestBonus(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def bonus(self, root: Root, player: Player) -> Bonus:
        return Bonus(root, player, Card(Suit.PIROS, Rank.FELSO))

    def test_bonus_starting_values(self, bonus: Bonus, root: Root, player: Player):
        assert bonus.previous is root
        assert bonus.next is None
        assert bonus.choices == []
        assert bonus.player is player
        assert bonus.card == Card(Suit.PIROS, Rank.FELSO)

    def test_score_is_20(self, bonus: Bonus):
        assert bonus.score == 20

    def test_score_is_40(self, root: Root, player: Player):
        bonus = Bonus(root, player, Card(Suit.PIROS, Rank.ASZ))
        assert bonus.score == 40

    def test_activate_adds_bonus_score(self, bonus: Bonus, root: Root, player: Player):
        bonus.activate()
        assert root.next is bonus
        assert player.bonus_score == 20
        assert len(bonus.choices) == 1
        game_eval = bonus.choices[0]
        assert isinstance(game_eval, GameEval)
        assert game_eval.previous is bonus
        assert game_eval.player is player
        assert game_eval.next is None
        assert game_eval.choices == []

    def test_deactivate_reverts_score_and_clears_choices(self, bonus: Bonus, root: Root, player: Player):
        bonus.activate()
        bonus.deactivate()
        assert root.next is None
        assert player.bonus_score == 0
        assert bonus.choices == []


class TestPlay(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def play(self, root: Root, player: Player) -> Play:
        return Play(root, player, Card(Suit.PIROS, Rank.ASZ))

    def test_play_starting_values(self, play: Play, root: Root, player: Player):
        assert play.previous is root
        assert play.next is None
        assert play.choices == []
        assert play.player is player
        assert play.card == Card(Suit.PIROS, Rank.ASZ)


class TestRoundEval(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def previous_play(self, root: Root, player: Player) -> Play:
        return Play(root, player, Card(Suit.PIROS, Rank.ASZ))

    @pytest.fixture
    def round_eval(self, previous_play: Play, player: Player) -> RoundEval:
        return RoundEval(previous_play, player)

    def test_round_eval_starting_values(self, round_eval: RoundEval, previous_play: Play, player: Player):
        assert round_eval.previous is previous_play
        assert round_eval.next is None
        assert round_eval.choices == []
        assert round_eval.player is player


class TestGameEval(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def bonus(self, root: Root, player: Player) -> Bonus:
        return Bonus(root, player, Card(Suit.PIROS, Rank.FELSO))

    @pytest.fixture
    def game_eval(self, bonus: Bonus, player: Player) -> GameEval:
        return GameEval(bonus, player)

    @pytest.fixture
    def previous_play(self, root: Root, player: Player) -> Play:
        return Play(root, player, Card(Suit.PIROS, Rank.ASZ))

    @pytest.fixture
    def round_eval(self, previous_play: Play, player: Player) -> RoundEval:
        return RoundEval(previous_play, player)

    @pytest.fixture
    def game_eval_after_round_eval(self, round_eval: RoundEval, player: Player) -> GameEval:
        return GameEval(round_eval, player)

    def test_game_eval_starting_values(self, game_eval: GameEval, bonus: Bonus, player: Player):
        assert game_eval.previous is bonus
        assert game_eval.next is None
        assert game_eval.choices == []
        assert game_eval.player is player

    def test_game_eval_starting_values_after_round_eval(
        self, game_eval_after_round_eval: GameEval, round_eval: RoundEval, player: Player
    ):
        assert game_eval_after_round_eval.previous is round_eval
        assert game_eval_after_round_eval.next is None
        assert game_eval_after_round_eval.choices == []
        assert game_eval_after_round_eval.player is player

    def test_is_game_over_when_hand_is_empty(self, game_eval: GameEval, player: Player):
        player.hand.clear()
        assert game_eval.is_game_over() is True

    def test_is_game_over_when_adu_is_out_and_team_reached_66(self, game_eval: GameEval, player: Player):
        player.score = 66
        game_eval.game.is_adu_out = True
        assert game_eval.is_game_over() is True

    def test_is_game_over_when_hand_has_cards(self, game_eval: GameEval):
        assert game_eval.is_game_over() is False

    def test_is_game_over_when_adu_is_out_but_team_below_66(self, game_eval: GameEval, player: Player):
        player.score = 65
        game_eval.game.is_adu_out = True
        assert game_eval.is_game_over() is False

    def test_is_game_over_when_team_reached_66_but_adu_is_in(self, game_eval: GameEval, player: Player):
        player.score = 66
        game_eval.game.is_adu_out = False
        assert game_eval.is_game_over() is False

    def test_activate_adds_play_choice_when_previous_is_bonus(self, game_eval: GameEval, bonus: Bonus, player: Player):
        game_eval.activate()
        assert bonus.next is game_eval
        assert game_eval.game.outcome == {}
        assert len(game_eval.choices) == 1
        play = game_eval.choices[0]
        assert isinstance(play, Play)
        assert play.previous is game_eval
        assert play.player is player
        assert play.card is bonus.card
        assert play.next is None
        assert play.choices == []

    def test_deactivate_clears_play_choices(self, game_eval: GameEval, bonus: Bonus):
        game_eval.activate()
        game_eval.deactivate()
        assert bonus.next is None
        assert game_eval.choices == []

    def test_activate_adds_play_choices_for_each_card_when_previous_is_round_eval(
        self, game_eval_after_round_eval: GameEval, round_eval: RoundEval, player: Player
    ):
        game_eval_after_round_eval.activate()
        assert round_eval.next is game_eval_after_round_eval
        assert game_eval_after_round_eval.game.outcome == {}
        plays = [choice for choice in game_eval_after_round_eval.choices if isinstance(choice, Play)]
        assert {play.card for play in plays} == player.hand
        assert all(play.player is player for play in plays)
        assert all(play.previous is game_eval_after_round_eval for play in plays)

    def test_activate_adds_one_bonus_choice_when_previous_is_round_eval(
        self, game_eval_after_round_eval: GameEval, player: Player
    ):
        game_eval_after_round_eval.activate()
        bonuses = [choice for choice in game_eval_after_round_eval.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
        }
        assert all(bonus.player is player for bonus in bonuses)
        assert all(bonus.previous is game_eval_after_round_eval for bonus in bonuses)

    def test_activate_adds_multiple_bonus_choices_when_previous_is_round_eval(
        self, game_eval_after_round_eval: GameEval, player: Player
    ):
        extra_felso = Card(Suit.ZOLD, Rank.FELSO)
        extra_kiraly = Card(Suit.ZOLD, Rank.KIRALY)
        replacements = [Card(Suit.PIROS, Rank.IX), Card(Suit.PIROS, Rank.ALSO)]
        player.hand.difference_update(replacements)
        player.hand.update([extra_felso, extra_kiraly])
        game_eval_after_round_eval.activate()
        bonuses = [choice for choice in game_eval_after_round_eval.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
            extra_felso,
            extra_kiraly,
        }

    def test_activate_adds_no_bonus_choices_when_previous_is_round_eval(
        self, game_eval_after_round_eval: GameEval, player: Player
    ):
        kiraly = Card(Suit.PIROS, Rank.KIRALY)
        other = Card(Suit.ZOLD, Rank.ASZ)
        player.hand.remove(kiraly)
        player.hand.add(other)
        game_eval_after_round_eval.activate()
        assert not any(isinstance(choice, Bonus) for choice in game_eval_after_round_eval.choices)

    def test_deactivate_clears_choices_when_previous_is_round_eval(
        self, game_eval_after_round_eval: GameEval, round_eval: RoundEval
    ):
        game_eval_after_round_eval.activate()
        assert game_eval_after_round_eval.choices
        game_eval_after_round_eval.deactivate()
        assert round_eval.next is None
        assert game_eval_after_round_eval.choices == []

    def test_activate_awards_three_points_when_opponents_have_zero(
        self, game_eval: GameEval, bonus: Bonus, player: Player, players: list[Player]
    ):
        player.hand.clear()
        game_eval.activate()
        assert bonus.next is game_eval
        assert game_eval.choices == []
        assert game_eval.game.outcome == {
            players[0]: 3,
            players[1]: 0,
            players[2]: 0,
            players[3]: 0,
        }

    def test_activate_awards_two_points_when_opponents_have_less_than_33(
        self, game_eval: GameEval, player: Player, players: list[Player]
    ):
        player.hand.clear()
        players[1].score = 32
        game_eval.activate()
        assert game_eval.game.outcome == {
            players[0]: 2,
            players[1]: 0,
            players[2]: 0,
            players[3]: 0,
        }

    def test_activate_awards_one_point_when_opponents_have_33_or_more(
        self, game_eval: GameEval, player: Player, players: list[Player]
    ):
        player.hand.clear()
        players[1].score = 33
        game_eval.activate()
        assert game_eval.game.outcome == {
            players[0]: 1,
            players[1]: 0,
            players[2]: 0,
            players[3]: 0,
        }

    def test_deactivate_clears_outcome_when_game_is_over(self, game_eval: GameEval, bonus: Bonus, player: Player):
        player.hand.clear()
        game_eval.activate()
        game_eval.deactivate()
        assert bonus.next is None
        assert game_eval.game.outcome == {}
