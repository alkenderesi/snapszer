from snapszer.cards import DECK, Card
from snapszer.players import Player


class Game:
    PLAYER_COUNT = 4

    def __init__(self, adu: Card, players: list[Player]):
        self._validate_player_count(players)
        self._validate_player_hand_sizes(players)
        self._validate_dealt_cards(players)
        self.adu = adu
        self.players = players
        self.adu_team: set[Player] = set()
        self.non_adu_team: set[Player] = set()
        self._assign_teams()
        self._link_players()

    @staticmethod
    def _validate_player_count(players: list[Player]):
        player_count = len(players)
        if player_count != Game.PLAYER_COUNT:
            error_message = f"Number of players must be {Game.PLAYER_COUNT}, got {player_count}"
            raise ValueError(error_message)

    @staticmethod
    def _validate_player_hand_sizes(players: list[Player]):
        expected_hand_size = len(DECK) // Game.PLAYER_COUNT
        for player in players:
            if player.hand_size != expected_hand_size:
                error_message = f"Player {player.name} must have {expected_hand_size} cards, got {player.hand_size}"
                raise ValueError(error_message)

    @staticmethod
    def _validate_dealt_cards(players: list[Player]):
        dealt_cards = set.union(*(player.hand for player in players))
        if undealt_cards := DECK - dealt_cards:
            error_message = f"Undealt cards: {', '.join(sorted(str(card) for card in undealt_cards))}"
            raise ValueError(error_message)

    def _assign_teams(self):
        starting_player, *other_players = self.players
        self.adu_team.add(starting_player)
        for player in other_players:
            if self.adu in player.hand:
                self.adu_team.add(player)
            else:
                self.non_adu_team.add(player)

    def _link_players(self):
        for i, player in enumerate(self.players):
            player.previous = self.players[(i - 1) % Game.PLAYER_COUNT]
            player.next = self.players[(i + 1) % Game.PLAYER_COUNT]
