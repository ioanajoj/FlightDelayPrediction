import re
import requests
from bs4 import BeautifulSoup
import json

#
# Retrieve from source_url all airports
# These are found as origin or destination airports in the flight data from BTS:
# https://www.bts.gov/browse-statistical-products-and-data/db20
#
# in: https://www.transtats.bts.gov/OT_Delay/NewAirportList.asp?xpage=OT_DelayCause1.asp&flag=undefined
# out: airports.json -> [ {"code":"", "name":"", "location":""}, ... ]
#

source_url = 'https://www.transtats.bts.gov/OT_Delay/NewAirportList.asp?xpage=OT_DelayCause1.asp&flag=undefined'
html_text = requests.get(source_url).text
soup = BeautifulSoup(html_text, 'html.parser')


class Airport:
    def __init__(self, code, name, location):
        self.code = code
        self.name = name
        self.location = location


if __name__ == '__main__':
    airports = []
    for link in soup.find_all('a'):
        call = link.get('href')
        args = re.findall(r"\'(.+?)\'", call)
        airport_code = args[0]
        airport_location, airport_name = args[1].split(':')
        airports.append(Airport(airport_code, airport_name, airport_location).__dict__)
        print(airport_code + ' - ' + airport_location + ' - ' + airport_name)

    output_structure = {'count': len(airports), 'airports': airports}
    with open('airports.json', 'w') as f:
        json.dump(output_structure, f)
