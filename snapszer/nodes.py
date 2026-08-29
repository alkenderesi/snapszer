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


class Root(Node):
    previous: None
    next: Play | Bonus | None
    choices: list[Play | Bonus]

    def __init__(self, adu: Card, players: list[Player]):
        super().__init__(None)
        self._game = Game(adu, players)

    def activate(self):
        starting_player = self.game.players[0]
        self.choices = [Play(self, starting_player, card) for card in starting_player.hand]
        for suit in Suit:
            bonus_cards = {Card(suit, Rank.FELSO), Card(suit, Rank.KIRALY)}
            if bonus_cards.issubset(starting_player.hand):
                self.choices.extend(Bonus(self, starting_player, card) for card in bonus_cards)

    def deactivate(self):
        self.choices.clear()

    @property
    def game(self) -> Game:
        return self._game


class Play(Node):
    previous: Root | GameEval | Play
    next: Play | RoundEval | None
    choices: list[Play | RoundEval]

    def __init__(self, previous: Root | GameEval | Play, player: Player, card: Card):
        super().__init__(previous)
        self.player = player
        self.card = card


class Bonus(Node):
    previous: Root | GameEval
    next: GameEval | None
    choices: list[GameEval]

    def __init__(self, previous: Root | GameEval, player: Player, card: Card):
        super().__init__(previous)
        self.player = player
        self.card = card
        self.score = 40 if self.card.rank == self.game.adu.rank else 20

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

    def __init__(self, previous: Play, player: Player):
        super().__init__(previous)
        self.player = player


class GameEval(Node):
    previous: Bonus | RoundEval
    next: Play | Bonus | None
    choices: list[Play | Bonus]

    def __init__(self, previous: Bonus | RoundEval, player: Player):
        super().__init__(previous)
        self.player = player

    def activate(self):
        self.previous.next = self
        if self.is_game_over():
            if self.player.opponent_team_score == 0:
                winner_points = 3
            elif self.player.opponent_team_score < 33:
                winner_points = 2
            else:
                winner_points = 1
            self.game.outcome = {
                player: winner_points if player in self.player.team else 0 for player in self.game.players
            }
        elif isinstance(self.previous, Bonus):
            self.choices = [Play(self, self.player, self.previous.card)]
        else:
            self.choices = [Play(self, self.player, card) for card in self.player.hand]
            for suit in Suit:
                bonus_cards = {Card(suit, Rank.FELSO), Card(suit, Rank.KIRALY)}
                if bonus_cards.issubset(self.player.hand):
                    self.choices.extend(Bonus(self, self.player, card) for card in bonus_cards)

    def deactivate(self):
        self.previous.next = None
        if self.is_game_over():
            self.game.outcome.clear()
        else:
            self.choices.clear()

    def is_game_over(self) -> bool:
        return len(self.player.hand) == 0 or (self.game.is_adu_out and self.player.team_score >= 66)
