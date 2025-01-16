import json
import sqlite3
from datetime import datetime
import pandas as pd

class PredictionTracker:
    def __init__(self, db_path='predictions.db'):
        self.db_path = db_path
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create predictions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            item_id INTEGER,
            current_price FLOAT,
            ma_14 FLOAT,
            ma_30 FLOAT,
            ma_90 FLOAT,
            rsi_14 FLOAT,
            rsi_30 FLOAT,
            rsi_90 FLOAT,
            upper_band_14 FLOAT,
            lower_band_14 FLOAT,
            upper_band_30 FLOAT,
            lower_band_30 FLOAT,
            upper_band_90 FLOAT,
            lower_band_90 FLOAT,
            signal_14 TEXT,
            signal_30 TEXT,
            signal_90 TEXT
        )''')
        
        # Create outcomes table for tracking actual results
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS outcomes (
            prediction_id INTEGER,
            actual_price FLOAT,
            outcome_timestamp DATETIME,
            success BOOLEAN,
            profit_loss FLOAT,
            FOREIGN KEY(prediction_id) REFERENCES predictions(id)
        )''')
        
        conn.commit()
        conn.close()

    def record_prediction(self, item_id, analysis_data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        current_time = datetime.now().isoformat()
        
        # Extract values from analysis data
        cursor.execute('''
        INSERT INTO predictions (
            timestamp, item_id, current_price,
            ma_14, ma_30, ma_90,
            rsi_14, rsi_30, rsi_90,
            upper_band_14, lower_band_14,
            upper_band_30, lower_band_30,
            upper_band_90, lower_band_90,
            signal_14, signal_30, signal_90
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            current_time, item_id,
            analysis_data['current_price'],
            analysis_data['ma_14'], analysis_data['ma_30'], analysis_data['ma_90'],
            analysis_data['rsi_14'], analysis_data['rsi_30'], analysis_data['rsi_90'],
            analysis_data['upper_14'], analysis_data['lower_14'],
            analysis_data['upper_30'], analysis_data['lower_30'],
            analysis_data['upper_90'], analysis_data['lower_90'],
            analysis_data['signal_14'], analysis_data['signal_30'], analysis_data['signal_90']
        ))
        
        prediction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return prediction_id

    def record_outcome(self, prediction_id, actual_price):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get original prediction
        cursor.execute('SELECT current_price, signal_14, signal_30, signal_90 FROM predictions WHERE id = ?', 
                      (prediction_id,))
        pred_data = cursor.fetchone()
        if not pred_data:
            return
        
        original_price, signal_14, signal_30, signal_90 = pred_data
        
        # Calculate success based on signals
        price_change = actual_price - original_price
        success = False
        
        # Simple success criteria (can be made more sophisticated)
        if "Sell" in signal_30 and price_change < 0:
            success = True
        elif "Buy" in signal_30 and price_change > 0:
            success = True
        
        cursor.execute('''
        INSERT INTO outcomes (prediction_id, actual_price, outcome_timestamp, success, profit_loss)
        VALUES (?, ?, ?, ?, ?)
        ''', (prediction_id, actual_price, datetime.now().isoformat(), success, price_change))
        
        conn.commit()
        conn.close()

    def get_accuracy_stats(self):
        conn = sqlite3.connect(self.db_path)
        query = '''
        SELECT 
            COUNT(*) as total_predictions,
            SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_predictions,
            AVG(CASE WHEN success = 1 THEN 1 ELSE 0 END) * 100 as success_rate,
            AVG(profit_loss) as avg_profit_loss
        FROM outcomes
        '''
        stats = pd.read_sql_query(query, conn)
        conn.close()
        return stats 