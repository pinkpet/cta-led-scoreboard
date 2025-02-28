from datetime import datetime
from nhl_api import game_status_info, current_season_info
import debug

class Status:
    def __init__(self):
        game_status = game_status_info()
        self.season_info = current_season_info()['seasons'][0]
        self.season_id = self.season_info["seasonId"]
        self.Preview = []
        self.Live = []
        self.GameOver = []
        self.Final = []
        self.Irregular = []

        for status in game_status:
            if status['code'] == '8' or status['code'] == '9':
                self.Irregular.append(status['detailedState'])
            elif status['abstractGameState'] == "Preview":
                self.Preview.append(status['detailedState'])
            elif status['abstractGameState'] == 'Live':
                self.Live.append(status['detailedState'])
            elif status['abstractGameState'] == 'Final':
                # since July 2020, status code 6 is no longer part of Game over but Final
                if status['code'] == '5':
                    self.GameOver.append(status['detailedState'])
                else:
                    self.Final.append(status['detailedState'])


    def is_scheduled(self, status):
        return status in self.Preview

    def is_live(self, status):
        return status in self.Live

    def is_game_over(self, status):
        return status in self.GameOver

    def is_final(self, status):
        return status in self.Final

    def is_irregular(self, status):
        return status in self.Irregular

    def is_offseason(self, date):
        try:
            regular_season_startdate = datetime.strptime(self.season_info['regularSeasonStartDate'], "%Y-%m-%d").date()
            end_of_season = datetime.strptime(self.season_info['seasonEndDate'], "%Y-%m-%d").date()
            return date < regular_season_startdate or date > end_of_season
        except:
            debug.error('The Argument provided for status.is_offseason is missing or not right.')
            return False
