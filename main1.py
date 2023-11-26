import aiohttp
import json
import argparse
from datetime import datetime, timedelta

async def fetch_currency_rates(days):
    # Створюємо порожній список для зберігання курсів валют
    rates = []

    # Встановлюємо асинхронний HTTP-клієнт
    async with aiohttp.ClientSession() as session:
        # Проходимось по кількості днів і отримуємо курси валют
        for i in range(days):
            # Визначаємо дату для запиту
            date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
            # Формуємо URL-адресу для запиту
            url = f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}'

            # Виконуємо асинхронний GET-запит
            async with session.get(url) as response:
                # Отримуємо текстовий вміст відповіді
                data = await response.text()
                # Додаємо результати у список курсів валют
                rates.append({date: parse_currency_data(data)})

    return rates

def parse_currency_data(data):
    # Розпаковуємо JSON-дані
    currency_data = json.loads(data)
    # Створюємо словники для євро та долара
    eur = {'EUR': {'sale': None, 'purchase': None}}
    usd = {'USD': {'sale': None, 'purchase': None}}

    # Проходимось по курсам валют
    for rate in currency_data['exchangeRate']:
        # Якщо це євро, записуємо курси євро
        if rate['currency'] == 'EUR':
            eur['EUR']['sale'] = rate['saleRateNB']
            eur['EUR']['purchase'] = rate['purchaseRateNB']
        # Якщо це долар, записуємо курси долара
        elif rate['currency'] == 'USD':
            usd['USD']['sale'] = rate['saleRateNB']
            usd['USD']['purchase'] = rate['purchaseRateNB']

    # Об'єднуємо словники для євро та долара та повертаємо результат
    return {**eur, **usd}

def print_currency_rates(rates):
    # Виводимо курси валют у зручному JSON-форматі
    print(json.dumps(rates, indent=2, ensure_ascii=False))

def exchange_command(days):
    # Отримуємо асинхронний цикл
    loop = asyncio.get_event_loop()
    # Викликаємо асинхронну функцію та отримуємо результати
    rates = loop.run_until_complete(fetch_currency_rates(days))
    # Виводимо результати на екран
    print_currency_rates(rates)

if __name__ == "__main__":
    # Створюємо парсер для аргументів командного рядка
    parser = argparse.ArgumentParser(description='Get currency rates from PrivatBank API.')
    # Визначаємо аргумент для кількості днів
    parser.add_argument('days', type=int, help='Number of days to fetch currency rates (up to 10 days)')
    # Парсимо аргументи командного рядка
    args = parser.parse_args()

    # Перевіряємо обмеження на кількість днів
    if args.days > 10:
        print("Error: You can fetch currency rates for up to 10 days only.")
    else:
        # Викликаємо функцію для отримання курсів валют
        exchange_command(args.days)
