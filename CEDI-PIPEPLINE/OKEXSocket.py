from time import sleep
import websocket
import json
import sys
from threading import Thread, Timer
import traceback
import DatabaseHandler


class OKEXSocket():
    def __init__(self):
        self.base_url = 'wss://ws.okx.com:8443/ws/v5/public'
        self.websocket = None
        self.instrument_ids = []
        self.handler = DatabaseHandler.DatabaseHandler()
        self.connect()


    def close(self):
        if self.thread and self.thread.isAlive():
            print(u'OKEX.close')
            self.websocket.close()
            self.thread.join()

    def connect(self):
        def on_message(ws, message):
            response = json.loads(message)
            data = response['data']
            if response['arg']['channel'] == 'instruments':
                self.instrument_ids = list(map(lambda d: d['instId'], data))
            elif response['arg']['channel'] == 'books': 
                #temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                with open('okexBooks.txt', 'a') as f:
                    self.handler.add_books_okex(data,response['arg']["instId"])
                    f.write(response['arg']["instId"])
                    f.write(str(data))
                    f.write(f'\n')
            elif response['arg']['channel'] == 'candle15m': 
                #temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                with open('Klines.txt', 'a') as f:
                    self.handler.add_kline_okex(data,response['arg']["instId"])
    

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
        self.get_instruments_from_stream()

    def get_instruments_from_stream(self):
        sleep(5)
        print("here")
        req = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "instruments",
                    "instType": "FUTURES"
                }
            ]
        }
        try:
            self.websocket.send(json.dumps(req))
            sleep(2)
        except websocket.WebSocketConnectionClosedException as ex:
            print(u'OKEX.sendDataRequest Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)
        except Exception as ex:
            print(u'OKEX.sendDataRequest Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)
        self.subscribe_to_kline_streams()
        self.subscribe_to_orderbook_streams()

    def subscribe_to_kline_streams(self):
        sleep(3)
        req = {
            "op": "subscribe",
            "args": []
        }
        for id in self.instrument_ids:
            req['args'].append({"channel": "candle15m", "instId": id})

        self.websocket.send(json.dumps(req))
    
    def subscribe_to_orderbook_streams(self):
        sleep(3)
        req = {
            "op": "subscribe",
            "args": []
        }
        for id in self.instrument_ids:
            req['args'].append({"channel": "books", "instId": id})

        self.websocket.send(json.dumps(req))

test = OKEXSocket()