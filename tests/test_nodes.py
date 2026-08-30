from types import SimpleNamespace

import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.nodes import Bonus, GameEval, Node, Play, Root, Round, RoundEval
from snapszer.players import Player
from tests.fixtures import NodeFixtures


def _exchange(player: Player, card_out: Card, other: Player, card_in: Card):
    player.hand.remove(card_out)
    player.hand.add(card_in)
    other.hand.remove(card_in)
    other.hand.add(card_out)


def _play_choice(choices: list, card: Card) -> Play:
    return next(choice for choice in choices if isinstance(choice, Play) and choice.card == card)


class TestNode:
    @pytest.fixture
    def previous(self) -> SimpleNamespace:
        return SimpleNamespace(game=object(), round=object())

    @pytest.fixture
    def node(self, previous: SimpleNamespace) -> Node:
        return Node(previous)

    def test_node_starts_with_previous(self, node: Node, previous: SimpleNamespace):
        assert node.previous is previous
        assert node.next is None
        assert node.choices == []

    def test_game_delegates_to_previous(self, node: Node, previous: SimpleNamespace):
        assert node.game is previous.game

    def test_round_delegates_to_previous(self, node: Node, previous: SimpleNamespace):
        assert node.round is previous.round

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
        assert root.round is None

    def test_game_is_owned_by_root(self, root: Root, players: list[Player]):
        assert isinstance(root.game, Game)
        assert root.game.adu is self.adu
        assert root.game.players is players

    def test_activate_adds_round_for_starting_player(self, root: Root, players: list[Player]):
        root.activate()
        assert len(root.choices) == 1
        round_node = root.choices[0]
        assert isinstance(round_node, Round)
        assert round_node.previous is root
        assert round_node.player is players[0]
        assert round_node.next is None
        assert round_node.choices == []

    def test_deactivate_clears_choices(self, root: Root):
        root.activate()
        assert root.choices
        root.deactivate()
        assert root.choices == []


