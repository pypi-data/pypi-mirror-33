from datetime import timedelta

import pandas as pd

from catalyst import run_algorithm
from catalyst.api import (symbols, )
from catalyst.exchange.utils.exchange_utils import get_exchange_symbols


def initialize(context):
    context.exchange = 'poloniex'
    context.base_currency = 'btc'

def handle_data(context, data):
    # run the following every so often in live mode to get the universe of active coins
    # in the given exchange quoted in base_currency
    context.coins = context.exchanges[context.exchange].assets
    context.coins = [c for c in context.coins
                             if c.quote_currency == context.base_currency]

#LIVE
run_algorithm(capital_base=0.07211586,  # amount of base_currency
            initialize=initialize,
            handle_data=handle_data,
            output='out_big_v2_live.pickle',
            exchange_name='poloniex',
            data_frequency='minute',
            base_currency='btc',
            live=True,
            simulate_orders=True,
            live_graph=False,
            algo_namespace='big_v2_live')
