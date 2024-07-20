from typing import Any

from player_data import PlayerData

class MatchResults:
    def __init__(self, axis_team_name: str, allies_team_name: str, map_name: str, match_date: str):
        self.results = {
            'Axis': self._create_team_dict(axis_team_name),
            'Allies': self._create_team_dict(allies_team_name),
            'Spectators': [],
            'Map': map_name,
            'Match Date': match_date
        }

    @staticmethod
    def _create_team_dict(team_name: str) -> dict[str, Any]:
        return {
            'Team Name': team_name,
            'Total': MatchResults._create_stats_dict(include_players=False),
            'Infantry': MatchResults._create_stats_dict(),
            'Artillery': MatchResults._create_stats_dict(),
            'Armor': MatchResults._create_stats_dict(),
            'Unknown': MatchResults._create_stats_dict()
        }

    @staticmethod
    def _create_stats_dict(include_players: bool = True) -> dict[str, Any]:
        stats = {
            'PlayerCount': 0,
            'Kills': 0,
            'Deaths': 0,
            'KDR': 0.0,
            'CombatEffectiveness': 0,
            'OffensivePoints': 0,
            'DefensivePoints': 0,
            'SupportPoints': 0,
            'MachineGunKills': 0
        }
        if include_players:
            stats['Players'] = []
        return stats

    def add_player(self, player: PlayerData):
        if player.side == 'Spectators':
            self.results['Spectators'].append(player.to_dict())
        else:
            side = self.results[player.side]
            group = side[player.group]
            self._update_stats(group, player)
            group['Players'].append(player.to_dict())
            self._update_stats(side['Total'], player)

    @staticmethod
    def _update_stats(stats: dict[str, Any], player: PlayerData):
        stats['PlayerCount'] += 1
        stats['Kills'] += player.kills
        stats['Deaths'] += player.deaths
        stats['CombatEffectiveness'] += player.combat_effectiveness
        stats['OffensivePoints'] += player.offensive_points
        stats['DefensivePoints'] += player.defensive_points
        stats['SupportPoints'] += player.support_points
        stats['MachineGunKills'] += player.machine_gun_kills

    def calculate_kdrs(self):
        for side in ['Axis', 'Allies']:
            for group in ['Total', 'Infantry', 'Artillery', 'Armor', 'Unknown']:
                stats = self.results[side][group]
                kills = stats['Kills']
                deaths = stats['Deaths']
                stats['KDR'] = self.calculate_kdr(kills, deaths)

    @staticmethod
    def calculate_kdr(kills: int, deaths: int) -> str:
        denominator = 1 if deaths == 0 else deaths
        return format(kills / denominator, '.2f')

    def to_dict(self) -> dict[str, Any]:
        return self.results