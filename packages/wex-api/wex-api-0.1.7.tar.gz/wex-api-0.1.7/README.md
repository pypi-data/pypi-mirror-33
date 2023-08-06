## wex.nz API client
A python client for [wex.nz](https://wex.nz) cryptocurrency exchange API.  
[Public API docs](https://wex.nz/api/3/docs)  
[Trade API docs](https://wex.nz/tapi/docs)  
Tested with python 2.7.13 and 3.6
##### Installation
```
$ pip install wex-api
```
##### Usage example
```python
from wex import Client
client = Client('your-API-key', 'your-API-secret')
# if key and secret not provided, only public API methods are available
market_info = client.info()
my_orders = client.active_orders('btc_usd')
```
