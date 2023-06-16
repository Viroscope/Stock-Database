# Database Builder

This program is used to build and update a database of stock tickers and their historical price data. It fetches stock ticker information from the Polygon API and retrieves historical price data for each ticker using the same API. The program is written in Python and utilizes SQLite for database management.

## Prerequisites

Before running the program, make sure you have the following:

- Python 3 installed on your system
- Required Python packages: `dotenv`, `sqlite3`, `requests`, `json`
- A valid API key for the Polygon API. You can obtain an API key by signing up on the Polygon website.

## Setup

1. Clone the repository or download the `Database_Builder.py` and `Database_Management.py` files.

2. Install the required packages by running the following command in your terminal:

   ```
   pip install python-dotenv
   ```

3. Create a file named `.env` in the same directory as the program files. Open the `.env` file and add the following line:

   ```
   PolygonKey=YOUR_POLYGON_API_KEY
   ```

   Replace `YOUR_POLYGON_API_KEY` with your actual Polygon API key.

## Usage

To build and update the database, follow these steps:

1. Run the `Database_Builder.py` script using Python:

   ```
   python Database_Builder.py
   ```

2. The program will check if the database file (`data.db`) exists and is greater than 20,000 bytes. If the file doesn't exist or is empty, it will update the known tickers in the database.

3. The program fetches ticker information from the Polygon API and updates the `tickers` table in the database.

4. After updating the tickers, the program creates or updates the `app_state` table in the database with the last processed ticker and sets the error status to 0.

5. The program proceeds to process each ticker in the `tickers` table. It fetches historical price data for each ticker using the Polygon API and stores it in a separate table in the database.

6. During the processing of tickers, the program displays the progress and handles any errors that may occur. It skips tickers with invalid formats or reserved keywords.

7. Once the program finishes processing all tickers, the database will be populated with the latest ticker information and historical price data.

## Customization

- To modify the duration of historical price data fetched, you can change the `From` and `To` variables in the `make_db` function of `Database_Management.py`. By default, it fetches data for the last 5000 days.

- You can adjust the `Multiplier`, `Timespan`, `Adjusted`, `Sort`, and `Limit` parameters in the `fetch_stock_data` function of `Database_Management.py` to customize the API request for historical price data. Refer to the Polygon API documentation for more details.

- The program uses the `data.db` file as the default database. If you want to use a different filename or location, you can modify the `db_filename` and `db_path` variables in both `Database_Builder.py` and `Database_Management.py` to match your desired configuration.

## Important Note

- The program assumes that you have set up the required tables (`tickers` and `app_state`) in the database. If the tables do not exist, the program will create them automatically.

- Make sure to handle the database file (`data.db`) with care. It contains sensitive financial data and should not be shared publicly or modified manually without proper knowledge.

## License

This program is licensed under the MIT License. You are free to use, modify, and distribute this program in accordance with the terms of the license. 

Proper attribution to the original author is required when using or distributing this program. Please provide credit to the original author as specified in the [LICENSE](LICENSE) file.

By using this program, you acknowledge and agree to comply with the attribution requirements outlined in the MIT License.