class TestRound(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    def test_round_starting_values(self, round_node: Round, root: Root, player: Player):
        assert round_node.previous is root
        assert round_node.next is None
        assert round_node.choices == []
        assert round_node.player is player
        assert round_node.plays == []
        assert round_node.value == 0
        assert round_node.round is round_node

    def test_activate_adds_play_choices_for_each_card(self, round_node: Round, root: Root, player: Player):
        round_node.activate()
        assert root.next is round_node
        plays = [choice for choice in round_node.choices if isinstance(choice, Play)]
        assert {play.card for play in plays} == player.hand
        assert all(play.player is player for play in plays)
        assert all(play.previous is round_node for play in plays)

    def test_activate_adds_one_bonus_choice(self, round_node: Round, player: Player):
        round_node.activate()
        bonuses = [choice for choice in round_node.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
        }
        assert all(bonus.player is player for bonus in bonuses)
        assert all(bonus.previous is round_node for bonus in bonuses)

    def test_activate_adds_multiple_bonus_choices(self, round_node: Round, players: list[Player]):
        extra_felso = Card(Suit.ZOLD, Rank.FELSO)
        extra_kiraly = Card(Suit.ZOLD, Rank.KIRALY)
        replacements = [Card(Suit.PIROS, Rank.IX), Card(Suit.PIROS, Rank.ALSO)]
        players[0].hand.difference_update(replacements)
        players[0].hand.update([extra_felso, extra_kiraly])
        players[1].hand.difference_update([extra_felso, extra_kiraly])
        players[1].hand.update(replacements)
        round_node.activate()
        bonuses = [choice for choice in round_node.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
            extra_felso,
            extra_kiraly,
        }

    def test_activate_adds_no_bonus_choices(self, round_node: Round, players: list[Player]):
        kiraly = Card(Suit.PIROS, Rank.KIRALY)
        other = Card(Suit.ZOLD, Rank.ASZ)
        _exchange(players[0], kiraly, players[1], other)
        round_node.activate()
        assert not any(isinstance(choice, Bonus) for choice in round_node.choices)

    def test_deactivate_clears_choices(self, round_node: Round, root: Root):
        round_node.activate()
        assert round_node.choices
        round_node.deactivate()
        assert root.next is None
        assert round_node.choices == []

    def test_winning_play_is_first_when_nothing_beats_it(self, round_node: Round, players: list[Player]):
        first = Play(round_node, players[0], Card(Suit.PIROS, Rank.X))
        second = Play(first, players[1], Card(Suit.ZOLD, Rank.ASZ))
        round_node.plays.extend([first, second])
        assert round_node.winning_play is first

    def test_winning_play_is_higher_same_suit(self, round_node: Round, players: list[Player]):
        first = Play(round_node, players[0], Card(Suit.PIROS, Rank.X))
        second = Play(first, players[1], Card(Suit.PIROS, Rank.ASZ))
        round_node.plays.extend([first, second])
        assert round_node.winning_play is second

    def test_winning_play_is_adu_over_non_adu(self, round_node: Round, players: list[Player]):
        first = Play(round_node, players[0], Card(Suit.ZOLD, Rank.ASZ))
        second = Play(first, players[1], Card(Suit.PIROS, Rank.IX))
        round_node.plays.extend([first, second])
        assert round_node.winning_play is second


class TestBonus(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def bonus(self, round_node: Round, player: Player) -> Bonus:
        return Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO))

    def test_bonus_starting_values(self, bonus: Bonus, round_node: Round, player: Player):
        assert bonus.previous is round_node
        assert bonus.next is None
        assert bonus.choices == []
        assert bonus.player is player
        assert bonus.card == Card(Suit.PIROS, Rank.FELSO)

    def test_score_is_20(self, round_node: Round, player: Player):
        bonus = Bonus(round_node, player, Card(Suit.ZOLD, Rank.FELSO))
        assert bonus.score == 20

    def test_score_is_40(self, bonus: Bonus):
        assert bonus.score == 40

    def test_activate_adds_bonus_score(self, bonus: Bonus, round_node: Round, player: Player):
        bonus.activate()
        assert round_node.next is bonus
        assert player.bonus_score == 40
        assert len(bonus.choices) == 1
        game_eval = bonus.choices[0]
        assert isinstance(game_eval, GameEval)
        assert game_eval.previous is bonus
        assert game_eval.player is player
        assert game_eval.next is None
        assert game_eval.choices == []

    def test_deactivate_reverts_score_and_clears_choices(self, bonus: Bonus, round_node: Round, player: Player):
        bonus.activate()
        bonus.deactivate()
        assert round_node.next is None
        assert player.bonus_score == 0
        assert bonus.choices == []


