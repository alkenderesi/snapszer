from types import SimpleNamespace

import pytest

from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.nodes import Bonus, GameEval, Node, Play, Root, Round, RoundEval
from snapszer.players import Player
from tests.fixtures import NodeFixtures, four_players


class TestNode:
    def test_delegates_game_and_round_to_previous(self):
        previous = SimpleNamespace(game=object(), round=object())
        node = Node(previous)
        assert node.game is previous.game
        assert node.round is previous.round

    def test_activate_and_deactivate_are_not_implemented(self):
        node = Node(SimpleNamespace())
        with pytest.raises(NotImplementedError):
            node.activate()
        with pytest.raises(NotImplementedError):
            node.deactivate()


class TestRoot(NodeFixtures):
    def test_owns_the_game(self, root: Root, players: list[Player]):
        assert isinstance(root.game, Game)
        assert root.game.adu is self.adu
        assert root.game.players is players
        assert root.round is None

    def test_activate_adds_round_for_starting_player(self, root: Root, players: list[Player]):
        root.activate()
        assert len(root.choices) == 1
        round_node = root.choices[0]
        assert isinstance(round_node, Round)
        assert round_node.previous is root
        assert round_node.player is players[0]

    def test_deactivate_clears_choices(self, root: Root):
        root.activate()
        assert root.choices
        root.deactivate()
        assert root.choices == []


class TestRound(NodeFixtures):
    def test_activate_adds_play_choices_for_each_card(self, round_node: Round, root: Root, players: list[Player]):
        player = players[0]
        round_node.activate()
        assert root.next is round_node
        plays = [choice for choice in round_node.choices if isinstance(choice, Play)]
        assert {play.card for play in plays} == player.hand
        assert all(play.player is player for play in plays)

    def test_no_bonus_choices(self, round_node: Round, players: list[Player]):
        a, b, *_ = players
        kiraly = Card(Suit.PIROS, Rank.KIRALY)
        zold_asz = Card(Suit.ZOLD, Rank.ASZ)
        a.hand.remove(kiraly)
        b.hand.remove(zold_asz)
        a.hand.add(zold_asz)
        b.hand.add(kiraly)
        round_node.activate()
        assert not any(isinstance(choice, Bonus) for choice in round_node.choices)

    def test_one_bonus_pair(self, round_node: Round):
        round_node.activate()
        bonuses = [choice for choice in round_node.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
        }

    def test_two_bonus_pairs(self, round_node: Round, players: list[Player]):
        a, b, *_ = players
        piros_ix = Card(Suit.PIROS, Rank.IX)
        piros_also = Card(Suit.PIROS, Rank.ALSO)
        zold_felso = Card(Suit.ZOLD, Rank.FELSO)
        zold_kiraly = Card(Suit.ZOLD, Rank.KIRALY)
        a.hand.remove(piros_ix)
        a.hand.remove(piros_also)
        b.hand.remove(zold_felso)
        b.hand.remove(zold_kiraly)
        a.hand.add(zold_felso)
        a.hand.add(zold_kiraly)
        b.hand.add(piros_ix)
        b.hand.add(piros_also)
        round_node.activate()
        bonuses = [choice for choice in round_node.choices if isinstance(choice, Bonus)]
        assert {bonus.card for bonus in bonuses} == {
            Card(Suit.PIROS, Rank.FELSO),
            Card(Suit.PIROS, Rank.KIRALY),
            zold_felso,
            zold_kiraly,
        }

    def test_deactivate_clears_choices(self, round_node: Round, root: Root):
        round_node.activate()
        assert round_node.choices
        round_node.deactivate()
        assert root.next is None
        assert round_node.choices == []

    def test_winning_play_walks_the_round(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        first = Play(round_node, a, Card(Suit.ZOLD, Rank.ASZ))
        second = Play(first, b, Card(Suit.TOK, Rank.X))
        third = Play(second, c, Card(Suit.PIROS, Rank.IX))
        fourth = Play(third, d, Card(Suit.PIROS, Rank.X))
        round_node.plays.extend([first, second, third, fourth])
        assert round_node.winning_play is fourth


class TestBonus(NodeFixtures):
    def test_score_is_40_for_adu(self, round_node: Round, players: list[Player]):
        assert Bonus(round_node, players[0], Card(Suit.PIROS, Rank.FELSO)).score == 40

    def test_score_is_20_for_non_adu(self, round_node: Round, players: list[Player]):
        assert Bonus(round_node, players[0], Card(Suit.ZOLD, Rank.FELSO)).score == 20

    def test_activate_adds_bonus_score(self, round_node: Round, players: list[Player]):
        player = players[0]
        bonus = Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO))
        bonus.activate()
        assert round_node.next is bonus
        assert player.bonus_score == 40
        assert len(bonus.choices) == 1
        assert isinstance(bonus.choices[0], GameEval)

    def test_deactivate_reverts_score(self, round_node: Round, players: list[Player]):
        player = players[0]
        bonus = Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO))
        bonus.activate()
        bonus.deactivate()
        assert player.bonus_score == 0
        assert bonus.choices == []
        assert round_node.next is None


