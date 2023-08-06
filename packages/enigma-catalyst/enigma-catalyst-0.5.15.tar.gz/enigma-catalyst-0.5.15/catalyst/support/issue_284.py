import pandas as pd
from catalyst.utils.run_algo import run_algorithm
from catalyst.api import symbol
from datetime import datetime
import pytz

def initialize(context):
    context.i = 0

def handle_data(context, data):
    prices = data.history(symbol('btc_usdt'), fields=['close'],bar_count=1,frequency='1T')
    context.i = context.i + 1
    #if context.i == 3: context.interrupt_algorithm()
    print prices

start_end = datetime(2018, 1, 1, 0, 0, 0, 0, pytz.utc)
run_algorithm(
    capital_base=3000,
    initialize=initialize,
    handle_data=handle_data,
    exchange_name='binance',
    algo_namespace='Test candles',
    quote_currency='usdt',
    data_frequency='minute',
    live=True,
    #start=start_end,
    #end=start_end
    )
