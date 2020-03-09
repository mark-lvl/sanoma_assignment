import datetime
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
        yield datetime.date(year, month, day)


def save_to_disk(input: pd.DataFrame, filename: str):
    output_path = Path(f"{OUTPUT_DIR}/{filename}/")
    log.info(f'Exporting data into {output_path}')
    try:
        input.to_csv(output_path, index=False)
    except Exception as ex:
        log.error(f'Faild on saving file in {output_path}, {ex}')


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


if __name__ == '__main__':
    log.info('Collecting the data started.')
    days_records = []
    for day_date in return_date_range(DATE_RANGE['year'], DATE_RANGE['month']):
        days_records.append(call_api(day_date))

    whole_month_records = pd.concat(days_records)
    save_to_disk(whole_month_records, OUTPUT_FILENAME)