class TestPlay(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def play(self, round_node: Round, player: Player) -> Play:
        return Play(round_node, player, Card(Suit.PIROS, Rank.ASZ))

    def test_play_starting_values(self, play: Play, round_node: Round, player: Player):
        assert play.previous is round_node
        assert play.next is None
        assert play.choices == []
        assert play.player is player
        assert play.card == Card(Suit.PIROS, Rank.ASZ)
        assert play.round is round_node

    def test_activate_updates_round_and_hand(self, round_node: Round, player: Player):
        card = Card(Suit.PIROS, Rank.X)
        round_node.activate()
        play = _play_choice(round_node.choices, card)
        play.activate()
        assert round_node.next is play
        assert card not in player.hand
        assert round_node.plays == [play]
        assert round_node.value == card.value
        assert play.game.is_adu_out is False
        assert {choice.card for choice in play.choices} == player.next.hand
        play.deactivate()
        assert round_node.next is None
        assert card in player.hand
        assert round_node.plays == []
        assert round_node.value == 0
        assert play.game.is_adu_out is False
        assert play.choices == []

    def test_activate_sets_adu_out(self, play: Play, player: Player):
        play.activate()
        assert play.card not in player.hand
        assert play.game.is_adu_out is True

    def test_deactivate_reverts_round_hand_and_adu_out(self, play: Play, round_node: Round, player: Player):
        play.activate()
        play.deactivate()
        assert round_node.next is None
        assert play.card in player.hand
        assert round_node.plays == []
        assert round_node.value == 0
        assert play.game.is_adu_out is False
        assert play.choices == []

    def test_activate_requires_following_suit_and_beating(self, round_node: Round, players: list[Player]):
        higher = Card(Suit.PIROS, Rank.ASZ)
        lead_card = Card(Suit.PIROS, Rank.IX)
        other = Card(Suit.ZOLD, Rank.ASZ)
        _exchange(players[0], higher, players[1], other)
        round_node.activate()
        play = _play_choice(round_node.choices, lead_card)
        play.activate()
        assert {choice.card for choice in play.choices} == {higher}

    def test_activate_requires_following_suit_when_unable_to_beat(self, round_node: Round, players: list[Player]):
        lower = Card(Suit.PIROS, Rank.IX)
        other = Card(Suit.ZOLD, Rank.ASZ)
        _exchange(players[0], lower, players[1], other)
        round_node.activate()
        play = _play_choice(round_node.choices, Card(Suit.PIROS, Rank.ASZ))
        play.activate()
        assert {choice.card for choice in play.choices} == {lower}

    def test_activate_requires_trumping_and_beating(self, round_node: Round, players: list[Player]):
        lead_card = Card(Suit.TOK, Rank.IX)
        adu_card = Card(Suit.PIROS, Rank.FELSO)
        _exchange(players[0], Card(Suit.PIROS, Rank.IX), players[2], lead_card)
        _exchange(players[0], adu_card, players[1], Card(Suit.ZOLD, Rank.IX))
        round_node.activate()
        play = _play_choice(round_node.choices, lead_card)
        play.activate()
        assert {choice.card for choice in play.choices} == {adu_card}

    def test_activate_requires_trumping_when_unable_to_beat(self, round_node: Round, players: list[Player]):
        lead_card = Card(Suit.TOK, Rank.IX)
        high_adu = Card(Suit.PIROS, Rank.ASZ)
        low_adu = Card(Suit.PIROS, Rank.IX)
        _exchange(players[0], low_adu, players[2], lead_card)
        _exchange(players[0], high_adu, players[1], Card(Suit.ZOLD, Rank.ASZ))
        remaining_tok = [card for card in players[2].hand if card.suit == Suit.TOK]
        makk_cards = list(players[3].hand)
        for tok_card, makk_card in zip(remaining_tok, makk_cards[: len(remaining_tok)], strict=True):
            _exchange(players[2], tok_card, players[3], makk_card)
        round_node.activate()
        lead = Play(round_node, players[0], lead_card)
        lead.activate()
        trump_play = Play(lead, players[1], high_adu)
        trump_play.activate()
        assert {choice.card for choice in trump_play.choices} == {low_adu}

    def test_activate_allows_any_card_when_unable_to_follow_or_trump(self, round_node: Round, players: list[Player]):
        round_node.activate()
        play = _play_choice(round_node.choices, Card(Suit.PIROS, Rank.IX))
        play.activate()
        assert {choice.card for choice in play.choices} == players[1].hand

    def test_activate_adds_round_eval_after_last_play(self, round_node: Round, players: list[Player]):
        round_node.activate()
        lead = _play_choice(round_node.choices, Card(Suit.PIROS, Rank.X))
        lead.activate()
        second = lead.choices[0]
        second.activate()
        third = second.choices[0]
        third.activate()
        fourth = third.choices[0]
        fourth.activate()
        assert len(fourth.choices) == 1
        round_eval = fourth.choices[0]
        assert isinstance(round_eval, RoundEval)
        assert round_eval.previous is fourth
        assert round_eval.player is players[0]


class TestRoundEval(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def play(self, round_node: Round) -> Play:
        round_node.activate()
        chosen = _play_choice(round_node.choices, Card(Suit.PIROS, Rank.ASZ))
        chosen.activate()
        return chosen

    @pytest.fixture
    def round_eval(self, play: Play) -> RoundEval:
        return RoundEval(play)

    def test_round_eval_starting_values(self, round_eval: RoundEval, play: Play, player: Player):
        assert round_eval.previous is play
        assert round_eval.next is None
        assert round_eval.choices == []
        assert round_eval.player is player

    def test_activate_adds_round_value_to_winner(self, round_eval: RoundEval, play: Play, player: Player):
        round_value = round_eval.round.value
        round_eval.activate()
        assert play.next is round_eval
        assert player.score == round_value
        assert len(round_eval.choices) == 1
        game_eval = round_eval.choices[0]
        assert isinstance(game_eval, GameEval)
        assert game_eval.previous is round_eval
        assert game_eval.player is player

    def test_deactivate_reverts_score_and_clears_choices(self, round_eval: RoundEval, play: Play, player: Player):
        round_eval.activate()
        round_eval.deactivate()
        assert play.next is None
        assert player.score == 0
        assert round_eval.choices == []


class TestGameEval(NodeFixtures):
    @pytest.fixture
    def player(self, players: list[Player]) -> Player:
        return players[0]

    @pytest.fixture
    def bonus(self, round_node: Round, player: Player) -> Bonus:
        return Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO))

    @pytest.fixture
    def game_eval(self, bonus: Bonus, player: Player) -> GameEval:
        return GameEval(bonus, player)

    @pytest.fixture
    def play(self, round_node: Round) -> Play:
        round_node.activate()
        chosen = _play_choice(round_node.choices, Card(Suit.PIROS, Rank.ASZ))
        chosen.activate()
        return chosen

    @pytest.fixture
    def round_eval(self, play: Play) -> RoundEval:
        return RoundEval(play)

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

    def test_activate_ends_game_when_hand_is_empty(
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

    def test_activate_ends_game_when_adu_is_out_and_team_reached_66(
        self, game_eval: GameEval, player: Player, players: list[Player]
    ):
        player.score = 66
        game_eval.game.is_adu_out = True
        game_eval.activate()
        assert game_eval.choices == []
        assert game_eval.game.outcome == {
            players[0]: 3,
            players[1]: 0,
            players[2]: 0,
            players[3]: 0,
        }

    def test_activate_continues_when_hand_has_cards(self, game_eval: GameEval):
        game_eval.activate()
        assert game_eval.game.outcome == {}
        assert game_eval.choices

    def test_activate_continues_when_adu_is_out_but_team_below_66(self, game_eval: GameEval, player: Player):
        player.score = 65
        game_eval.game.is_adu_out = True
        game_eval.activate()
        assert game_eval.game.outcome == {}
        assert game_eval.choices

    def test_activate_continues_when_team_reached_66_but_adu_is_in(self, game_eval: GameEval, player: Player):
        player.score = 66
        game_eval.game.is_adu_out = False
        game_eval.activate()
        assert game_eval.game.outcome == {}
        assert game_eval.choices

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

    def test_activate_adds_round_when_previous_is_round_eval(
        self, game_eval_after_round_eval: GameEval, round_eval: RoundEval, player: Player
    ):
        game_eval_after_round_eval.activate()
        assert round_eval.next is game_eval_after_round_eval
        assert game_eval_after_round_eval.game.outcome == {}
        assert len(game_eval_after_round_eval.choices) == 1
        next_round = game_eval_after_round_eval.choices[0]
        assert isinstance(next_round, Round)
        assert next_round.previous is game_eval_after_round_eval
        assert next_round.player is player
        assert next_round.next is None
        assert next_round.choices == []

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
