from snapszer.game import Game


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
