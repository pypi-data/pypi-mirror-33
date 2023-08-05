from catalyst.exchange.exchange_bundle import ExchangeBundle
import pandas as pd

exchange_name = "poloniex"

exchange_bundle = ExchangeBundle(exchange_name)

exchange_bundle.ingest(
    data_frequency="minute",
    include_symbols="btc_usdt",
    start=pd.Timestamp("01-01-2016"),
    end=pd.Timestamp("01-02-2017"),
)