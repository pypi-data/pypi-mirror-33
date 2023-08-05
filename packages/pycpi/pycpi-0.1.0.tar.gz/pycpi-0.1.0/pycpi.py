from datetime import datetime, timedelta
from decimal import Decimal
import json

import requests


def get_data(start_year=None, end_year=None):
    end_year = end_year or datetime.now().year
    start_year = start_year or (end_year - 9)
    if not start_year < end_year:
        raise ValueError('start_year must be before end_year')

    # The BLS API only supports fetching up to 10 years at a time.
    window_start = max(start_year, end_year - 9)
    window_end = end_year

    while window_end >= start_year:
        response = requests.post(
            'https://api.bls.gov/publicAPI/v1/timeseries/data/',
            json={
                'seriesid': ['CUUR0000SA0'],
                'startyear': window_start,
                'endyear': window_end
            })

        response.raise_for_status()
        response_data = json.loads(response.content)

        response_status = response_data.get('status', 'REQUEST_SUCCEEDED')
        if response_status != 'REQUEST_SUCCEEDED':
            error_message = response_data.get(
                'message', 'The BLS API responded with an error.')
            raise BLSAPIError(error_message)

        try:
            results = response_data['Results']['series'][0]['data']
        except TypeError:
            raise BLSAPIError('The BLS API returned results in an unexpected '
                              'format.')

        if len(results) == 0:
            return

        for result in results:
            yield (int(result['year']), result['periodName'],
                   Decimal(result['value']))

        window_start = max(start_year, window_start - 10)
        window_end = window_end - 10


class BLSAPIError(Exception):
    pass
