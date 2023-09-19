import sys
import platform
from datetime import datetime, timedelta
import logging

import aiohttp
import asyncio

BANK_LINK = 'https://api.privatbank.ua/p24api/exchange_rates?date='
# date_currency = '18.09.2023'
USD = "USD"
EUR = "EUR"
date_now = datetime.now()



def get_list_date(day):
    list_date = []

    for i in range(day):
        delta_day = timedelta(days=i)
        new_date = date_now - delta_day
        day = str(new_date.day) if new_date.day > 9 else '0' + str(new_date.day)
        month = str(new_date.month) if new_date.month > 9 else '0' + str(new_date.month)
        date_of_change = day + '.' + month + '.' + str(new_date.year)
        list_date.append(date_of_change)

    return list_date



async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    r = await resp.json()
                    return r
                logging.error(f"Error status: {resp.status} for {url}")
                return None
        except aiohttp.ClientConnectorError as err:
            logging.error(f"Connection error: {str(err)}")
            return None


async def get_exchange(date, currency):
    # result = await request('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
    result = await request(BANK_LINK + date)
    if result:
        temp_info = result['exchangeRate']
        exc, = list(filter(lambda el: el["currency"] == currency, temp_info))
        return f'{currency}: buy: {exc["purchaseRate"]}, sale: {exc["saleRate"]}. Date: {date}'
    return "Failed to retrieve data"



def main():
    try:
        day = sys.argv[1]
    except IndexError:
        return "No argument"

    try:
        d = int(day)
    except ValueError:
        return "No numerical value"
    
    if d <= 10:
        list_date = get_list_date(d) 
    else:
        return "list period more 10 day"

    curr_USD = ''
    curr_EUR = ''
    result = ''

    for item in list_date:
        if platform.system() == 'Windows':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        temp_USD = asyncio.run(get_exchange(item, USD))
        curr_USD += "\n" + temp_USD
        temp_EUR = asyncio.run(get_exchange(item, EUR))
        curr_EUR += "\n" + temp_EUR
    result = curr_USD.strip() + "\n" + curr_EUR.strip()
   
    return result



if __name__ == "__main__":
    print(main())
