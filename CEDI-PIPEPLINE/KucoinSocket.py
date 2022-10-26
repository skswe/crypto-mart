from time import sleep
from urllib import response
from xml.etree.ElementInclude import include
import websocket
import requests
import json
import sys
from threading import Thread, Timer
import traceback
import DatabaseHandler


class KucoinSocket():
    def __init__(self):
        self.base_url = 'wss://ws-api.kucoin.com/endpoint'
        self.websocket = None
        self.symbols = set()
        self.handler = DatabaseHandler.DatabaseHandler()
        self.connect()

    def close(self):
        if self.thread and self.thread.isAlive():
            print(u'Kucoin.close')
            self.websocket.close()
            self.thread.join()

    def send_ping(self):
        Timer(30.0, self.send_ping).start()
        req = {
            "id": 1525910360739,
            "type": "ping"
        }
        self.websocket.send(json.dumps(req))

    def establish_connection(self):
        url = 'https://api.kucoin.com/api/v1/bullet-public'
        post_data = {
            "code": "200000",
            "data": {

                "instanceServers": [
                    {
                        "endpoint": "wss://push1-v2.kucoin.com/endpoint",
                        "protocol": "websocket",
                        "encrypt": False,
                        "pingInterval": 50000,
                        "pingTimeout": 10000
                    }
                ],
                "token": "vYNlCtbz4XNJ1QncwWilJnBtmmfe4geLQDUA62kKJsDChc6I4bRDQc73JfIrlFaVYIAE0Gv2--MROnLAgjVsWkcDq_MuG7qV7EktfCEIphiqnlfpQn4Ybg==.IoORVxR2LmKV7_maOR9xOg=="
            }
        }

        resp = requests.post(url, json=post_data)
        print(resp.json()['data'])
        return resp.json()['data']['token']

    def connect(self):
        def on_message(ws, message):
            response = json.loads(message)
            data = response['data']
            if response['topic'] == '/market/ticker:all':
                self.symbols.add(response['subject'])
            elif '/spotMarket/level2Depth5' in response['topic']:
                self.handler.add_books_kucoin(
                    response['data'], response['topic'].replace('/spotMarket/level2Depth5:', ""))
            elif '/market/candles:' in response['topic']:
                self.handler.add_kline_kucoin(
                    response['data'], response['data']['symbol'])

        def on_close(ws):
            print("closed connection")

        def on_open(ws):
            print("Opened connection")

        def on_error(ws, evt):
            print(evt)

        token = self.establish_connection()
        base_url_token = self.base_url + "?token=" + \
            token + "&[connectId=hQvf8jkno]"
        self.websocket = websocket.WebSocketApp(
            base_url_token, on_message=on_message, on_close=on_close, on_open=on_open, on_error=on_error)

        self.thread = Thread(target=self.websocket.run_forever)
        self.thread.start()
        self.get_instruments_from_stream()

    def get_instruments_from_stream(self):
        sleep(5)
        req = {
            "id": 1545910660739,
            "type": "subscribe",
            "topic": "/market/ticker:all",
            "response": True
        }
        try:
            self.websocket.send(json.dumps(req))
            sleep(2)
        except websocket.WebSocketConnectionClosedException as ex:
            print(u'Kucoin.sendDataRequest Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)
        except Exception as ex:
            print(u'Kucoin.sendDataRequest Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)
        sleep(4)
        self.subscribe_to_kline_streams()
        self.subscribe_to_orderbook_streams()

    def unsubscribe_from_instrument_stream(self):
        req = {
            "id": 1545910660439,
            "type": "unsubscribe",
            "topic": "/market/ticker:all",
            "response": True
        }
        self.websocket.send(json.dumps(req))

    def subscribe_to_kline_streams(self):
        sleep(4)
        self.unsubscribe_from_instrument_stream()
        self.send_ping()
        req = {
            "id": 1545910660741,
            "type": "subscribe",
            "topic": "/market/candles:",
            "privateChannel": False,
            "response": True
        }
        count = 0
        for symbol in self.symbols:
            count = count + 1
            if count == 120:
                break
            if 'USD' in symbol:
                req['topic'] = req['topic'] + symbol + "_3min,"
        req['topic'] = req["topic"][:-1]
        self.websocket.send(json.dumps(req))

    def subscribe_to_orderbook_streams(self):
        sleep(3)
        req = {
            "id": 1545910660741,
            "type": "subscribe",
            "topic": "/spotMarket/level2Depth5:",
            "privateChannel": False,
            "response": True
        }
        count = 0
        for symbol in self.symbols:
            count = count + 1
            if count == 120:
                break
            if 'USD' in symbol:
                req['topic'] = req['topic'] + symbol + ","
        req['topic'] = req["topic"][:-1]
        self.websocket.send(json.dumps(req))


test = KucoinSocket()
