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
    def __init__(self, previous: Root, player: Player, card: Card):
        super().__init__(previous)
        self.player = player
        self.card = card


class Bonus(Node):
    def __init__(self, previous: Root, player: Player, card: Card):
        super().__init__(previous)
        self.player = player
        self.card = card
