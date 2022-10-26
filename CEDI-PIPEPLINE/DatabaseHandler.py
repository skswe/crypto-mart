from datetime import datetime, timedelta
import mysql.connector
import time
import json
import re


class DatabaseHandler:
    def __init__(self):
        self.user = 'root'
        self.password = 'agrahul88888888#'
        self.db = None
        self.cursor = None
        self.connect()
        self.create_klines_table()
        self.create_books_table()

    def connect(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user=self.user,
            password=self.password,
            database='cedipipeline'
        )

        self.cursor = self.db.cursor(buffered=True)
        self.cursor.execute("SHOW DATABASES")

    def create_books_table(self):
        self.cursor.execute("SHOW TABLES")
        tables = []
        for x in self.cursor:
            print(x[0])
            tables.append(x[0])
        if 'orderbooks' not in tables:
            print(tables)
            self.cursor.execute(
                "CREATE TABLE orderbooks (id INT AUTO_INCREMENT PRIMARY KEY, exchange_name VARCHAR(255), symbol_name VARCHAR(255), event_time TIMESTAMP, asks JSON, bids JSON)")

    def create_klines_table(self):
        self.cursor.execute("SHOW TABLES")
        tables = []
        for x in self.cursor:
            print(x[0])
            tables.append(x[0])
        if 'klines' not in tables:
            print(tables)
            self.cursor.execute(
                "CREATE TABLE klines (id INT AUTO_INCREMENT PRIMARY KEY, exchange_name VARCHAR(255), symbol_name VARCHAR(255), event_time TIMESTAMP, open FLOAT, close FLOAT, high FLOAT, low FLOAT, volume FLOAT)")

    def add_kline_bybit(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('bybit', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            data[0]['end'])), data[0]['open'], data[0]['close'], data[0]['high'], data[0]['low'], data[0]['volume'])
        if self.query_timestamp_kline('bybit', symbol):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted bybit.")

    def add_kline_coinflex(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('coinflex', symbol.replace('-SWAP-LIN', '').replace('-', ""), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data[0]['candle'][0])/1000)), float(data[0]['candle'][1]), float(data[0]['candle'][4]), float(data[0]['candle'][2]), float(data[0]['candle'][3]), float(data[0]['candle'][5]))
        if self.query_timestamp_kline('coinflex', symbol.replace('-SWAP-LIN', '').replace('-', "")):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted coinflex.")

    def add_kline_gateio(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('gateio', symbol.replace('15m_', '').replace("_", ""), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['t']))), float(data['o']), float(data['c']), float(data['h']), float(data['l']), float(data['v']))
        if self.query_timestamp_kline('gateio', symbol.replace('15m_', '').replace("_", "")):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted gateio.")

    def add_kline_okex(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('okex', re.sub('\d', '', symbol.replace("-", "")), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data[0][0])/1000)), float(data[0][1]), float(data[0][4]), float(data[0][2]), float(data[0][3]), float(data[0][5]))
        if self.query_timestamp_kline('okex', re.sub('\d', '', symbol.replace("-", ""))):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted okex.")

    def add_kline_kucoin(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('kucoin', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['candles'][0]))), float(data['candles'][1]), float(data['candles'][2]), float(data['candles'][3]), float(data['candles'][4]), float(data['candles'][5]))
        if self.query_timestamp_kline('kucoin', symbol):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted kucoin.")

    def add_kline_binance(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('binance', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['T'])/1000)), float(data['o']), float(data['c']), float(data['h']), float(data['l']), float(data['v']))
        if self.query_timestamp_kline('binance', symbol):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted.")

    def add_books_okex(self, data, symbol):
        sql = "INSERT INTO orderbooks (exchange_name, symbol_name, event_time, asks, bids) VALUES (%s, %s, %s, %s, %s)"
        values = ('okex', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data[0]['ts'])/1000)), json.dumps(data[0]['asks']), json.dumps(data[0]['bids']))
        if self.query_timestamp_books('okex', re.sub('\d', '', symbol.replace("-", ""))):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted into okex books.")

    def add_books_gateio(self, data, symbol):
        sql = "INSERT INTO orderbooks (exchange_name, symbol_name, event_time, asks, bids) VALUES (%s, %s, %s, %s, %s)"
        values = ('gateio', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['t'])/1000)), json.dumps(data['asks']), json.dumps(data['bids']))
        if self.query_timestamp_books('gateio', symbol.replace('15m_', '').replace("_", "")):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted into gateio books.")

    def add_books_coinflex(self, data, symbol):
        sql = "INSERT INTO orderbooks (exchange_name, symbol_name, event_time, asks, bids) VALUES (%s, %s, %s, %s, %s)"
        values = ('coinflex', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['timestamp'])/1000)),  json.dumps(data['asks']),  json.dumps(data['bids']))
        if self.query_timestamp_books('coinflex', symbol.replace('-SWAP-LIN', '').replace('-', "")):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted into coinflex books.")

    def add_books_binance(self, data, symbol):
        sql = "INSERT INTO orderbooks (exchange_name, symbol_name, event_time, asks, bids) VALUES (%s, %s, %s, %s, %s)"
        values = ('binance', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data[2])/1000)),  json.dumps(data[4]),  json.dumps(data[3]))
        if self.query_timestamp_books('binance', symbol):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted into books.")

    def add_books_kucoin(self, data, symbol):
        sql = "INSERT INTO orderbooks (exchange_name, symbol_name, event_time, asks, bids) VALUES (%s, %s, %s, %s, %s)"
        values = ('kucoin', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['timestamp'])/1000)),  json.dumps(data["asks"]),  json.dumps(data["bids"]))
        if self.query_timestamp_books('binance', symbol):
            self.cursor.execute(sql, values)
            self.db.commit()
            print(self.cursor.rowcount, "record inserted into kucoin.")

    def query_records_exchange(self, exchange):
        print(exchange)
        sql = "SELECT event_time FROM klines WHERE exchange_name = %s"
        self.cursor.execute(sql, exchange)
        print(self.cursor.fetchone())

    def query_timestamp_kline(self, exchange, symbol):
        datetime_3minutes = timedelta(minutes=3)
        sql = "SELECT event_time FROM klines WHERE exchange_name = %s AND symbol_name = %s"
        values = (exchange, symbol)
        self.cursor.execute(sql, values)
        if self.cursor.fetchone() is None:
            return True
        else:
            print(datetime_3minutes > (
                datetime.now() - self.cursor.fetchone()[0]))
            return datetime_3minutes > (datetime.now() - self.cursor.fetchone()[0])

    def query_timestamp_books(self, exchange, symbol):
        datetime_3minutes = timedelta(minutes=3)
        sql = "SELECT event_time FROM orderbooks WHERE exchange_name = %s AND symbol_name = %s"
        values = (exchange, symbol)
        self.cursor.execute(sql, values)
        if self.cursor.fetchone() is None:
            print('no records')
            return True
        else:
            print(datetime_3minutes > (
                datetime.now() - self.cursor.fetchone()[0]))
            return datetime_3minutes > (datetime.now() - self.cursor.fetchone()[0])

    def delete_all_records(self):
        sql = "DELETE FROM klines"
        self.cursor.execute(sql)
        self.db.commit()
        sql = "DELETE FROM orderbooks"
        self.cursor.execute(sql)
        self.db.commit()


test = DatabaseHandler().delete_all_records()
