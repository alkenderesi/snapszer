"""Snapszer game."""

from snapszer.cards import DECK, Card
from snapszer.players import Player


class Game:
    """A game of Snapszer."""

    def __init__(self, adu: Card, players: tuple[Player, ...]) -> None:
        """Initialize a game."""
        self._validate_player_count(players)
        self._validate_starting_hand_sizes(players)
        self._validate_unique_player_names(players)
        self._validate_unique_player_cards(players)
        self._adu = adu
        self._players = players
        self.player_count = len(self.players)
        self._link_players()

    @property
    def adu(self) -> Card:
        """Adu card of the game."""
        return self._adu

    @property
    def players(self) -> tuple[Player, ...]:
        """Players of the game."""
        return self._players

    @staticmethod
    def _validate_player_count(players: tuple[Player, ...]) -> None:
        """Validate the number of players."""
        player_count = len(players)
        supported_player_counts = {4}
        if player_count not in supported_player_counts:
            error_message = (
                f"Player count must be one of {supported_player_counts}, "
                f"got {player_count}"
            )
            raise ValueError(error_message)

    @staticmethod
    def _validate_unique_player_names(players: tuple[Player, ...]) -> None:
        """Validate that all player names are unique."""
        names: set[str] = set()
        for player in players:
            name = player.name
            if name in names:
                error_message = f"Duplicate player name: {name}"
                raise ValueError(error_message)
            names.add(name)

    @staticmethod
    def _validate_starting_hand_sizes(players: tuple[Player, ...]) -> None:
        """Validate that all players start with the correct number of cards."""
        expected_hand_size = len(DECK) // len(players)
        for player in players:
            if player.hand_size != expected_hand_size:
                error_message = (
                    f"Player {player.name} has {player.hand_size} cards "
                    f"instead of {expected_hand_size}"
                )
                raise ValueError(error_message)

    @staticmethod
    def _validate_unique_player_cards(players: tuple[Player, ...]) -> None:
        """Validate that all players have unique cards."""
        cards: set[Card] = set()
        for player in players:
            for card in player.hand:
                if card in cards:
                    error_message = f"Duplicate card: {card}"
                    raise ValueError(error_message)
                cards.add(card)

    def _link_players(self) -> None:
        """Link the players together in a circle based on their order."""
        for i, player in enumerate(self.players):
            player.previous = self.players[(i - 1) % self.player_count]
            player.next = self.players[(i + 1) % self.player_count]
