# @"""
#     Show a summary of the favorite team. (previous game, next game, stats,)
#
# """
from PIL import Image, ImageFont, ImageDraw, ImageOps
from rgbmatrix import graphics
import nhl_api
import datetime
import random

from data.scoreboard import Scoreboard
from data.team import Team
from time import sleep
from utils import convert_date_format, get_file

class CtaTrainTracker:
    def __init__(self, data, matrix,sleepEvent):
        '''
            TODO:
                Need to move the Previous/Next game info in the data section. I think loading it in the data section
                and then taking that info here would make sense
        '''
        self.data = data
        self.data.cta_trains.get_trains()
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
            print("HERE:")
            print(self.data.cta_trains.traintracker_data)

            stations = {
                "Forest Park": "For. Park",
                "O'Hare": "O'Hare",
                "UIC Halsted": "UIC Hals.",
                "Rosemont": "Rosemont"
            }

            trains = []

            try:
                for train in self.data.cta_trains.traintracker_data['ctatt']['eta']:
                    dtarrival = datetime.datetime.strptime(train['arrT'], '%Y-%m-%dT%H:%M:%S')
                    minsuntil =  dtarrival - datetime.datetime.now()
                    dest = train['destNm']

                    try:
                        dest = stations[dest]
                    except:
                        dest = dest

                    trains.append({
                        "Dest": dest,
                        "Time": str(round(minsuntil.seconds/60)) + " min"
                    })
                print(trains)
            except:
                trains.append({
                    "Dest": "No",
                    "Time": "Data"
                })


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

            # experimenting/poking around the data variable
            print("Here comes the weather data print!")
            print(self.data.wx_current)

            i = 0

            if not self.sleepEvent.is_set():
                #Create images for the train scroller
                image_train_top_two = self.draw_train_times(
                    trains,
                    0,
                    2
                )

                # TO DO: What if there are less than 3 trains? Need a way to get the train data and fail gracefully if there are not a lot of trains there.

                image_train_bottom_rest = self.draw_train_times(
                    trains,
                    2,
                    len(trains)
                )


                #image SCROLLER!
                #in the future, this would be good to do programmatically (that is, use os to find the number of files in the folder, and then go from there.)
                png_number = random.randint(1,12)
                cta_logo_image = Image.open(get_file('assets/images/cta/cta-' + str(png_number) + '.png'))
                cta_img_width, cta_img_height = cta_logo_image.size
                cta_xpos = 0
                self.matrix.clear()
                self.matrix.draw_image((-cta_xpos, 0), cta_logo_image, "top-left")
                self.matrix.render()
                self.sleepEvent.wait(2)
                while cta_xpos < cta_img_width - 64:
                    cta_xpos += 1
                    self.matrix.clear()
                    self.matrix.draw_image((-cta_xpos, 0), cta_logo_image, "top-left")
                    self.matrix.render()
                    self.sleepEvent.wait(0.05)
                self.sleepEvent.wait(2)


                #load fancy bottom bar png
                image_bottom_bar = Image.open(get_file('assets/images/cta_bottom_bar.png'))

                #draw up the weather data
                image_weather = Image.new('RGB', (40, 10), color = (0, 120, 193))
                draw = ImageDraw.Draw(image_weather)
                weather_text_font = ImageFont.truetype('assets/fonts/BMmini.TTF', 8)
                weather_icons_font = ImageFont.truetype('assets/fonts/weathericons.ttf')
                if(len(self.data.wx_current) > 0):
                    draw.text((0, 1), self.data.wx_current[3], fill=(255, 255, 255), font=weather_text_font, align="right")
                    draw.text((25,-3), self.data.wx_current[1], fill=(255, 255, 255), font=weather_icons_font, align="right")
                print('\U0001f638')

                #here comes the main layout
                self.matrix.clear()

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_train_top_two,
                )

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_train_bottom_rest,
                    (0, 14)
                )

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_bottom_bar,
                    (0, 22)
                )

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_weather,
                    (24, 23)
                )

                self.matrix.render()

            self.matrix.render()

            self.sleepEvent.wait(9)

            # Move the image up until we hit the bottom.
            train_scroller_height = (len(trains) - 3) * 7
            i = 0
            while i > -(train_scroller_height):
                i -= 1

                self.matrix.clear()

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_train_bottom_rest,
                    (0, i + 14)
                )

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_train_top_two
                )

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_bottom_bar,
                    (0, 22)
                )

                self.matrix.draw_image_layout(
                    self.layout.info,
                    image_weather,
                    (24, 23)
                )

                self.matrix.render()
                if self.data.network_issues:
                    self.matrix.network_issue_indicator()
                if self.data.newUpdate and not self.data.config.clock_hide_indicators:
                    self.matrix.update_indicator()

                if i%7 == 0:
                    self.sleepEvent.wait(2)
                else:
                    self.sleepEvent.wait(0.3)

            # Show the bottom before we change to the next table.
            self.sleepEvent.wait(9)

    def draw_train_times(self, cta_data, train_start, train_max):
        image = Image.new('RGB', (64, train_max * 7))
        draw = ImageDraw.Draw(image)

        pos = 0
        loop_count = 0 + train_start
        while loop_count < train_max:
            if(len(cta_data) > 0):
                #index error here...please fix
                print(len(cta_data))
                draw.text((3, pos), "{}".format(cta_data[loop_count]['Dest']), fill=(255, 255, 255), font=self.font, align="right")
                draw.text((43,pos), "{}".format(cta_data[loop_count]['Time']), fill=(255, 255, 255), font=self.font, align="right")
                #if done for lines other than the blue line, then create a dictionary with all the line names and their corresponding rgb values, then use the cta data feed to populate it.
                draw.rectangle((0, pos + 1, 1, pos + 5), fill = (0, 157, 220))
            pos += 7
            loop_count += 1
        print(cta_data)

        return image
