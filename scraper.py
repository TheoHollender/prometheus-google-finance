import time
from prometheus_client import Gauge, start_http_server

from finance import generate_finance_data

metric = Gauge( "finance_crypto_data", "Crypto Finance Data", [ "target" ] )

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    # Generate some requests.
    while True:
        data = generate_finance_data()

        for target, value in data:
            metric.labels( target ).set( value )
        
        time.sleep(60)