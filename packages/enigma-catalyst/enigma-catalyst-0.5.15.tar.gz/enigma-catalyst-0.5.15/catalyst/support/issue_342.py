from datetime import datetime
import pytz

from catalyst.api import symbol, cancel_order, order
from catalyst.utils.run_algo import run_algorithm
from catalyst.exchange.utils.exchange_utils import get_exchange_symbols

EXCHANGE_NAME = 'poloniex'

def initialize(context):
    context.asset = symbol('etc_usdt')
    context.exchange_name = EXCHANGE_NAME
    context.i = 0

def handle_data(context, data):
    json_symbols = get_exchange_symbols(context.exchange_name)
    #symbol()

    orders = context.blotter.open_orders
    if context.i == 0:
        order(context.asset, 1000, limit_price=0.001)

    if context.i == 0:
        for ord in context.blotter.open_orders[context.asset]:
            cancel_order(ord.id)#, EXCHANGE_NAME)
            #context.exchanges[EXCHANGE_NAME].cancel_order(ord.id)

    context.i += 1
    print json_symbols
    #context.exchanges[EXCHANGE_NAME].cancel_order(5)


live = False

if live:
    run_algorithm(initialize=initialize,
                  handle_data=handle_data,
                  exchange_name=EXCHANGE_NAME,
                  quote_currency='usdt',
                  algo_namespace='issue-342--',
                  live=True,
                  data_frequency='daily',
                  capital_base=104,
                  simulate_orders=True,
                )
else:
    run_algorithm(initialize=initialize,
                  handle_data=handle_data,
                  exchange_name=EXCHANGE_NAME,
                  quote_currency='usdt',
                  algo_namespace='issue-337',
                  live=False,
                  #data_frequency='minute',
                  capital_base=3000,
                  start=datetime(2018, 3, 25, 0, 0, 0, 0, pytz.utc),
                  end=datetime(2018, 4, 3, 0, 0, 0, 0, pytz.utc))