class TestPlay(NodeFixtures):
    def test_updates_round_and_hand(self, round_node: Round, players: list[Player]):
        player = players[0]
        card = Card(Suit.PIROS, Rank.X)
        play = Play(round_node, player, card)
        play.activate()
        assert round_node.next is play
        assert card not in player.hand
        assert round_node.plays == [play]
        assert round_node.value == card.value
        assert play.game.is_adu_out is False
        assert {choice.card for choice in play.choices} == player.next.hand

    def test_playing_adu_marks_it_out(self, round_node: Round, players: list[Player]):
        player = players[0]
        play = Play(round_node, player, Card(Suit.PIROS, Rank.ASZ))
        play.activate()
        assert play.card not in player.hand
        assert play.game.is_adu_out is True

    def test_deactivate_reverts_non_adu(self, round_node: Round, players: list[Player]):
        player = players[0]
        card = Card(Suit.PIROS, Rank.X)
        play = Play(round_node, player, card)
        play.activate()
        play.deactivate()
        assert card in player.hand
        assert round_node.plays == []
        assert round_node.value == 0
        assert play.game.is_adu_out is False
        assert play.choices == []
        assert round_node.next is None

    def test_deactivate_reverts_adu(self, round_node: Round, players: list[Player]):
        player = players[0]
        card = Card(Suit.PIROS, Rank.ASZ)
        play = Play(round_node, player, card)
        play.activate()
        play.deactivate()
        assert card in player.hand
        assert round_node.plays == []
        assert round_node.value == 0
        assert play.game.is_adu_out is False
        assert play.choices == []
        assert round_node.next is None

    def test_follow_and_beat(self, round_node: Round, players: list[Player]):
        a, b, *_ = players
        piros_asz = Card(Suit.PIROS, Rank.ASZ)
        zold_asz = Card(Suit.ZOLD, Rank.ASZ)
        a.hand.remove(piros_asz)
        b.hand.remove(zold_asz)
        a.hand.add(zold_asz)
        b.hand.add(piros_asz)
        first = Play(round_node, a, Card(Suit.PIROS, Rank.IX))
        first.activate()
        assert {choice.card for choice in first.choices} == {piros_asz}

    def test_follow_only(self, round_node: Round, players: list[Player]):
        a, b, *_ = players
        piros_nine = Card(Suit.PIROS, Rank.IX)
        zold_asz = Card(Suit.ZOLD, Rank.ASZ)
        a.hand.remove(piros_nine)
        b.hand.remove(zold_asz)
        a.hand.add(zold_asz)
        b.hand.add(piros_nine)
        first = Play(round_node, a, Card(Suit.PIROS, Rank.ASZ))
        first.activate()
        assert {choice.card for choice in first.choices} == {piros_nine}

    def test_adu_and_beat(self, round_node: Round, players: list[Player]):
        a, b, c, _ = players
        tok_nine = Card(Suit.TOK, Rank.IX)
        piros_nine = Card(Suit.PIROS, Rank.IX)
        piros_felso = Card(Suit.PIROS, Rank.FELSO)
        zold_nine = Card(Suit.ZOLD, Rank.IX)
        a.hand.remove(piros_nine)
        c.hand.remove(tok_nine)
        a.hand.add(tok_nine)
        c.hand.add(piros_nine)
        a.hand.remove(piros_felso)
        b.hand.remove(zold_nine)
        a.hand.add(zold_nine)
        b.hand.add(piros_felso)
        first = Play(round_node, a, tok_nine)
        first.activate()
        assert {choice.card for choice in first.choices} == {piros_felso}

    def test_adu_only(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        makk_nine = Card(Suit.MAKK, Rank.IX)
        piros_nine = Card(Suit.PIROS, Rank.IX)
        piros_asz = Card(Suit.PIROS, Rank.ASZ)
        zold_asz = Card(Suit.ZOLD, Rank.ASZ)
        tok_nine = Card(Suit.TOK, Rank.IX)
        a.hand.remove(piros_nine)
        c.hand.remove(tok_nine)
        a.hand.add(tok_nine)
        c.hand.add(piros_nine)
        a.hand.remove(piros_asz)
        b.hand.remove(zold_asz)
        a.hand.add(zold_asz)
        b.hand.add(piros_asz)
        a.hand.remove(tok_nine)
        d.hand.remove(makk_nine)
        a.hand.add(makk_nine)
        d.hand.add(tok_nine)
        first = Play(round_node, a, makk_nine)
        first.activate()
        adu = Play(first, b, piros_asz)
        adu.activate()
        assert {choice.card for choice in adu.choices} == {piros_nine}

    def test_any_card_when_unable_to_follow_or_adu(self, round_node: Round, players: list[Player]):
        a, b, *_ = players
        first = Play(round_node, a, Card(Suit.PIROS, Rank.IX))
        first.activate()
        assert {choice.card for choice in first.choices} == b.hand

    def test_round_eval_after_fourth_play(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        first = Play(round_node, a, Card(Suit.PIROS, Rank.X))
        first.activate()
        second = Play(first, b, Card(Suit.ZOLD, Rank.ASZ))
        second.activate()
        third = Play(second, c, Card(Suit.TOK, Rank.ASZ))
        third.activate()
        fourth = Play(third, d, Card(Suit.MAKK, Rank.ASZ))
        fourth.activate()
        assert len(fourth.choices) == 1
        round_eval = fourth.choices[0]
        assert isinstance(round_eval, RoundEval)
        assert round_eval.previous is fourth
        assert round_eval.player is a


class TestRoundEval(NodeFixtures):
    def test_credits_the_round_winner(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        tok_nine = Card(Suit.TOK, Rank.IX)
        piros_nine = Card(Suit.PIROS, Rank.IX)
        piros_asz = Card(Suit.PIROS, Rank.ASZ)
        zold_asz = Card(Suit.ZOLD, Rank.ASZ)
        a.hand.remove(piros_nine)
        c.hand.remove(tok_nine)
        a.hand.add(tok_nine)
        c.hand.add(piros_nine)
        a.hand.remove(piros_asz)
        b.hand.remove(zold_asz)
        a.hand.add(zold_asz)
        b.hand.add(piros_asz)
        first = Play(round_node, a, tok_nine)
        first.activate()
        adu = Play(first, b, piros_asz)
        adu.activate()
        third = Play(adu, c, Card(Suit.TOK, Rank.ASZ))
        third.activate()
        fourth = Play(third, d, Card(Suit.MAKK, Rank.ASZ))
        fourth.activate()
        round_eval = fourth.choices[0]
        assert round_eval.player is b
        round_eval.activate()
        assert b.score == round_node.value
        assert a.score == 0

    def test_one_round_then_next_round(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        first = Play(round_node, a, Card(Suit.PIROS, Rank.X))
        first.activate()
        second = Play(first, b, Card(Suit.ZOLD, Rank.ASZ))
        second.activate()
        third = Play(second, c, Card(Suit.TOK, Rank.ASZ))
        third.activate()
        fourth = Play(third, d, Card(Suit.MAKK, Rank.ASZ))
        fourth.activate()
        round_eval = fourth.choices[0]
        assert isinstance(round_eval, RoundEval)
        round_eval.activate()
        game_eval = round_eval.choices[0]
        assert isinstance(game_eval, GameEval)
        game_eval.activate()
        next_round = game_eval.choices[0]
        assert isinstance(next_round, Round)
        assert next_round.player is a

    def test_deactivate_reverts_score(self, round_node: Round, players: list[Player]):
        player = players[0]
        play = Play(round_node, player, Card(Suit.PIROS, Rank.ASZ))
        play.activate()
        round_eval = RoundEval(play)
        round_eval.activate()
        round_eval.deactivate()
        assert play.next is None
        assert player.score == 0
        assert round_eval.choices == []


class TestGameEval(NodeFixtures):
    def test_ends_when_hand_is_empty(self, round_node: Round, players: list[Player]):
        player = players[0]
        game_eval = GameEval(Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO)), player)
        player.hand.clear()
        game_eval.activate()
        assert game_eval.choices == []
        assert game_eval.game.outcome[player] > 0

    def test_ends_when_adu_out_and_66(self, round_node: Round, players: list[Player]):
        player = players[0]
        game_eval = GameEval(Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO)), player)
        player.score = 66
        game_eval.game.is_adu_out = True
        game_eval.activate()
        assert game_eval.choices == []
        assert game_eval.game.outcome[player] > 0

    def test_ends_when_hits_plus_bonus_reach_66(self, round_node: Round, players: list[Player]):
        player = players[0]
        game_eval = GameEval(Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO)), player)
        player.score = 46
        player.bonus_score = 20
        game_eval.game.is_adu_out = True
        game_eval.activate()
        assert game_eval.choices == []
        assert game_eval.game.outcome[player] > 0

    def test_continues_when_adu_out_and_65(self, round_node: Round, players: list[Player]):
        player = players[0]
        game_eval = GameEval(Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO)), player)
        player.score = 65
        game_eval.game.is_adu_out = True
        game_eval.activate()
        assert game_eval.game.outcome == {}
        assert game_eval.choices

    def test_continues_when_adu_in_and_66(self, round_node: Round, players: list[Player]):
        player = players[0]
        game_eval = GameEval(Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO)), player)
        player.score = 66
        game_eval.game.is_adu_out = False
        game_eval.activate()
        assert game_eval.game.outcome == {}
        assert game_eval.choices

    def test_continues_when_only_bonuses(self, round_node: Round, players: list[Player]):
        player = players[0]
        game_eval = GameEval(Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO)), player)
        player.bonus_score = 66
        game_eval.game.is_adu_out = True
        game_eval.activate()
        assert game_eval.game.outcome == {}
        assert game_eval.choices

    def test_awards_three_points_when_opponents_have_zero(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        game_eval = GameEval(Bonus(round_node, a, Card(Suit.PIROS, Rank.FELSO)), a)
        a.hand.clear()
        game_eval.activate()
        assert game_eval.game.outcome == {a: 3, b: 0, c: 0, d: 0}

    def test_awards_two_points_when_opponents_have_32(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        game_eval = GameEval(Bonus(round_node, a, Card(Suit.PIROS, Rank.FELSO)), a)
        a.hand.clear()
        b.score = 32
        game_eval.activate()
        assert game_eval.game.outcome == {a: 2, b: 0, c: 0, d: 0}

    def test_awards_one_point_when_opponents_have_33(self, round_node: Round, players: list[Player]):
        a, b, c, d = players
        game_eval = GameEval(Bonus(round_node, a, Card(Suit.PIROS, Rank.FELSO)), a)
        a.hand.clear()
        b.score = 33
        game_eval.activate()
        assert game_eval.game.outcome == {a: 1, b: 0, c: 0, d: 0}

    def test_awards_points_to_both_partners(self):
        players = four_players()
        a, b, c, d = players
        other = Card(Suit.ZOLD, Rank.ASZ)
        a.hand.remove(self.adu)
        a.hand.add(other)
        b.hand.remove(other)
        b.hand.add(self.adu)
        root = Root(self.adu, players)
        root.activate()
        round_node = root.choices[0]
        a.hand.clear()
        game_eval = GameEval(Bonus(round_node, a, Card(Suit.PIROS, Rank.FELSO)), a)
        game_eval.activate()
        assert game_eval.game.outcome == {a: 3, b: 3, c: 0, d: 0}

    def test_adds_play_after_bonus(self, round_node: Round, players: list[Player]):
        player = players[0]
        bonus = Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO))
        game_eval = GameEval(bonus, player)
        game_eval.activate()
        assert bonus.next is game_eval
        assert game_eval.game.outcome == {}
        assert len(game_eval.choices) == 1
        play = game_eval.choices[0]
        assert isinstance(play, Play)
        assert play.player is player
        assert play.card is bonus.card

    def test_adds_round_after_round_eval(self, round_node: Round, players: list[Player]):
        player = players[0]
        play = Play(round_node, player, Card(Suit.PIROS, Rank.ASZ))
        play.activate()
        round_eval = RoundEval(play)
        game_eval = GameEval(round_eval, player)
        game_eval.activate()
        assert round_eval.next is game_eval
        assert game_eval.game.outcome == {}
        assert len(game_eval.choices) == 1
        next_round = game_eval.choices[0]
        assert isinstance(next_round, Round)
        assert next_round.player is player

    def test_deactivate_clears_outcome(self, round_node: Round, players: list[Player]):
        player = players[0]
        bonus = Bonus(round_node, player, Card(Suit.PIROS, Rank.FELSO))
        game_eval = GameEval(bonus, player)
        player.hand.clear()
        game_eval.activate()
        game_eval.deactivate()
        assert bonus.next is None
        assert game_eval.game.outcome == {}
        assert game_eval.choices == []
