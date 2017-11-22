#!/usr/bin/env python3.6

SCRAPE_URL = 'https://www.wunderground.com/health/{locality}?cm_ven=localwx_modpollen'
DEFAULT_LOCALITY = 'us/az/phoenix/85001'

from bs4 import BeautifulSoup
import os
import requests
import sendgrid
from sendgrid.helpers.mail import Email, Mail, Content

def scrape(locality=DEFAULT_LOCALITY):
    url = SCRAPE_URL.format(locality=locality)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    parsedValues = {}
    airQualityDiv = soup.find(name='div', class_='content aqi')

    airQualityIndexDiv = airQualityDiv.find(name='div', string='AQI:').parent
    parsedValues['aqiIndex'] = int(airQualityIndexDiv.find(name='div', class_='aqi-value').string)

    pollutantDiv = airQualityDiv.find(name='div', string='Dominant Pollutant:').parent
    parsedValues['dominantPollution'] = pollutantDiv.find(name='div', class_='aqi-value').string
    
    # pollenDiv = soup.find(name='div', class_='region-pollen')

    textSummary = '''AQI: {aqiIndex}
    Dominant air pollution class: {dominantPollution}

    Brought to you by 
    {url}
    and
    https://github.com/mattbornski/airqualityexpress
    '''.format(url=url, **parsedValues)

    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('MAIL_FROM_ADDRESS'))
    to_email = Email(os.environ.get('MAIL_TO_ADDRESS'))
    subject = "Air quality metrics for " + locality
    content = Content("text/plain", textSummary)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)


if __name__ == '__main__':
    scrape()