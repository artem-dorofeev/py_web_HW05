# тест функции гет_екс и реквест. добавить в файл сервера. и удалить перед сдачей ДЗ

import platform
from datetime import datetime
import logging

import aiohttp
import asyncio

link_bank = 'https://api.privatbank.ua/p24api/exchange_rates?date='
date_currency = '18.09.2023'
currency = "USD"

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


async def get_exchange():
    # result = await request('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5')
    result = await request(link_bank + date_currency)
    if result:
        temp_info = result['exchangeRate']
        exc, = list(filter(lambda el: el["currency"] == currency, temp_info))
        return f'{currency}: buy: {exc["purchaseRate"]}, sale: {exc["saleRate"]}. Date: {date_currency}'
    return "Failed to retrieve data"


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    result = asyncio.run(get_exchange())
    print(result)