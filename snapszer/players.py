from snapszer.cards import Card


class Player:
    def __init__(self, name: str, hand: set[Card]) -> None:
        self.name = name
        self.hand = hand
        self.score: int = 0
        self.bonus_score: int = 0
        self.previous: Player = None
        self.next: Player = None

    def __str__(self) -> str:
        return self.name
