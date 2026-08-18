"""Snapszer players."""

from snapszer.cards import DECK, Card

PLAYER_COUNT = 4
"""
Number of players in a game of Snapszer.
This library only supports 4 player mode.
"""


class Player:
    """Snapszer player."""

    def __init__(self, name: str, hand: set[Card]) -> None:
        """Initialize a player."""
        self.validate_starting_hand_size(hand)
        self._name = name
        self.hand = hand
        self.score: int = 0
        self.bonus_score: int = 0
        self.previous: Player = None
        self.next: Player = None

    @property
    def name(self) -> str:
        """Name of the player."""
        return self._name

    @classmethod
    def validate_starting_hand_size(cls, hand: set[Card]) -> None:
        """Validate the size of a starting hand."""
        hand_size = len(hand)
        expected_hand_size = len(DECK) // PLAYER_COUNT
        if hand_size != expected_hand_size:
            error_message = f"Hand size must be {expected_hand_size}, got {hand_size}"
            raise ValueError(error_message)
