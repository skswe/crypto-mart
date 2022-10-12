from time import sleep
import websocket
import rel
import json
import requests
import sys
from threading import Thread, Timer
import traceback


class CoinFlexSocket():
    def __init__(self):
        self.base_url = 'wss://v2api.coinflex.com/v2/websocket'
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
            data = response['data']
            print(response)
            if response['table'] == 'candles300s':
                print('here')
                # temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                with open('CoinFlexKlines.txt', 'a') as f:
                    f.write(str(data))
                    f.write(f'\n')
            elif response['table'] == 'depthL10':
                # temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                with open('CoinFlexBooks.txt', 'a') as f:
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
        instrument_response = requests.get(
            'https://v2api.coinflex.com/v3/markets?marketCode').json()['data']
        self.symbols = list(
            map(lambda d: d['marketCode'], instrument_response))
        self.subscribe_to_kline_streams()
        self.subscribe_to_orderbook_streams()

    def subscribe_to_kline_streams(self):
        sleep(3)
        req = {
            "op": "subscribe",
            "tag": 1,
            "args": []
        }
        for symbol in self.symbols:
            req['args'].append("candles300s:" + symbol) 
        self.websocket.send(json.dumps(req))

    def subscribe_to_orderbook_streams(self):
       sleep(3)
       req = {
            "op": "subscribe",
            "tag": 103,
            "args": []
        }
       for symbol in self.symbols:
            req['args'].append("depthL10:" + symbol) 
       self.websocket.send(json.dumps(req))



