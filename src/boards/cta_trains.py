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
                },
                {
                    "Dest": "For. Park",
                    "Time": "18 mins"
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
            prev_game = team.previous_game
            next_game = team.next_game

            stats = team.stats
            im_height = 64
            team_abbrev = team.abbreviation
            team_logo = Image.open(get_file('assets/logos/{}.png'.format(team_abbrev)))

            i = 0

            if not self.sleepEvent.is_set():
                #Create images for the train scroller
                image_train_top_two = self.draw_train_times(
                    trains,
                    0,
                    2
                )

                image_train_bottom_rest = self.draw_train_times(
                    trains,
                    2,
                    len(trains)
                )
                print(len(trains))
                print(len(trains))
                print(len(trains))

                #cta SCROLLER!
                cta_logo_image = Image.open(get_file('assets/images/quad-ctas.png'))
                cta_img_width, cta_img_height = cta_logo_image.size
                cta_xpos = 0
                while cta_xpos < cta_img_width:
                    cta_xpos += 1
                    self.matrix.clear()
                    self.matrix.draw_image((-cta_xpos, 0), cta_logo_image, "top-left")
                    self.matrix.render()
                    self.sleepEvent.wait(0.02)

                # bottom bar rectangle --TO DO add weather, time
                image_bottom_bar = Image.new('RGB', (64,12))
                draw = ImageDraw.Draw(image_bottom_bar)
                draw.rectangle([0, 0, 64, 30], fill=(0, 157, 220))

                self.matrix.clear()

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_train_top_two,
                )

                # ***START HERE the goal is to use the same function and have it put the two fixed trains and then the revolving trains below it.
                # self.matrix.draw_image_layout(
                #     self.layout.info,
                #     image_train_bottom_rest,
                #     (0, 15)
                # )

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_bottom_bar,
                    (0, 22)
                )

                self.matrix.render()

            self.matrix.render()

            self.sleepEvent.wait(3)

            # Move the image up until we hit the bottom.
            train_scroller_height = len(trains) * 7
            while i > -(train_scroller_height - 21):
                i -= 1

                self.matrix.clear()

                self.matrix.draw_image_layout(
                self.layout.info,
                image_train_top_two,
                (0, i)
                )

                self.matrix.draw_image_layout(
                self.layout.info,
                image_bottom_bar,
                (0, 22)
                )

                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

                self.sleepEvent.wait(0.3)

            # Show the bottom before we change to the next table.
            self.sleepEvent.wait(5)

    def draw_train_times(self, cta_data, train_start, train_max):
        image = Image.new('RGB', (64, train_max * 7))
        draw = ImageDraw.Draw(image)

        pos = 0
        loop_count = 0 + train_start
        while loop_count < train_max:
            draw.text((1, pos), "{}".format(cta_data[loop_count]['Dest']), fill=(255, 255, 255), font=self.font, align="right")
            draw.text((40,pos), "{}".format(cta_data[loop_count]['Time']), fill=(255, 255, 255), font=self.font, align="center")
            pos += 7
            print(str(loop_count)+" worked")
            loop_count += 1
        print(cta_data)

        return image
