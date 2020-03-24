import requests

cdo_token = 'davQIOzciXPWdFXJzJLAZXGfCdyrOEiq'
header = {'token': cdo_token}

base_url = 'https://www.ncdc.noaa.gov/cdo-web/api/v2'
stations_endpoint = '/stations'

params = {'limit': 1000, 'datasetid': 'lcd',
          'startdate': '2019-12-01', 'enddate': '2019-12-31'}

# response = requests.get(base_url + stations_endpoint, params=params, headers=header)

response = requests.get(base_url + '/datasets', headers=header)
print('Status: ' + str(response.status_code))
print(response.text)