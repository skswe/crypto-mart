from time import sleep
import websocket
import rel
import json
import requests
import sys
import DatabaseHandler
from threading import Thread, Timer


class BybitSocket():
    def __init__(self):
        self.base_url = 'wss://stream-testnet.bybit.com/realtime'
        self.websocket = None
        self.symbols = []
        self.handler = DatabaseHandler.DatabaseHandler()
        self.connect()

    def close(self):
        if self.thread and self.thread.isAlive():
            self.websocket.close()
            self.thread.join()

    def connect(self):
        def on_message(ws, message):
            response = json.loads(message)
            data = response['data']
            if 'type' in response:
                # temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                with open('bybitBooks.txt', 'a') as f:
                    f.write(str(data))
                    f.write(f'\n')
            else:
                self.handler.add_kline_bybit(
                    data, response['topic'].removeprefix('klineV2.15.'))

        def on_close(ws):
            print("closed connection")

        def on_open(ws):
            print("Opened connection")

        def on_error(ws, evt):
            print(evt)
        self.websocket = websocket.WebSocketApp(
            self.base_url, on_message=on_message, on_close=on_close, on_open=on_open, on_error=on_error)

        self.thread = Thread(target=self.websocket.run_forever)
        self.thread.start()
        self.get_instuments()

    def get_instuments(self):
        instrument_response = requests.get(
            'https://api.bybit.com//v2/public/symbols').json()['result']
        self.symbols = list(map(lambda d: d['name'], instrument_response))
        self.subscribe_to_kline_streams()
        self.subscribe_to_orderbook_streams()

    def subscribe_to_kline_streams(self):
        sleep(3)
        req = {
            "op": "subscribe",
            "args": ["klineV2.15.*"]
        }
        # for symbol in self.symbols:
        #     req['args'][0] = req['args'][0] + symbol + "|"
        # req['args'][0] = req['args'][0][:-1]
        self.websocket.send(json.dumps(req))

    def subscribe_to_orderbook_streams(self):
        sleep(3)
        req = {
            "op": "subscribe",
            "args": ["orderBookL2_25.*"]
        }
        # for symbol in self.symbols:
        #     req['args'][0] = req['args'][0] + symbol + "|"
        # req['args'][0] = req['args'][0][:-1]
        self.websocket.send(json.dumps(req))


test = BybitSocket()
