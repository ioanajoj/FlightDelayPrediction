import pandas as pd

#
# Get USA airports from GlobalAirportDatabase from
# http://www.partow.net/miscellaneous/airportdatabase/index.html
# and normalize their names
#
# in: GlobalAirportDatabase.csv
# ->  icao_code,iata_code,airport_name,city,country,lat_degree,lat_min,lat_sec,lat_dir,
# ->  long_degree,long_min,long_sec,long_dir,altitude,lat_dec,long_dec
# out: USA_airports.csv
# ->  iata_code,airport_name,city,lat_dec,long_dec
#


def change_names(name):
    return name.lower()\
        .replace(' rgnl', ' regional')\
        .replace(' mem', ' memorial')\
        .replace(' fld', ' field')\
        .replace(' muni', ' municipal')\
        .replace(' afb', ' air force base')\
        .replace(' arb', ' air reserve base')\
        .title()

if __name__ == '__main__':
    df = pd.read_csv('GlobalAirportDatabase.csv')
    df = df[df.country == 'USA']
    columns = ['iata_code', 'airport_name', 'city', 'lat_dec', 'long_dec']
    df = df[columns]
    df = df.dropna()
    df.airport_name = df.apply(lambda row: change_names(row['airport_name']), axis=1)

    output_file = 'USA_airports.csv'
    df.to_csv(output_file, index=False)
