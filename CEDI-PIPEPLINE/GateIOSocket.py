
from time import sleep
import websocket
import rel
import json
import requests
import sys
import time
from threading import Thread, Timer
import traceback
import multiprocessing


class GateIOSocket():
    def __init__(self):
        self.base_url = 'wss://api.gateio.ws/ws/v4/'
        self.websocket = None
        self.symbols = []
        self.connect()
        # self.socket = f'{self.fullUrl}'

    def close(self):
        if self.thread and self.thread.isAlive():
            self.websocket.close()
            self.thread.join()

    def connect(self):
        def on_message(ws, message):
            response = json.loads(message)
            data = response['result']
            if response['channel'] == "spot.candlesticks" and 'status' not in response:
                # temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                with open('GateIOKlines.txt', 'a') as f:
                    f.write(str(data))
                    f.write(f'\n')
            elif response['channel'] == "spot.order_book" and 'status' not in response:
                # temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                with open('GateIOBooks.txt', 'a') as f:
                    f.write(str(data))
                    f.write(f'\n')

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
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json'}
        instrument_response = requests.get(
            'https://api.gateio.ws/api/v4/spot/currency_pairs', headers=headers).json()
        self.symbols = list(map(lambda d: d['id'], instrument_response))
        self.subscribe_to_kline_streams()
        self.subscribe_to_orderbook_streams()

    def subscribe_to_kline_streams(self):
        sleep(3)
        for symbol in self.symbols:
            req = {
                "time": int(time.time()),
                "channel": "spot.candlesticks",
                "event": "subscribe",  # "unsubscribe" for unsubscription
                "payload": ["15m", symbol]
            }
            self.websocket.send(json.dumps(req))

    def subscribe_to_orderbook_streams(self):
        sleep(3)
        for symbol in self.symbols:
            req = {
                "time": int(time.time()),
                "channel": "spot.order_book",
                "event": "subscribe",  # "unsubscribe" for unsubscription
                "payload": [symbol, "20", "1000ms"]
            }
            self.websocket.send(json.dumps(req))


test = GateIOSocket()
