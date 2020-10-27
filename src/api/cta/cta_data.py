import requests
import json
import datetime
import math

import .cta_config


MAIN_URL = 'http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx'

class TrainTracker:
    def __init__(self):
        pass

    def get_trains(self):
        print("Train tracker initiated.")
        payload = {'key': cta_config.api_key, 'mapid': cta_config.mapid, 'max': 6, 'outputType': 'JSON'}
        try:
            response = requests.get(MAIN_URL, params=payload)
            self.traintracker_data = json.loads(response.text)
        #    numtrains = len(self.traintracker_data['ctatt']['eta'])
            print(type(self.traintracker_data))
        except requests.exceptions.RequestException as e:
            #raise ValueError(e)
            print(e)

        # for train in traintracker_data['ctatt']['eta']:
        #     dtarrival = datetime.datetime.strptime(train['arrT'], '%Y-%m-%dT%H:%M:%S')
        #     minsuntil =  dtarrival - datetime.datetime.now()
        #     print(train['rt'] + ' ' + train['destNm'] + ' ' + str(round(minsuntil.seconds/60)) + " mins")
# Need to round up on the mins until.
# Why isn't the UIC Halstead trains showing up?
#    print(math.ciel(minsuntil.seconds/60))
if __name__ == "__main__":
    try:
        go = TrainTracker()
        go.get_trains()
    except KeyboardInterrupt:
        print("Exiting CTA-SCOREBOARD. Doors closing.\n")
        sys.exit(0)
