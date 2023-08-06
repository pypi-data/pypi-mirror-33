# coding: utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from exchange.client import Client

client = Client(api_key='2749589/QCx9VCOSus3yCR',
                api_secret='uvJU29w1T0P+QZlfE0yY5IxlzaqKvsyqBxLLYT1DQOXMGqQv3TRPGmdRHiKBLzAy')


markets = client.get_markets()
print(markets)

# tickers = client.get_ticker(market='ETHCLP')
# print(tickers)

# books = client.get_book(market="ETHCLP", type='sell', page=1)
# print(books)

# trades = client.get_trades(market="ETHCLP")
# print(trades)

# active_orders = client.get_active_orders(market="ETHCLP")
# print(active_orders)

# executed_orders = client.get_executed_orders(market="ETHCLP")
# print(executed_orders)

# new_order = client.create_order(market="ETHCLP", amount=1, price=100000, type='buy')
# print(new_order)
#
# status_order = client.get_status_order(id='M315140')
# print(status_order)

# cancel_order = client.cancel_order(id='M307270')
# print(cancel_order)

# status_order2 = client.get_status_order(id='M307270')
# print(status_order2)

# balance = client.get_balance()
# print(balance)



