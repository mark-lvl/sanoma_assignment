from datetime import (
    datetime, date, timedelta)
import calendar
import requests
from pathlib import Path
import pandas as pd
from utils.logger import log

# DEBUG
pd.set_option('display.expand_frame_repr', False)

#########
# SETTING
#########
API_URI = 'https://rata.digitraffic.fi/api/v1/trains/{DATE}/{TRAIN_NUMBER}'
DATE_RANGE = {
    'year': 2020,
    'month': 1
}
OUTPUT_FILENAME = 'jan_2020_train_5.csv'
OUTPUT_DIR = 'data'


def return_date_range(year: int, month: int) -> datetime:
    """Return all days date within the given month"""
    num_days = calendar.monthrange(year, month)[1]
    for day in range(1, num_days+1):
        yield date(year, month, day)


def _file_path_generator(filename: str) -> str:
    """Construct file path in disk"""
    return Path(f"{OUTPUT_DIR}/{filename}/")


def save_to_disk(input: pd.DataFrame, filename: str):
    """Export dataframe to disk"""
    output_path = _file_path_generator(filename)
    log.info(f'Exporting data into {output_path}')
    try:
        input.to_csv(output_path, index=False)
    except Exception as ex:
        log.error(f'Faild on saving file in {output_path}, {ex}')


def read_from_disk(filename: str) -> pd.DataFrame:
    """Read csv file from disk"""
    input_path = _file_path_generator(filename)
    try:
        return pd.read_csv(input_path)
    except Exception as ex:
        log.error(f'Faild on reading file in {input_path}, {ex}')
        exit()


def call_api(date: datetime, train_number: int = 5) -> pd.DataFrame:
    """Calling API to get a specific train data"""
    try:
        uri = API_URI.format(DATE=date, TRAIN_NUMBER=train_number)
        log.info(f'Calling api: {uri}')
        response = requests.get(uri)
        if response:
            response = response.json()[0]
            # normalising json to flat columns and clean data for csv
            root_df = pd.json_normalize(
                response).drop(['timeTableRows'], axis=1)
            timetable_df = pd.json_normalize(response['timeTableRows'])
            full_day = pd.merge(root_df, timetable_df)
            full_day.fillna('NA', inplace=True)
            return full_day
    except Exception as ex:
        log.error(f'Faild on calling api on {date}, {ex}')


def calc_avg_arrival_time(input_filename: str) -> str:
    """
    Read collected data from disk and return and calculate the average
    actual arrival time at the final destination of the train during the
    month January 2020.
    """
    df = read_from_disk(input_filename)
    last_stops = df.groupby('departureDate')['scheduledTime'].max()
    actualtimes = []
    # extract arrival timess on final destinations
    for index, value in last_stops.items():
        actualtime = df[
            (df['departureDate'] == index) &
            (df['scheduledTime'] == value)]['actualTime'].values[0]
        actualtimes.append((actualtime.split('T')[1]).split('.')[0])
    # calculate the avg arrival time
    avg = str(timedelta(
        seconds=sum(
            map(lambda f: int(f[0])*3600 + int(f[1])*60 + int(f[2]),
                map(lambda f: f.split(':'), actualtimes))) / len(actualtimes)))
    return avg.split('.')[0]


if __name__ == '__main__':
    log.info('Collecting the data started.')
    days_records = []
    for day_date in return_date_range(DATE_RANGE['year'], DATE_RANGE['month']):
        days_records.append(call_api(day_date))

    whole_month_records = pd.concat(days_records)
    save_to_disk(whole_month_records, OUTPUT_FILENAME)
