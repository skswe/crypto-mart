from time import sleep
import websocket
import rel
import json
import sys
from threading import Thread, Timer
import traceback
import multiprocessing


class BitMexSocket():
    def __init__(self):
        self.base_url = 'wss://ws.bitmex.com/realtime'
        self.ws = None
        self.symbols = []
        self.connect()

        # self.socket = f'{self.fullUrl}'

    def close(self):
        if self.thread and self.thread.isAlive():
            print(u'Bitmex.close')
            self.ws.close()
            self.thread.join()

    def connect(self):
        def on_message(ws, message):
            response = json.loads(message)
            if response['table'] == "instrument" and response["action"] == "partial":
                for instrument in response['data']:
                    if '.' not in instrument['symbol']:
                        self.symbols.append(instrument['symbol'])
                print('got symbols')
                self.unsubscribe_from_instruments_stream()
                self.subscribe_to_orderbook_streams()
            elif response['table'] == "orderBookL2_25":
                with open('bitmexbooks.txt', 'a') as f:
                    f.write(str(response['data']))

        def on_close(ws):
            print("closed connection")

        def on_open(ws):
            print("Opened connection")

        def on_error(ws, evt):
            print(evt)
        self.ws = websocket.WebSocketApp(
            self.base_url, on_message=on_message, on_close=on_close, on_open=on_open, on_error=on_error)

        self.thread = Thread(target=self.ws.run_forever)
        self.thread.start()
        self.get_instruments_from_stream()

    def get_instruments_from_stream(self):
        sleep(5)
        req = {
            "op": "subscribe",
            "args": [

                "instrument",

            ]
        }
        try:
            self.ws.send(json.dumps(req))
            sleep(2)
        except websocket.WebSocketConnectionClosedException as ex:
            print(u' Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)
        except Exception as ex:
            print(u' Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)

    def unsubscribe_from_instruments_stream(self):
        sleep(5)
        req = {
            "op": "unsubscribe",
            "args": [

                "instrument",

            ]
        }
        try:
            self.ws.send(json.dumps(req))
            sleep(2)
        except websocket.WebSocketConnectionClosedException as ex:
            print(u' Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)
        except Exception as ex:
            print(u' Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)

    def subscribe_to_orderbook_streams(self):
        sleep(3)
        for symbol in self.symbols:
            req = {
                "op": "subscribe",
                "args": []
            }
            req['args'].append("orderBookL2_25:" + symbol)
            self.ws.send(json.dumps(req))


test = BitMexSocket()
