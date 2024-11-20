
from typing import List, Tuple
from bs4 import BeautifulSoup

import requests

URL = "https://www.google.com/finance/markets/cryptocurrencies"

def filter_with_text (soup: BeautifulSoup, text: str) -> "BeautifulSoup | None":
    divs = soup.find_all("div")
    for _div in divs:
        if _div.get_text().strip() == text:
            return _div
    return None

def li_to_finance_data (data) -> Tuple[str, float]:
    try:
        text : str = data.get_text( "|" )
        words = text.split("|")

        target = words[0]
        value  = words[2].replace(",", "")
        return (target, float(value))
    except Exception:
        return None
def generate_finance_data () -> List[Tuple[str, float]]:
    response = requests.get(URL)
    if response.status_code != 200:
        print("No response from google finance data")
        return []

    soup = BeautifulSoup(response.content)
    BTC  = filter_with_text(soup, "Bitcoin (BTC / USD)").find_parent("li")
    if BTC is None:
        print("Missing bitcoin holder, aborting")
        return []
    container = BTC.parent
    markets   = list( container.find_all("li") )

    results = []
    some_fails = False
    for market in markets:
        result = li_to_finance_data(market)
        if result is None:
            some_fails = True
            continue
        results.append(result)
    if some_fails:
        print("Some crypto data had strange behaviour, could recover", len(results), "out of", len(markets), "targets")

    return list(map(li_to_finance_data, markets))
