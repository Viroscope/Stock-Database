from Database_Management import *
from dotenv import dotenv_values

env_values = dotenv_values(".env")
PolygonKey = env_values["PolygonKey"]



script_dir = os.path.dirname(os.path.abspath(__file__))
db_filename = 'data.db'
db_path = os.path.join(script_dir, db_filename)




if os.path.exists(db_path) and os.path.getsize(db_path) > 20000:
    Update_Known_Tickers = 0
else:
    Update_Known_Tickers = 1

if Update_Known_Tickers == 1:
    get_polygon_tickers(PolygonKey)
    update_ticker_database(PolygonKey)
    add_app_state_row('', 0)
    Update_Known_Tickers = 0

make_db(PolygonKey)
