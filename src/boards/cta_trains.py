"""
    Show a summary of the favorite team. (previous game, next game, stats,)

"""
from PIL import Image, ImageFont, ImageDraw, ImageOps
from rgbmatrix import graphics
import nhl_api
from data.scoreboard import Scoreboard
from data.team import Team
from time import sleep
from utils import convert_date_format, get_file
from renderer.logos import LogoRenderer

class CtaTrainTracker:
    def __init__(self, data, matrix,sleepEvent):
        '''
            TODO:
                Need to move the Previous/Next game info in the data section. I think loading it in the data section
                and then taking that info here would make sense
        '''
        self.data = data
        self.teams_info = data.teams_info
        self.preferred_teams = data.pref_teams
        self.matrix = matrix
        self.team_colors = data.config.team_colors

        self.font = data.config.layout.font
        self.layout = data.config.config.layout.get_board_layout('cta_tracker')

        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()

    def render(self):
        for team_id in self.preferred_teams:

            trains = [
                {
                    "Dest": "For. Park",
                    "Time": "2 mins"
                },
                {
                    "Dest": "O'Hare",
                    "Time": "4 mins"
                },
                {
                    "Dest": "UIC Hals.",
                    "Time": "6 mins"
                },
                {
                    "Dest": "Rosemont",
                    "Time": "9 mins"
                }
            ]


            self.team_id = team_id

            team = self.teams_info[team_id]
            team_data = Team(
                team.team_id,
                team.abbreviation,
                team.name
            )

            team_colors = self.data.config.team_colors
            bg_color = team_colors.color("{}.primary".format(team_id))
            txt_color = team_colors.color("{}.text".format(team_id))
            prev_game = team.previous_game
            next_game = team.next_game

            logo_renderer = LogoRenderer(
                self.matrix,
                self.data.config,
                self.layout.logo,
                team_data,
                'team_summary'
            )

            try:
                if prev_game:
                    prev_game_id = self.teams_info[team_id].previous_game.dates[0]["games"][0]["gamePk"]
                    prev_game_scoreboard = Scoreboard(nhl_api.overview(prev_game_id), self.data)
                else:
                    prev_game_scoreboard = False

                self.data.network_issues = False
            except ValueError:
                prev_game_scoreboard = False
                self.data.network_issues = True

            stats = team.stats
            im_height = 64
            team_abbrev = team.abbreviation
            team_logo = Image.open(get_file('assets/logos/{}.png'.format(team_abbrev)))

            i = 0

            if not self.sleepEvent.is_set():
                image = self.draw_train_times(
                    trains,
                    bg_color,
                    txt_color,
                    im_height
                )

                image_bottom_bar = self.draw_bottom_bar()

                self.matrix.clear()

                logo_renderer.render()

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image,
                )

                self.matrix.draw_image_layout(
                self.layout.info,
                image_bottom_bar,
                (0, 24)
                )

                # self.matrix.draw.rectangle([0, 0, self.matrix.width, 8], fill=(250, 0, 0))

                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

            # self.matrix.draw.rectangle([0, 23, self.matrix.width, self.matrix.height], fill=(0, 0, 205))
            self.matrix.render()

            self.sleepEvent.wait(5)

            # Move the image up until we hit the bottom.
            while i > -(im_height - self.matrix.height) and not self.sleepEvent.is_set():
                i -= 1

                self.matrix.clear()

                logo_renderer.render()

                self.matrix.draw_image_layout(
                self.layout.info,
                image,
                (0, i)
                )

                self.matrix.draw_image_layout(
                self.layout.info,
                image_bottom_bar,
                (0, 24)
                )

                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

                self.sleepEvent.wait(0.3)

            # Show the bottom before we change to the next table.
            self.sleepEvent.wait(5)

    def draw_train_times(self, cta_data, bg_color, txt_color, im_height):

        train_scroller_height = len(cta_data) * 8

        image = Image.new('RGB', (64, train_scroller_height))
        draw = ImageDraw.Draw(image)

        pos = 0
        for train in cta_data:
            draw.text((1, pos), "{}  {}".format(train['Dest'], train['Time']), fill=(255, 255, 255), font=self.font)
            pos += 7

        print(cta_data)

        return image

    def draw_bottom_bar(self):
        image_bottom_bar = Image.new('RGB', (64,32))
        draw = ImageDraw.Draw(image_bottom_bar)

        draw.rectangle([0, 0, 64, 30], fill=(0, 157, 220))

        cta_logo_image = Image.open(get_file('assets/images/quad-ctas.png'))
        self.matrix.draw_image((0, 0), cta_logo_image, "top-left")
        self.matrix.render()
        self.sleepEvent.wait(5)
        print("Sleeping now...do you see the CTA?")

        self.matrix.render()
        print('ya it happened')

        return image_bottom_bar
