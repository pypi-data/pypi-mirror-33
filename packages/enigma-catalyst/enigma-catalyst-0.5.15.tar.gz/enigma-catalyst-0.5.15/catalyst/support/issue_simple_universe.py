from catalyst.api import symbol
from catalyst.utils.run_algo import run_algorithm

import pandas as pd
import numpy as np

#coins = ['btc', 'dash', 'etc', 'eth', 'ltc', 'nxt', 'rep', 'str', 'xmr', 'xrp', 'zec']
symbols = None
from catalyst.exchange.utils.factory import get_exchange

def initialize(context):
    pass


def _handle_data(context, data):
    global symbols
    #if symbols is None: symbols = [symbol(c + '_usd') for c in coins]

    lookback = 10

    exchange = get_exchange('bitfinex', skip_init=True)
    exchange.init()
    exchange_coins = []
    for asset in exchange.assets:
        print asset.asset_name
        #sim =  symbol(exchange.get_symbol(asset))

        #print sim
        exchange_coins.append(symbol(asset.asset_name))

    for coin in exchange_coins:
        print coin
        opened = fill(data.history(coin,
                                   'open',
                                   bar_count=lookback,
                                   frequency='1H')).values
        high = fill(data.history(coin,
                                 'high',
                                 bar_count=lookback,
                                 frequency='1H')).values
        low = fill(data.history(coin,
                                'low',
                                bar_count=lookback,
                                frequency='1H')).values
        close = fill(data.history(coin,
                                  'price',
                                  bar_count=lookback,
                                  frequency='1H')).values
        volume = fill(data.history(coin,
                                   'volume',
                                   bar_count=lookback,
                                   frequency='1H')).values

        # close[-1] is the last value in the set, which is the equivalent
        # to current price (as in the most recent value)
        # displays the minute price for each pair every 30 minutes
        print('{now}: {pair} -\tO:{o},\tH:{h},\tL:{c},\tC{c},'
              '\tV:{v}'.format(
            now=now,
            pair=pair,
            o=opened[-1],
            h=high[-1],
            l=low[-1],
            c=close[-1],
            v=volume[-1],
        ))

# Replace all NA, NAN or infinite values with its nearest value
def fill(series):
    if isinstance(series, pd.Series):
        return series.replace([np.inf, -np.inf], np.nan).ffill().bfill()
    elif isinstance(series, np.ndarray):
        return pd.Series(series).replace(
                     [np.inf, -np.inf], np.nan
                    ).ffill().bfill().values
    else:
        return series


run_algorithm(initialize=initialize,
              handle_data=_handle_data,
            analyze=lambda _, results: True,
            exchange_name='bitfinex',
            base_currency='usdt',
            algo_namespace='issue-simple-universe',
            live=True,
            data_frequency='minute',
            capital_base=3000,
            simulate_orders=True)