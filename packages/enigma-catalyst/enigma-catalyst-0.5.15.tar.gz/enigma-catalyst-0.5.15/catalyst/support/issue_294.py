from catalyst.api import order, record, symbol
from catalyst.utils.run_algo import run_algorithm
import pandas as pd

def initialize(context):
    pass




def handle_data(context, data):
    current_price = data.current(symbol('eth_usd'), fields=['price'])
    current_open = data.current(symbol('eth_usd'), fields=['open'])


    #prices = data.history(
    #    symbol('btc_eur'),
    #    fields=['price', 'open', 'high', 'low', 'close', 'volume'],
    #    bar_count=3,
    #    frequency="5T"
    #)

    #record(
    #    volume=current['volume'], prices = prices
    #)
    print ("CURRENT: %s %s %s" % (data.current_dt, current_price, current_open))


#LIVE
run_algorithm(
    initialize=initialize,
    exchange_name='bitfinex', # also tried poloniex
    quote_currency='usd',# or usdt
    capital_base=20000,
    algo_namespace="issue-230",
    data_frequency='minute',
    handle_data=handle_data,
    start=pd.to_datetime('2018-2-27', utc=True),
    end=pd.to_datetime('2018-3-1', utc=True)) # False also
    #live=True,
    #simulate_orders=True) # False also


