import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import os

#
# Download yearly weather data for stations matched with airports in airports_stations.csv file
#
# IN
# Weather data downloaded from:
#   https://www.ncei.noaa.gov/data/local-climatological-data/access/<year>/<station_file_name>.csv
# Station id is matched with file names in source_url by matching last 5 digits in file_names
#   with the station ids in airports_stations csv file
#
# OUT
# weather-data/ file for each station having name = id
#


source_url = 'https://www.ncei.noaa.gov/data/local-climatological-data/access/'
year = '2019'

def download_csv(id, filename, year):
    """
    weather_data_cleanup.ipynb code
    Saves a csv file with weather data for station with given id for
    :param id: 5 digit id
    :param filename: name of file from source_url
    :param year: int [1901, 2020]
    :return:
    """
    print(f'Converting {id}')
    df = pd.read_csv(source_url + str(year) + '/' + filename)
    # keep only relevant columns
    columns = ['STATION', 'DATE', 'REPORT_TYPE', 'HourlyDryBulbTemperature', 'HourlyPrecipitation',
               'HourlyStationPressure', 'HourlyVisibility', 'HourlyWindSpeed']
    df = df[columns]
    # keep only REPORT_TYPE FM-15 = METAR Aviation routine weather report => hourly report for whole month
    df = df[df.REPORT_TYPE == 'FM-15']
    df = df.drop(columns=['REPORT_TYPE'])
    def clean_up(df, column_name):
        if df[column_name].isnull().all:
            df[column_name].fillna(0)
        else:
            # some rows contain numeric values followed by letters, while some are null
            # convert everything to string => 54 = '54', '72s' = '72s', nan = 'nan'
            df[column_name] = df[column_name].astype(str)
            # Remove all letters => 54 = '54', '72s' = '72', nan = ''
            df[column_name] = df[column_name].replace('[A-Za-z]+','', regex=True)
            # Change '' back to valid nan: np.nan
            df[column_name] = df[column_name].str.replace('^$', lambda _: np.nan)
            # Replace * with np.nan
            df[column_name] = df[column_name].str.replace('\*', lambda _: np.nan)
            # Convert back to numeric all numeric values, nan remains none
            df[column_name] = pd.to_numeric(df[column_name])
            # Fill left nan with average values
            df[column_name] = (df[column_name].fillna(method='ffill') + df[column_name].fillna(method='bfill')) / 2
            # Fill boundary nan values
            df[column_name] = df[column_name].fillna(method='bfill')
            df[column_name] = df[column_name].fillna(method='ffill')
            # Convert new values
            df[column_name] = pd.to_numeric(df[column_name])
            df[column_name] = df[column_name].round(2)
        return df[column_name]
    df.HourlyDryBulbTemperature = clean_up(df, 'HourlyDryBulbTemperature')
    df.HourlyPrecipitation = clean_up(df, 'HourlyPrecipitation')
    df.HourlyStationPressure = clean_up(df, 'HourlyStationPressure')
    df.HourlyVisibility = clean_up(df, 'HourlyVisibility')
    df.HourlyWindSpeed = clean_up(df, 'HourlyWindSpeed')
    df.to_csv(os.path.join('', id + '.csv'), index=False)


def retrieve_files():
    html_text = requests.get(source_url + str(year)).text
    soup = BeautifulSoup(html_text, 'html.parser')
    file_names = dict()
    for link in soup.find_all('a'):
        call = link.get('href')
        if call[-4:] == '.csv':
            file_names[call[6:-4]] = call
    return file_names



if __name__ == '__main__':
    file = retrieve_files()
    df = pd.read_csv('airports_stations.csv')
    ids = np.unique(df[['station_id']]).tolist()

    for id in ids:
        if id[:4] == 'WBAN':
            short_id = id[5:]
            try:
                download_csv(short_id, file[short_id], year)
            except KeyError as ke:
                print(f'Exception occurred for {short_id}, data for this station is not available for the given year')
            except Exception as e:
                print(f'Exception occurred for {short_id} {e}')

