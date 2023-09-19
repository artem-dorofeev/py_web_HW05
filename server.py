import asyncio
import aiohttp
import logging
import names
import websockets
from websockets import WebSocketServerProtocol, WebSocketProtocolError
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)

LINK_BANK = 'https://api.privatbank.ua/p24api/exchange_rates?date='
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
    result = await request(LINK_BANK + date_currency)
    if result:
        temp_info = result['exchangeRate']
        exc, = list(filter(lambda el: el["currency"] == currency, temp_info))
        return f'{currency}: buy: {exc["purchaseRate"]}, sale: {exc["saleRate"]}. Date: {date_currency}'
    return "Failed to retrieve data"

def parser(text: str):
    pass


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
            if message.lower().startswith('exc'):
            # if message == 'exc':
                 r = await get_exchange()
                 await self.send_to_clients(r)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())