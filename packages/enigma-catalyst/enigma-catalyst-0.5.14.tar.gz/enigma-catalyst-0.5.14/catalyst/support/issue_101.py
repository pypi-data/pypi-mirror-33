import os
import csv
import pytz
from datetime import datetime

from catalyst.api import record, symbol, symbols
from catalyst.utils.run_algo import run_algorithm


def initialize(context):
    # Portfolio assets list
    context.asset = symbol('btc_usdt') # Bitcoin on Poloniex

    # Creates a .CSV file with the same name as this script to store results
    context.csvfile = open(os.path.splitext(os.path.basename('btc_usdt_error'))[0]+'.csv', 'w+')
    context.csvwriter = csv.writer(context.csvfile)
    context.csvwriter.writerow(['date', 'open', 'close', 'high', 'low', 'volume'])

def handle_data(context, data):
    # Variables to record for a given asset: price and volume
    # Other options include 'open', 'high', 'open', 'close'
    # Please note that 'price' equals 'close'
    date   = context.blotter.current_dt     # current time in each iteration
    opened = data.current(context.asset, 'open')
    close = data.current(context.asset, 'close')
    high = data.current(context.asset, 'high')
    low = data.current(context.asset, 'low')
    volume = data.current(context.asset, 'volume')

    # Writes one line to CSV on each iteration with the chosen variables
    context.csvwriter.writerow([date, opened, close, high, low, volume])

def analyze(context=None, results=None):
    # Close open file properly at the end
    context.csvfile.close()


# Bitcoin data is available from 2015-3-2. Dates vary for other tokens.
start = datetime(2017, 12, 6, 0, 0, 0, 0, pytz.utc)
end = datetime(2017, 12, 8, 0, 0, 0, 0, pytz.utc)
results = run_algorithm(
    initialize=initialize,
    handle_data=handle_data,
    analyze=analyze,
    start=start,
    end=end,
    exchange_name='poloniex',
    data_frequency='minute',
    base_currency ='usdt',
    capital_base=10000)