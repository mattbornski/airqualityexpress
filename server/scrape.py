#!/usr/bin/env python3.6

SCRAPE_URL = 'https://www.wunderground.com/health/{country_code}/{state_code}/{city}/{postcode}?cm_ven=localwx_modpollen'
DEFAULT_LOCALITY = {
    'country_code': 'us',
    'state': 'Arizona',
    'city': 'Phoenix',
    'postcode': '85001',
}

from bs4 import BeautifulSoup
import os
import requests
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content
import us

def urlFromLocality(locality):
    print(locality)
    if not 'state_code' in locality:
        print(us.states.lookup(locality['state']))
        locality['state_code'] = us.states.lookup(locality['state']).abbr
    print(locality)
    return SCRAPE_URL.format(**locality)

def scrape(locality=DEFAULT_LOCALITY):
    url = urlFromLocality(locality)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    parsedValues = {
        'url': url,
        'city': locality['city'],
    }
    airQualityDiv = soup.find(name='div', class_='content aqi')
    print(airQualityDiv.prettify())

    airQualityIndexDiv = airQualityDiv.find(name='div', string='AQI:').parent
    parsedValues['aqiIndex'] = int(airQualityIndexDiv.find(name='div', class_='aqi-value').string)

    airQualityClassificationDiv = airQualityDiv.find(name='div', class_='aqi-type')
    parsedValues['aqiClassification'] = airQualityClassificationDiv.string

    airQualityIconImg = airQualityDiv.find(name='img')
    parsedValues['aqiIconSrc'] = airQualityIconImg.src

    airQualityDescDiv = airQualityDiv.find(name='div', class_='aqi-callout')
    # print(airQualityDescDiv.prettify())
    parsedValues['aqiDesc'] = airQualityDescDiv.string

    pollutantDiv = airQualityDiv.find(name='div', string='Dominant Pollutant:').parent
    parsedValues['dominantPollution'] = pollutantDiv.find(name='div', class_='aqi-value').string

    pollutantDescDiv = airQualityDiv.find(name='p', class_='pollutant-desc')
    parsedValues['dominantPollutionDesc'] = pollutantDescDiv.string
    
    # pollenDiv = soup.find(name='div', class_='region-pollen')
    # print(pollenDiv.prettify())

    print(parsedValues)

    return parsedValues



def email(parsedValues):
    textSummary = '''AQI: {aqiIndex}
    Dominant air pollution class: {dominantPollution}

    Brought to you by 
    {url}
    and
    https://github.com/mattbornski/airqualityexpress
    '''.format(**parsedValues)

    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('MAIL_FROM_ADDRESS'))
    to_email = Email(os.environ.get('MAIL_TO_ADDRESS'))
    subject = "Air quality metrics for " + parsedValues['locality']
    content = Content("text/plain", textSummary)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    # print(response.status_code)
    # print(response.body)
    # print(response.headers)



if __name__ == '__main__':
    data = scrape()
    email(data)