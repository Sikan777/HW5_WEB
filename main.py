import asyncio
import json
import argparse
import httpx
from datetime import datetime, timedelta

async def fetch_currency_rates(days):
    async with httpx.AsyncClient() as client:
        rates = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
            url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'

            response = await client.get(url)
            data = response.text
            rates.append({date: parse_currency_data(data)})

        return rates

def parse_currency_data(data):
    currency_data = json.loads(data)
    eur = {'EUR': {'sale': None, 'purchase': None}}
    usd = {'USD': {'sale': None, 'purchase': None}}

    for rate in currency_data['exchangeRate']:
        if rate['currency'] == 'EUR':
            eur['EUR']['sale'] = rate['saleRateNB']
            eur['EUR']['purchase'] = rate['purchaseRateNB']
        elif rate['currency'] == 'USD':
            usd['USD']['sale'] = rate['saleRateNB']
            usd['USD']['purchase'] = rate['purchaseRateNB']

    return {**eur, **usd}

def print_currency_rates(rates):
    print(json.dumps(rates, indent=2, ensure_ascii=False))

def exchange_command(days):
    loop = asyncio.get_event_loop()
    rates = loop.run_until_complete(fetch_currency_rates(days))
    print_currency_rates(rates)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get currency rates from PrivatBank API.')
    parser.add_argument('days', type=int, help='Number of days to fetch currency rates (up to 10 days)')

    args = parser.parse_args()

    if args.days > 10:
        print("Error: You can fetch currency rates for up to 10 days only.")
    else:
        exchange_command(args.days)
