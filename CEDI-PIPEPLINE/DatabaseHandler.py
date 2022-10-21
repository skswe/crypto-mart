import mysql.connector
import time
import json


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
        self.cursor.execute(sql, values)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted.")

    def add_kline_coinflex(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('coinflex', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data[0]['candle'][0])/1000)), float(data[0]['candle'][1]), float(data[0]['candle'][4]), float(data[0]['candle'][2]), float(data[0]['candle'][3]), float(data[0]['candle'][5]))
        self.cursor.execute(sql, values)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted.")

    def add_kline_gateio(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('gateio', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['t']))), float(data['o']), float(data['c']), float(data['h']), float(data['l']), float(data['v']))
        self.cursor.execute(sql, values)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted.")

    def add_kline_okex(self, data, symbol):
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('okex', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data[0][0])/1000)), float(data[0][1]), float(data[0][4]), float(data[0][2]), float(data[0][3]), float(data[0][5]))
        self.cursor.execute(sql, values)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted.")

    def add_kline_binance(self, data, symbol):
        print(data, symbol)
        sql = "INSERT INTO klines (exchange_name, symbol_name, event_time, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = ('binance', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['T'])/1000)), float(data['o']), float(data['c']), float(data['h']), float(data['l']), float(data['v']))
        self.cursor.execute(sql, values)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted.")

    def add_books_okex(self, data, symbol):
        sql = "INSERT INTO orderbooks (exchange_name, symbol_name, event_time, asks, bids) VALUES (%s, %s, %s, %s, %s)"
        values = ('okex', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data[0]['ts'])/1000)), json.dumps(data[0]['asks']), json.dumps(data[0]['bids']))
        self.cursor.execute(sql, values)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted into books.")

    def add_books_gateio(self, data, symbol):
        sql = "INSERT INTO orderbooks (exchange_name, symbol_name, event_time, asks, bids) VALUES (%s, %s, %s, %s, %s)"
        values = ('gateio', symbol, time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(
            int(data['t'])/1000)), json.dumps(data['asks']), json.dumps(data['bids']))
        self.cursor.execute(sql, values)
        self.db.commit()
        print(self.cursor.rowcount, "record inserted into books.")


test = DatabaseHandler()
