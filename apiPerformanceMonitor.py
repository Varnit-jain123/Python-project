import time
import threading
import sqlite3
import requests
from flask import Flask, jsonify

app = Flask(__name__)

DB_FILE = 'api_monitor.db'
API_ENDPOINT = 'https://raw.githubusercontent.com/Lexie88rus/bank-marketing-analysis/master/bank.csv'

def setup_database():
    """
    Make sure our database and table are ready.
    If they don’t exist, create them.
    """
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS api_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                response_time_ms REAL,
                status_code INTEGER
            )
        ''')
        conn.commit()

def save_metric(timestamp, response_time, status_code):
    """
    Save a single API check result into the database.
    """
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            'INSERT INTO api_metrics (timestamp, response_time_ms, status_code) VALUES (?, ?, ?)',
            (timestamp, response_time, status_code)
        )
        conn.commit()

def monitor_api_every(interval=60):
    """
    Keep pinging the API every `interval` seconds,
    and save how long it took and the status code.
    """
    while True:
        start_time = time.time()
        try:
            response = requests.get(API_ENDPOINT, timeout=10)
            status = response.status_code
        except requests.RequestException:
            status = 0  # 0 means something went wrong (timeout, network error, etc.)

        end_time = time.time()
        elapsed_ms = (end_time - start_time) * 1000  # Convert to milliseconds
        current_ts = int(time.time())

        save_metric(current_ts, elapsed_ms, status)

        print(f"Recorded: status={status}, took {elapsed_ms:.2f} ms")

        time.sleep(interval)

@app.route('/metrics')
def get_metrics():
    """
    Let’s see the last 100 API check records in JSON format.
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute('''
            SELECT timestamp, response_time_ms, status_code
            FROM api_metrics
            ORDER BY timestamp DESC
            LIMIT 100
        ''')
        rows = cursor.fetchall()

    metrics = [
        {"timestamp": ts, "response_time_ms": rt, "status_code": sc}
        for ts, rt, sc in rows
    ]
    return jsonify(metrics)

if __name__ == '__main__':
    setup_database()
    
    # Run the monitor function on a separate thread so Flask can serve web requests too
    thread = threading.Thread(target=monitor_api_every, args=(60,), daemon=True)
    thread.start()
    
    print("Starting API Performance Monitor...")
    app.run(host='0.0.0.0', port=5000)
