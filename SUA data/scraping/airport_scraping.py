import re
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

#
# Retrieve from source_url all airports
# These are found as origin or destination airports in the flight data from BTS:
# https://www.bts.gov/browse-statistical-products-and-data/db20
#
# Fill missing data from this source with geographical coordinates from open database https://ourairports.com/data/
#
# in: https://www.transtats.bts.gov/OT_Delay/NewAirportList.asp?xpage=OT_DelayCause1.asp&flag=undefined
#
# JSON out: usa-airports.json ->
# { "count": ?, "airports": [
# "iata_code": "OCA",
# "airport_name": "Ocean Reef Club Airport",
# "latitude_deg": 25.325399398804002,
# "longitude_deg": -80.274803161621,
# "elevation_ft": 8.0,
# "municipality": "Key Largo",
# "code": null,
# "name": null,
# "location": null} ]
# }
# • code, name and location are retrieved from BTS website
#
# CSV out:
#   -> head: iata_code,airport_name,latitude_deg,longitude_deg,elevation_ft,city
#   -> sorted by iata_code
#

source_url = 'https://www.transtats.bts.gov/OT_Delay/NewAirportList.asp?xpage=OT_DelayCause1.asp&flag=undefined'
html_text = requests.get(source_url).text
soup = BeautifulSoup(html_text, 'html.parser')


class Airport:
    def __init__(self, iata_code, airport_name, latitude_deg, longitude_deg, elevation_ft, municipality):
        self.iata_code = iata_code
        self.airport_name = airport_name
        self.latitude_deg = latitude_deg
        self.longitude_deg = longitude_deg
        self.elevation_ft = elevation_ft
        self.municipality = municipality

    def __hash__(self):
        return hash(self.iata_code)


if __name__ == '__main__':
    open_airports_path = os.path.join('ourairports', 'ourairports.csv')
    df = pd.read_csv(open_airports_path)
    usa_airports = {kwargs['iata_code']: Airport(**kwargs) for kwargs in df.to_dict(orient='records')}

    column_names = ['iata_code', 'airport_name', 'latitude_deg',
                    'longitude_deg', 'elevation_ft', 'city']
    airports_data_frame = pd.DataFrame(columns=column_names)
    for link in soup.find_all('a'):
        call = link.get('href')
        args = re.findall(r"\'(.+?)\'", call)
        airport_code = args[0]
        airport_location, airport_name = args[1].split(':')

        try:
            matched_airport = usa_airports[airport_code]
            new_row = pd.DataFrame([list(matched_airport.__dict__.values())], columns=column_names)
            airports_data_frame = airports_data_frame.append(new_row)
        except KeyError:
            print('Airport with code ' + str(airport_code) + ' not found in usa airports database')

    airports_data_frame = airports_data_frame.sort_values(by=['iata_code'])
    airports_data_frame.latitude_deg = airports_data_frame.latitude_deg.round(3)
    airports_data_frame.longitude_deg = airports_data_frame.longitude_deg.round(3)
    airports_data_frame.to_csv('usa-airports.csv', index=False)
