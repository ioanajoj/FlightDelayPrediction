import pandas as pd
import geopy.distance
import os


#
# Match airports used in on-time flight data with weather stations
#
# Airports Source: https://ourairports.com/data/ +
#                  https://www.transtats.bts.gov/OT_Delay/NewAirportList.asp?xpage=OT_DelayCause1.asp&flag=undefined
# Weather Stations Source: https://www.ncdc.noaa.gov/cdo-web/webservices/v2#stations
#
# Out: CSV each row has an airport and its closest (most cases) WBAN weather station
# Columns: iata_code,airport_name,latitude,longitude,elevation_ft,city,station_id,station_name,mindate,maxdate
#

def get_closest_station(stations, lat, long, index):
    """
    Find the closest element in the stations df based on distance computed between two geographical coordinates
    :param stations: dataframe
    :param lat: float with 3 decimal points
    :param long: float with 3 decimal points
    :return: id,name,mindate,maxdate
    """
    df = pd.DataFrame(stations)
    df['distance'] = stations.apply(lambda row:
                                    geopy.distance.distance((lat, long), (row['latitude'], row['longitude'])).km,
                                    axis=1)
    df = df.sort_values(by=['distance'])
    df.distance = df.distance.round(3)
    for i in range(3):
        if 'WBAN' in df.iloc[i].id:
            return [df.iloc[i].id, df.iloc[i]['name'], df.iloc[i].mindate, df.iloc[i].maxdate, df.iloc[0].distance]
    else:
        print(f'WBAN not found {index} {lat} {long} {df.iloc[0].to_list()}')
        return [df.iloc[0].id, df.iloc[0]['name'], df.iloc[0].mindate, df.iloc[0].maxdate, df.iloc[0].distance]


airports_stations_columns = ['iata_code', 'airport_name', 'latitude', 'longitude', 'elevation_ft', 'city',
                             'station_id', 'station_name', 'mindate', 'maxdate', 'distance']
airports_stations_df = pd.DataFrame(columns=airports_stations_columns)
stations_path = os.path.join('weather', 'stations.csv')
# with open(stations_path, 'r') as stations_f:
#     json_stations_f = json.load(stations_f)
#     json_stations = json_stations_f['stations']
stations_df = pd.read_csv(stations_path)
airports_df = pd.read_csv('usa-airports.csv')
for index, row in airports_df.iterrows():
    if index % 50 == 0:
        print(index)
    closest_station = get_closest_station(stations_df, row.latitude_deg, row.longitude_deg, index)
    new_row = pd.DataFrame([row.to_list() + closest_station], columns=airports_stations_columns)
    airports_stations_df = airports_stations_df.append(new_row)

airports_stations_df.to_csv('airports_stations.csv', index=False)
