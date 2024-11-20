
import argparse
import json
from typing import List, Tuple
from matplotlib.lines import Line2D
import requests
import os

hostname = os.getenv( "PROMETHEUS_HOST" )
if hostname == "": 
    print("No hostname provided")
    exit(1)
global_url = f"http://{hostname}/api/v1/query_range"

def process (data):
    assert data["metric"]["__name__"] == "finance_crypto_data"

    target: str = data["metric"]["target"]
    values: List[List[float, str]] = data["values"]
    values.insert(0, [0, ""])
    
    values_with_self = zip(values, values[1:])
    values_filtered  = filter( lambda x: x[0][1] != x[1][1], values_with_self )
    final_values = list(map( lambda x: (x[1][0], float(x[1][1])), values_filtered ))
    return (target, final_values)

def query (start: float, end: float, resolution: int):
    url = global_url + f"?query=finance_crypto_data&start={start}&end={end}&step={resolution}"

    parsed = requests.get(url)
    assert parsed.status_code == 200

    payload = json.loads(parsed.content)
    assert payload["status"] == "success"
    payload = payload["data"]
    assert payload["resultType"] == "matrix"
    payload = payload["result"]
    
    return list(map(process, payload))

if __name__ == "__main__":
    # example on how to use the data
    import matplotlib.pyplot as plt

    values = query(1732100792.648, 1732102592.648, 7)

    amount = int(input("How many values do you want to plot ? "))

    legends = []
    cmap = plt.cm.coolwarm
    for index, (name, array) in enumerate(values[:amount]):
        if len(array) <= 20:
            print(f"Not enough data to process on 30 minutes on metric {name}")
            continue
        time   = list(map(lambda x: x[0], array))
        values = list(map(lambda x: x[1] / array[0][1], array)) # normalize values to show all of them
        
        color = cmap(index / max(1, amount - 1))
        legends.append( Line2D( time, values, label=name, color=color ) )
        plt.plot(time, values, color=color)
    plt.legend(handles=legends)
    plt.show()
