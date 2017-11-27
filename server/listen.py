#!/usr/bin/env python3.6

import geopy
from geopy.geocoders import Nominatim
import re
import scrape
from slackbot.bot import Bot, default_reply, respond_to
import time

def slackify(parsedValues):
    textSummary = '''{aqiClassification} air quality in {city}, {state_code}
AQI: {aqiIndex}
Dominant air pollution class: {dominantPollution}
{dominantPollutionDesc}'''.format(**parsedValues)

    return textSummary

@default_reply
def quality(message):
    print('')
    print('')
    print('New request for quality at default location')
    message.reply(slackify(scrape.scrape()))

@respond_to('(at|in) (.*)', re.IGNORECASE)
def qualityAt(message, preposition, location, isRetry = False):
    print('')
    print('')
    print('New request for quality at ' + location)
    geoResolver = Nominatim()
    try:
        resolvedLocation = geoResolver.geocode(location + ', United States of America')
        print(resolvedLocation)
        resolvedAddress = geoResolver.reverse("{lat}, {lon}".format(**resolvedLocation.raw))
        print(resolvedAddress.raw)

        message.reply(slackify(scrape.scrape(resolvedAddress.raw['address'])))
    except geopy.exc.GeocoderTimedOut as e:
        if isRetry:
            raise e
        else:
            time.sleep(3)
            return qualityAt(message, preposition, location, True)

def serve():
    bot = Bot()
    bot.run()

if __name__ == '__main__':
    serve()