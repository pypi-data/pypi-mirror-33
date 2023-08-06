from catalyst.api import symbol, order
from catalyst.utils.run_algo import run_algorithm

def initialize(context):
    context.asset = symbol('abt_btc')


def handle_data(context, data):
    history = data.history(context.asset, ['volume'],
                           bar_count=1,
                           frequency='5T')

    print('\nnow: %s\n%s' % (data.current_dt, history))
    if not hasattr(context, 'i'):
        context.i = 0
    context.i += 1
    if context.i == 1:
        order(context.asset, 1000)
    if context.i > 10:
        raise Exception('stop')


live = True
if live:
    run_algorithm(initialize=initialize,
                  handle_data=handle_data,
                  exchange_name='huobipro',
                  quote_currency='usdt',
                  algo_namespace='issue-324',
                  live=True,
                  data_frequency='daily',
                  capital_base=3000,
                )

