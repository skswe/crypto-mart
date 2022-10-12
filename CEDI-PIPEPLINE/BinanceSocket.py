
from time import sleep
import math
import websocket
import rel
import json
import sys
from threading import Thread, Timer
import traceback



class BinanceSocket():
    def __init__(self):
        self.base_url = 'wss://fstream.binance.com/ws/'
        self.symbols = []
        self.kline_urls = []
        self.book_urls = []
        self.websockets = []
        self.thread = []
        self.book_data_cache = []
        self.book_symbols_cache = set()
        self.connect()

    def create_kline_urls(self):
        urls = []
        for symbol in self.symbols:
            urls.append(symbol + "@kline_3m")
        return urls

    def create_book_urls(self):
        urls = []
        for symbol in self.symbols:
            urls.append(symbol + "@depth20")
        return urls

    def subscribe_to_streams(self, index):
        req = {
            "method": "SUBSCRIBE",
            "params":
            [

            ],
            "id": 1
        }
        half_symbols = math.floor((len(self.symbols)/2))
        if index == 0:
            for x in range(half_symbols):
                req['params'].append(self.kline_urls[x])
        if index == 1:
            for x in range(half_symbols):
                req['params'].append(
                    self.kline_urls[half_symbols + x])
        if index == 2:
            for x in range(half_symbols):
                req['params'].append(self.book_urls[x])
        if index == 3:
            for x in range(half_symbols):
                req['params'].append(self.book_urls[half_symbols + x])

        try:
            sleep(4)
            self.websockets[index].send(json.dumps(req))
        except websocket.WebSocketConnectionClosedException as ex:
            print(u'Binance Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)
        except Exception as ex:
            print(u'Binance Exception:{},{}'.format(
                str(ex), traceback.format_exc()), file=sys.stderr)

    def clear_book_cache(self):
        Timer(300.0, self.clear_book_cache).start()
        with open('binanceBooks.txt', 'a') as f:
            # Change the standard output to the file we created.
            # Reset the standard output to its original value
            for data in self.book_data_cache:
                f.write(str(data))
                f.write(f'\n')
        self.book_data_cache = []
        self.book_symbols_cache = set()

    def get_instruments_from_stream(self):
        sleep(5)
        req = {
            "method": "SUBSCRIBE",
            "params":
            [
                "!markPrice@arr",
            ],
            "id": 1
        }
        self.websockets[0].send(json.dumps(req))

    def unsubscribe_from_instruments_stream(self):
        sleep(3)
        req = {
            "method": "UNSUBSCRIBE",
            "params":
            [
                "!markPrice@arr",
            ],
            "id": 1
        }
        self.websockets[0].send(json.dumps(req))

    def connect(self):
        # start book data flushing function
        self.clear_book_cache
        # create 4 websocket clients to bypass streams per connection limit and incoming messages limits 
        for x in range(4):
            def on_message(websockets, message):
                response = json.loads(message)
                if isinstance(response, list):
                    # get symbols from mark price stream
                    if (response[0]['e'] == "markPriceUpdate"):
                        for res in response:
                            self.symbols.append(res['s'].lower())
                        self.unsubscribe_from_instruments_stream()
                        # create kline and book stream urls and then subscribe to streams
                        self.kline_urls= self.create_kline_urls()
                        self.book_urls = self.create_book_urls()
                        for x in range(4):
                            sleep(2)
                            self.subscribe_to_streams(x)
                else:
                    if response['e'] == 'kline':
                        data = response['k']
                        # only store Klines whose event time and data end time are within 3 seconds of each other
                        timeDiff = float(response['E']) - float(data['T'])
                        if timeDiff >= 0 and timeDiff <= 3000:
                            #temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                            with open('binanceKlines.txt', 'a') as f:
                                f.write(str(data))
                                f.write(f'\n')
                    elif response['e'] == 'depthUpdate':
                        #temporary save to text file for testing, data will be sent to datahandler module to be saved to database
                        if response['s'] not in self.book_symbols_cache:
                            self.book_data_cache.append([response['s'], response['E'],
                                                      response['T'], response['b'], response['a']])
                            self.book_symbols_cache.add(response['s'])

            def on_close(websockets, error, event):
                print("closed connection", error, event)

            def on_open(websockets):
                print("Opened connection")

            def on_error(websockets, error):
                print(error, "here")
            try:
                self.websockets.append(websocket.WebSocketApp(
                    self.base_url, on_message=on_message, on_close=on_close, on_open=on_open, on_error=on_error))

                self.thread.append(
                    Thread(target=self.websockets[x].run_forever))
                self.thread[x].start()
            except websocket.WebSocketConnectionClosedException as ex:
                print(u'Binance Connection Closed Exception:{},{}'.format(
                    str(ex), traceback.format_exc()), file=sys.stderr)
            except Exception as ex:
                print(u'Binance Exception:{},{}'.format(
                    str(ex), traceback.format_exc()), file=sys.stderr)

        self.get_instruments_from_stream()



