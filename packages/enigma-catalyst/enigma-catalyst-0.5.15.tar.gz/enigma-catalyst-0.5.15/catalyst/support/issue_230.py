from catalyst.api import order, record, symbol
from catalyst.utils.run_algo import run_algorithm
import pandas as pd

def initialize(context):
    pass




def handle_data(context, data):
    current = data.current(symbol('btc_eur'), fields=['volume'])


    prices = data.history(
        symbol('eth_usdt'),
        fields=['price', 'open', 'high', 'low', 'close', 'volume'],
        bar_count=3,
        frequency="5T"
    )

    #record(
    #    volume=current['volume'], prices = prices
    #)
    print ("CURRENT VOLUME: %s" % prices)


#LIVE
run_algorithm(
    initialize=initialize,
    exchange_name='bitfinex', # also tried poloniex
    base_currency='eur',# or usdt
    capital_base=20000,
    algo_namespace="issue-230",
    handle_data=handle_data,
    start=pd.to_datetime('2018-2-11', utc=True),
    end=pd.to_datetime('2018-2-12', utc=True)) # False also
    #live=True,
    #simulate_orders=True) # False also


"""

#BACK-TEST
run_algorithm(
    initialize=initialize,
    exchange_name='poloniex', # also tried poloniex
    base_currency='usdt',# or usdt
    capital_base=20000,
    data_frequency='minute',
    algo_namespace="issue-230",
    handle_data=handle_data,
    start=pd.to_datetime('2018-2-11', utc=True),
    end=pd.to_datetime('2018-2-12', utc=True)) # False also



run_algorithm(
                capital_base=100,
                data_frequency='minute',
                initialize=initialize,
                handle_data=handle_data,
                analyze=analyze,
                exchange_name='poloniex',
                algo_namespace=NAMESPACE,
                base_currency='usdt',
                start=pd.to_datetime('2018-2-12', utc=True),
                end=pd.to_datetime('2018-2-12', utc=True),
                output=out
            )

And I am using this configuration to run live against Poloniex:

        if live:
            run_algorithm(
                capital_base=100,
                initialize=initialize,
                handle_data=handle_data,
                analyze=analyze,
                exchange_name='poloniex',
                live=True,
                algo_namespace=NAMESPACE,
                base_currency='usdt',
                live_graph=False,
                simulate_orders=False,
                stats_output=None,
            )

The only thing I change to backtest is using this configuration:

run_algorithm(
                capital_base=100,
                data_frequency='minute',
                initialize=initialize,
                handle_data=handle_data,
                analyze=analyze,
                exchange_name='poloniex',
                algo_namespace=NAMESPACE,
                base_currency='usdt',
                start=pd.to_datetime('2018-2-12', utc=True),
                end=pd.to_datetime('2018-2-12', utc=True),
                output=out
            )
"""