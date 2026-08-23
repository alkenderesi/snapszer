from snapszer.cards import Card
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

    @property
    def game(self) -> Game:
        return self._game
