#!/usr/bin/env python3.6

from geopy.geocoders import Nominatim
import re
import scrape
from slackbot.bot import Bot, default_reply, respond_to

def slackify(parsedValues):
    textSummary = '''{aqiClassification} air quality in {city}
AQI: {aqiIndex}
Dominant air pollution class: {dominantPollution}
{dominantPollutionDesc}'''.format(**parsedValues)

    return textSummary

@default_reply
def quality(message):
    message.reply(slackify(scrape.scrape()))

@respond_to('(at|in) (.*)', re.IGNORECASE)
def qualityAt(message, preposition, location):
    geoResolver = Nominatim()
    resolvedLocation = geoResolver.geocode(location)
    # print(resolvedLocation)
    resolvedAddress = geoResolver.reverse("{lat}, {lon}".format(**resolvedLocation.raw))
    # print(resolvedAddress.raw)

    message.reply(slackify(scrape.scrape(resolvedAddress.raw['address'])))

def serve():
    bot = Bot()
    bot.run()

if __name__ == '__main__':
    serve()