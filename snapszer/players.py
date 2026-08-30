from snapszer.cards import Card


class Player:
    def __init__(self, name: str, hand: set[Card]):
        self.name = name
        self.hand = hand
        self.score: int = 0
        self.bonus_score: int = 0
        self.previous: Player = None
        self.next: Player = None
        self.team: set[Player] = {self}
        self.opponent_team: set[Player] = set()

    @property
    def hand_size(self) -> int:
        return len(self.hand)

    @property
    def team_score(self) -> int:
        return self._team_score(self.team)

    @property
    def opponent_team_score(self) -> int:
        return self._team_score(self.opponent_team)

    @staticmethod
    def _team_score(team: set[Player]) -> int:
        team_score = 0
        team_bonus_score = 0
        for player in team:
            team_score += player.score
            team_bonus_score += player.bonus_score
        return team_score + team_bonus_score if team_score > 0 else 0
