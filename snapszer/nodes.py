from snapszer.cards import Card, Rank, Suit
from snapszer.game import Game
from snapszer.players import Player


class Node:
    def __init__(self, previous: Node):
        self.previous = previous
        self.next = None
        self.choices = []

    def activate(self):
        raise NotImplementedError

    def deactivate(self):
        raise NotImplementedError

    @property
    def game(self) -> Game:
        return self.previous.game

    @property
    def round(self) -> Round | None:
        return self.previous.round


class Root(Node):
    previous: None
    next: Round | None
    choices: list[Round]

    def __init__(self, adu: Card, players: list[Player]):
        super().__init__(None)
        self._game = Game(adu, players)

    def activate(self):
        starting_player = self.game.players[0]
        self.choices = [Round(self, starting_player)]

    def deactivate(self):
        self.choices.clear()

    @property
    def game(self) -> Game:
        return self._game

    @property
    def round(self) -> None:
        return None


class Round(Node):
    previous: Root | GameEval
    next: Play | Bonus | None
    choices: list[Play | Bonus]

    def __init__(self, previous: Root | GameEval, player: Player):
        super().__init__(previous)
        self.player = player
        self.plays: list[Play] = []
        self.value = 0

    def activate(self):
        self.previous.next = self
        self.choices = [Play(self, self.player, card) for card in self.player.hand]
        for suit in Suit:
            bonus_cards = {Card(suit, Rank.FELSO), Card(suit, Rank.KIRALY)}
            if bonus_cards.issubset(self.player.hand):
                self.choices.extend(Bonus(self, self.player, card) for card in bonus_cards)

    def deactivate(self):
        self.previous.next = None
        self.choices.clear()

    @property
    def winning_play(self) -> Play:
        winning, *rest = self.plays
        for play in rest:
            if play.card.beats(winning.card, self.game.adu.suit):
                winning = play
        return winning

    @property
    def round(self) -> Round:
        return self


class Play(Node):
    previous: Round | Play | GameEval
    next: Play | RoundEval | None
    choices: list[Play | RoundEval]

    def __init__(self, previous: Round | Play | GameEval, player: Player, card: Card):
        super().__init__(previous)
        self.player = player
        self.card = card

    def activate(self):
        self.previous.next = self
        self.player.hand.remove(self.card)
        self.round.plays.append(self)
        self.round.value += self.card.value
        if self.card == self.game.adu:
            self.game.is_adu_out = True
        if len(self.round.plays) == Game.PLAYER_COUNT:
            self.choices = [RoundEval(self)]
        else:
            challenger_card = self.round.plays[0].card
            winning_card = self.round.winning_play.card
            if challenger_suited_cards := {card for card in self.player.next.hand if card.suit == challenger_card.suit}:
                if winning_cards := {card for card in challenger_suited_cards if card.beats(winning_card, self.game.adu.suit)}:
                    self.choices = [Play(self, self.player.next, card) for card in winning_cards]
                else:
                    self.choices = [Play(self, self.player.next, card) for card in challenger_suited_cards]
            elif adu_suited_cards := {card for card in self.player.next.hand if card.suit == self.game.adu.suit}:
                if winning_cards := {card for card in adu_suited_cards if card.beats(winning_card, self.game.adu.suit)}:
                    self.choices = [Play(self, self.player.next, card) for card in winning_cards]
                else:
                    self.choices = [Play(self, self.player.next, card) for card in adu_suited_cards]
            else:
                self.choices = [Play(self, self.player.next, card) for card in self.player.next.hand]

    def deactivate(self):
        self.previous.next = None
        self.player.hand.add(self.card)
        self.round.plays.pop()
        self.round.value -= self.card.value
        if self.card == self.game.adu:
            self.game.is_adu_out = False
        self.choices.clear()


class Bonus(Node):
    previous: Round
    next: GameEval | None
    choices: list[GameEval]

    def __init__(self, previous: Round, player: Player, card: Card):
        super().__init__(previous)
        self.player = player
        self.card = card
        self.score = 40 if self.card.suit == self.game.adu.suit else 20

    def activate(self):
        self.previous.next = self
        self.player.bonus_score += self.score
        self.choices = [GameEval(self, self.player)]

    def deactivate(self):
        self.previous.next = None
        self.player.bonus_score -= self.score
        self.choices.clear()


class RoundEval(Node):
    previous: Play
    next: GameEval | None
    choices: list[GameEval]

    def __init__(self, previous: Play):
        super().__init__(previous)
        self.player = self.round.winning_play.player

    def activate(self):
        self.previous.next = self
        self.player.score += self.round.value
        self.choices = [GameEval(self, self.player)]

    def deactivate(self):
        self.previous.next = None
        self.player.score -= self.round.value
        self.choices.clear()


class GameEval(Node):
    previous: Bonus | RoundEval
    next: Round | Play | None
    choices: list[Round | Play]

    def __init__(self, previous: Bonus | RoundEval, player: Player):
        super().__init__(previous)
        self.player = player

    def activate(self):
        self.previous.next = self
        if self.player.hand_size == 0 or (self.game.is_adu_out and self.player.team_score >= 66):
            opponent_team_score = self.player.opponent_team_score
            if opponent_team_score == 0:
                points = 3
            elif opponent_team_score < 33:
                points = 2
            else:
                points = 1
            self.game.outcome = {player: points if player in self.player.team else 0 for player in self.game.players}
        elif isinstance(self.previous, Bonus):
            self.choices = [Play(self, self.player, self.previous.card)]
        else:
            self.choices = [Round(self, self.player)]

    def deactivate(self):
        self.previous.next = None
        self.game.outcome.clear()
        self.choices.clear()
