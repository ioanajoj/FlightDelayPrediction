import requests
import json

#
# Get all weather stations available at Climate Data Online Web Services
# found on the map within USA coordinates +/- Bermuda, Bahamas etc. having name ending in US
# having data available starting start_date
# Service Doc: https://www.ncdc.noaa.gov/cdo-web/webservices/v2#stations
#
# in: https://www.ncdc.noaa.gov/cdo-web/api/v2/stations
# out: stations.json ->
# [ {"elevation":0,
#    "mindate":"yyyy-mm-dd",
#    "maxdate":"yyyy-mm-dd",
#    "latitude":32.3667,
#    "name":"",
#    "datacoverage":[0-1),
#    "id":"",
#    "elevationUnit":"METERS",
#    "longitude":-64.6833
# }, ... ]
#


cdo_token = 'davQIOzciXPWdFXJzJLAZXGfCdyrOEiq'
header = {'token': cdo_token}

base_url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2'
stations_endpoint = '/stations'

# get number of stations available
start_date = '2019-12-01'
usa_extent = '25.6291,-124.81,48.332,-61.97'
response = requests.get(base_url + stations_endpoint, params={'startdate': start_date, 'extent': usa_extent}, headers=header)
station_count = response.json()['metadata']['resultset']['count']

# get stations
limit = 1000
offset = 0
no_requests = station_count // limit + 1
stations = []
for i in range(no_requests):
    params = {'offset': offset, 'limit': limit, 'startdate': start_date, 'extent': usa_extent}
    response = requests.get(base_url + stations_endpoint, params=params, headers=header)
    assert response.status_code == 200
    stations_subset = response.json()['results']
    for station in stations_subset:
        if station['name'][-3:] == ' US':
            stations.append(station)
    offset += limit

output_file = 'stations.json'
output_structure = {'count': len(stations), 'stations': stations}
with open(output_file, 'w') as f:
    json.dump(output_structure, f)

print('Saved ' + str(len(stations)) + ' stations to ' + output_file)
