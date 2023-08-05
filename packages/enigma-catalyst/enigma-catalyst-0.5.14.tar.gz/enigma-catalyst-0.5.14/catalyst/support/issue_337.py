import pytz
from datetime import datetime, timedelta
from catalyst.api import symbol
from catalyst.utils.run_algo import run_algorithm

coin = 'btc'
base_currency = 'usd'
n_candles = 5


def initialize(context):
    context.symbol = symbol('%s_%s' % (coin, base_currency))


def handle_data(context, data):
    # all I do is print the current last 2 candles (5T)
    history = data.history(symbol('eth_usdt'), ['volume'],
                           bar_count=1,
                           frequency='5T')

    current = data.current(symbol('eth_usdt'), ['price'])

    #print('\nnow: %s\n%s' % (data.current_dt, history))

    print('%s %s' % (data.current_dt, current))


live = True
if live:
    run_algorithm(initialize=lambda ctx: True,
                  handle_data=handle_data,
                  exchange_name='poloniex',
                  quote_currency='usd',
                  algo_namespace='issue-337',
                  live=True,
                  # data_frequency='minute',
                  capital_base=3000,

                  #start=datetime(2018, 3, 25, 0, 0, 0, 0, pytz.utc),
                  #end=datetime(2018, 4, 3, 0, 0, 0, 0, pytz.utc)
     )
else:
    run_algorithm(initialize=lambda ctx: True,
                  handle_data=handle_data,
                  exchange_name='bitfinex',
                  quote_currency='usd',
                  algo_namespace='issue-337',
                  live=False,
                  #data_frequency='minute',
                  capital_base=3000,
                  start=datetime(2018, 3, 25, 0, 0, 0, 0, pytz.utc),
                  end=datetime(2018, 4, 3, 0, 0, 0, 0, pytz.utc))