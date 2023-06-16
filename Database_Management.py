import os
import sqlite3
import requests
import json
from datetime import datetime
from datetime import date, timedelta
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
db_filename = 'data.db'
db_path = os.path.join(script_dir, db_filename)

spinner_chars = ['/', '-', '\\', '|']

def clear_screen():
    if os.name == 'nt':  # for Windows
        os.system('cls')
    else:  # for Unix/Linux/Mac
        os.system('clear')
        
def add_app_state_row(last_ticker, error_occurred):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO app_state (last_ticker, error_occurred) VALUES (?, ?)", (last_ticker, error_occurred))
    conn.commit()
    cursor.close()
    conn.close()

def update_ticker_database(api_key):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickers")
    conn.commit()
    cursor.close()
    conn.close()
    tickers_data = get_polygon_tickers(api_key)
    if tickers_data is not None:
        print("Total tickers:", len(tickers_data))
    else:
        print('Failed to fetch tickers data.')

def create_tickers_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tickers (
            ticker TEXT,
            name TEXT,
            market TEXT,
            locale TEXT,
            currency TEXT,
            active INTEGER,
            cik TEXT,
            composite_figi TEXT,
            currency_name TEXT,
            delisted_utc TEXT,
            last_updated_utc TEXT,
            primary_exchange TEXT,
            share_class_figi TEXT,
            type TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS app_state (
            last_ticker TEXT,
            error_occurred INTEGER
        )
    ''')
    conn.commit()
    conn.commit()

def insert_ticker_data(conn, ticker_data):
    c = conn.cursor()
    c.executemany('''
        INSERT INTO tickers (
            ticker, name, market, locale, currency, active, cik, composite_figi,
            currency_name, delisted_utc, last_updated_utc, primary_exchange,
            share_class_figi, type
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ticker_data)

def get_polygon_tickers(api_key):
    url = 'https://api.polygon.io/v3/reference/tickers'
    params = {
        'market': 'stocks',
        'active': 'true',
        'sort': 'ticker',
        'apiKey': api_key
    }
    conn = sqlite3.connect(db_path)
    create_tickers_table(conn)
    tickers_data = []
    next_url = url
    while next_url:
        response = requests.get(next_url, params=params)
        if response.status_code == 200:
            data = response.json()
            tickers_data.extend(data.get('results', []))
            next_url = data.get('next_url')
            ticker_data = []
            spinner_index = 0
            for ticker in data.get('results', []):
                ticker_data.append((
                    ticker.get('ticker', 'N/A'),
                    ticker.get('name', 'N/A'),
                    ticker.get('market', 'N/A'),
                    ticker.get('locale', 'N/A'),
                    ticker.get('currency', 'N/A'),
                    ticker.get('active', 'N/A'),
                    ticker.get('cik', 'N/A'),
                    ticker.get('composite_figi', 'N/A'),
                    ticker.get('currency_name', 'N/A'),
                    ticker.get('delisted_utc', 'N/A'),
                    ticker.get('last_updated_utc', 'N/A'),
                    ticker.get('primary_exchange', 'N/A'),
                    ticker.get('share_class_figi', 'N/A'),
                    ticker.get('type', 'N/A')
                ))
            print(f"\rProcessing {spinner_chars[spinner_index]}", end='')
            spinner_index = (spinner_index + 1) % len(spinner_chars)
            insert_ticker_data(conn, ticker_data)
        else:
            print('Failed to fetch tickers data.')
            print("Error response:", json.dumps(response.json(), indent=2))
            return None
    conn.commit()
    conn.close()
    return tickers_data

class DataEntry:
    def __init__(self, date, volume, open_price, close_price, high_price, low_price, vw_price):
        self.date = date
        self.volume = volume
        self.open_price = open_price
        self.close_price = close_price
        self.high_price = high_price
        self.low_price = low_price
        self.vw_price = vw_price

    def __str__(self):
        return f"DataEntry(date={self.date}, volume={self.volume}, open_price={self.open_price}, close_price={self.close_price}, high_price={self.high_price}, low_price={self.low_price}, vw_price={self.vw_price})"

    def to_tuple(self):
        return (self.date, self.volume, self.open_price, self.close_price, self.high_price, self.low_price, self.vw_price)

def fetch_stock_data(ticker, multiplier, timespan, start_date, end_date, adjusted, sort, limit, api_key):
    create_table(ticker)
    URL = "https://api.polygon.io/v2/aggs/ticker/"
    url = f"{URL}{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}?adjusted={adjusted}&sort={sort}&limit={limit}&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        reformat(json_data, ticker)
    else:
        print(f"Failed to fetch data for ticker: {ticker}")

def create_table(ticker):
    table_name = f"[{ticker.strip()}]"
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(f"DROP TABLE IF EXISTS {table_name}")
    c.execute(f'''CREATE TABLE {table_name} (
                    date TEXT PRIMARY KEY,
                    volume REAL,
                    open_price REAL,
                    close_price REAL,
                    high_price REAL,
                    low_price REAL,
                    vw_price REAL
                )''')
    conn.commit()
    conn.close()

def reformat(json_data, ticker):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    entries = []
    results = json_data['results']
    for result in results:
        timestamp = result['t'] / 1000
        date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        volume = result.get('v')
        open_price = result.get('o')
        close_price = result.get('c')
        high_price = result.get('h')
        low_price = result.get('l')
        vw_price = result.get('vw')
        missing_keys = [key for key, value in [('v', volume), ('o', open_price), ('c', close_price),
                                               ('h', high_price), ('l', low_price), ('vw', vw_price)]
                        if value is None]
        if len(missing_keys) > 2:
            print(f"Warning: More than two keys are missing for ticker '{ticker}' at timestamp {timestamp}")
            continue
        entry = DataEntry(date, volume, open_price, close_price, high_price, low_price, vw_price)
        entries.append(entry)
    insert_entries(c, ticker, entries)
    conn.commit()
    conn.close()

def insert_entries(cursor, ticker, entries):
    values = [entry.to_tuple() for entry in entries]
    cursor.executemany(f"INSERT INTO {ticker} VALUES (?, ?, ?, ?, ?, ?, ?)", values)

def update_last_ticker(cursor, conn, ticker):
    try:
        update_query = "UPDATE app_state SET last_ticker = ?, error_occurred = 0 WHERE ROWID = 1"
        print("Update Last Ticker Query:", update_query)
        cursor.execute(update_query, (ticker,))
        rows_affected = cursor.rowcount
        print(f"Rows affected: {rows_affected}")
        conn.commit()
    except Exception as e:
        print(f"Error occurred while updating last ticker: {str(e)}")

def make_db(PolygonKey):
    Multiplier = 1
    Timespan = "day"
    From = (date.today() - timedelta(days=5000)).strftime("%Y-%m-%d")
    To = date.today().strftime("%Y-%m-%d")
    Adjusted = "true"
    Sort = "desc"
    Limit = 1000
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_tickers_table(conn)
    cursor.execute("SELECT ticker FROM tickers")
    tickers_in_database = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT last_ticker FROM app_state")
    last_ticker = cursor.fetchone()
    if last_ticker and last_ticker[0] in tickers_in_database:
        last_ticker_index = tickers_in_database.index(last_ticker[0])
        tickers_to_process = tickers_in_database[last_ticker_index:]
    else:
        tickers_to_process = tickers_in_database
    total_tickers = len(tickers_to_process)
    print("Total tickers to process:", total_tickers)
    for index, ticker in enumerate(tickers_to_process, start=1):
        if not re.match("^[a-zA-Z0-9]+$", ticker) or ticker == "ADD" or ticker == "ALL":
            print(f"Skipping ticker {ticker} (Invalid format or reserved keyword)")
            continue
        try:
            clear_screen()
            print(f"Processing ticker {ticker} ({index}/{total_tickers})")
            fetch_stock_data(ticker, Multiplier, Timespan, From, To, Adjusted, Sort, Limit, PolygonKey)
            print(f"Successfully processed ticker {ticker}")
            
            update_last_ticker_query = "UPDATE app_state SET last_ticker = ? WHERE ROWID = 1"
            cursor.execute(update_last_ticker_query, (ticker,))
            conn.commit()
        except Exception as e:
            print(f"Error occurred during processing of {ticker}: {str(e)}")
            print("Processing will continue with the next ticker.")
    cursor.close()
    conn.close()
