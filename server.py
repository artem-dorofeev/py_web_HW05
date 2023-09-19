import asyncio
import aiohttp
import logging
import names
from datetime import datetime, timedelta
import websockets
from websockets import WebSocketServerProtocol, WebSocketProtocolError
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)

LINK_BANK = 'https://api.privatbank.ua/p24api/exchange_rates?date='
# date_currency = '18.09.2023'
# currency = "USD"


def get_date():
    d = datetime.now()
    day = str(d.day) if d.day > 9 else '0' + str(d.day)
    month = str(d.month) if d.month > 9 else '0' + str(d.month)
    return f"{day}.{month}.{str(d.year)}"


def get_list_date(day: int):
    list_date = []
    d = datetime.now()
    for i in range(day):
        delta_day = timedelta(days=i)
        new_date = d - delta_day
        day = str(new_date.day) if new_date.day > 9 else '0' + \
            str(new_date.day)
        month = str(new_date.month) if new_date.month > 9 else '0' + \
            str(new_date.month)
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


async def get_exchange(currency, day_cur):
    list_date = get_list_date(day_cur)
    result_currency = ''

    for i in list_date:
        result = await request(LINK_BANK + i)
        if result:
            temp_info = result['exchangeRate']
            exc, = list(
                filter(lambda el: el["currency"] == currency, temp_info))
            result_currency += f' {currency}: buy: {exc["purchaseRate"]}, sale: {exc["saleRate"]}. Date: {i} '
        else:
            result_currency += f' Failed to retrieve data: {i} '

    return result_currency


COMMANDS = {
    "exchange": ("exchange", "exch", "exc", "обмін", ),
}

CURRENCY_VAL = {"USD": ("usd", "dollar", "долар", "usa", ),
                "EUR": ("eur", "євро", "евро", ),
                "GBP": ("gbp", "фунт", ),
                "CHF": ("chf", "франк", ),
                "PLZ": ("plz", "злотий"),
                }


def parser(text: str):
    exch_flag = False
    exch_cur = "USD"
    exch_day = 1
    text = text.lower().strip().split()

    for key, val in CURRENCY_VAL.items():
        for items in val:
            if items in text:
                exch_cur = key
                text.remove(items)

    for key, val in COMMANDS.items():
        for items in val:
            if items in text:
                exch_flag = True
                text.remove(items)

    for i in text:
        try:
            exch_day = int(i)
        except ValueError:
            continue

    if exch_day > 5:
        exch_day = 5

    return exch_flag, exch_cur, exch_day


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            flag, exch_cur, exch_day = parser(message)

            if flag:

                r = await get_exchange(exch_cur, exch_day)
                await self.send_to_clients(r)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())
