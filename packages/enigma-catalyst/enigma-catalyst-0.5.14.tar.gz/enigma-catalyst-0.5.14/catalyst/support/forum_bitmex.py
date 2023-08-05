from catalyst.api import order, record, symbol, order_target_percent
from catalyst.api import order, record, symbol
from catalyst.utils.run_algo import run_algorithm

def initialize(context):
    context.asset = symbol('btc_usd')
    context.i = 0
    #context.set_slippage(spread=0.01)

def handle_data(context, data):
    context.i += 1

    print("========")
    print(context.i)
    print("========")

    if context.i == 1:
        order(context.asset, 10)
        #order_target_percent(context.asset, 1)

    elif context.i == 2:
        order(context.asset, -10)
        #order_target_percent(context.asset, -1)

    record(data.current(context.asset, 'price'))



#LIVE
run_algorithm(
    initialize=initialize,
    exchange_name='bitmex', # also tried poloniex
    base_currency='usd',# or usdt
    capital_base=0,
    algo_namespace="bitmex",
    handle_data=handle_data,
    #start=pd.to_datetime('2017-1-1', utc=True),
    #end=pd.to_datetime('2018-4-8', utc=True), # False also
    live=True,
    simulate_orders=False) # False also
