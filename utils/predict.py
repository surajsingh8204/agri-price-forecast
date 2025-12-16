"""
Prediction utilities for crop price forecasting
"""
import pandas as pd
import joblib
import os
from typing import List, Tuple, Dict


def get_model_path(crop: str, state: str) -> str:
    """Get the model file path for a given crop and state"""
    model_path = f"models/{crop}_{state}.pkl"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    return model_path


def load_model(crop: str, state: str):
    """Load the trained model for a given crop and state"""
    model_path = get_model_path(crop, state)
    model = joblib.load(model_path)
    return model


def make_daily_ts(df: pd.DataFrame, crop: str, state: str) -> pd.DataFrame:
    """
    Create daily time series for a specific crop and state
    Returns a DataFrame with Date index and Price column
    """
    # Filter crop & state
    ts = df[
        (df['Commodity'] == crop) &
        (df['STATE'] == state)
    ][['Date', 'Price']].copy()
    
    if ts.empty:
        raise ValueError(f"No data found for {crop} in {state}")
    
    # Sort & set index
    ts = ts.sort_values('Date')
    ts = ts.set_index('Date')
    
    # Resample to daily
    ts_daily = ts.resample('D').mean()
    
    # Interpolate missing values
    ts_daily['Price'] = ts_daily['Price'].interpolate(method='time')
    ts_daily['Price'] = ts_daily['Price'].ffill().bfill()
    
    return ts_daily


def make_features(ts_daily: pd.DataFrame) -> pd.DataFrame:
    """
    Create features from time series for model prediction
    """
    df_feat = ts_daily.copy()
    
    # Time-based features (using 'day' not 'year' - matches training)
    df_feat['day'] = df_feat.index.day
    df_feat['month'] = df_feat.index.month
    df_feat['dayofweek'] = df_feat.index.dayofweek
    df_feat['weekofyear'] = df_feat.index.isocalendar().week.astype(int)
    
    # Lag features
    for lag in [1, 7, 14, 30]:
        df_feat[f'lag_{lag}'] = df_feat['Price'].shift(lag)
    
    # Rolling statistics
    df_feat['ma_7'] = df_feat['Price'].rolling(7).mean()
    df_feat['ma_14'] = df_feat['Price'].rolling(14).mean()
    df_feat['ma_30'] = df_feat['Price'].rolling(30).mean()
    df_feat['std_7'] = df_feat['Price'].rolling(7).std()
    
    return df_feat.dropna()


def get_recent_ts(df: pd.DataFrame, crop: str, state: str, days: int = 60) -> pd.DataFrame:
    """
    Get recent time series data for prediction
    """
    ts = make_daily_ts(df, crop, state)
    
    if len(ts) < days:
        raise ValueError("Not enough historical data")
    
    return ts.iloc[-days:]


def prepare_latest_features(ts_recent: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare features from recent time series
    Takes the last row which represents "today"
    """
    ts_feat = make_features(ts_recent)
    
    # Take LAST row → represents "today"
    X_latest = ts_feat.drop(columns=['Price']).iloc[-1:]
    
    return X_latest


def predict_next_day_price(df: pd.DataFrame, crop: str, state: str) -> float:
    """
    Predict next day's price for given crop and state
    
    Parameters:
    - df: DataFrame with crop price data
    - crop: Crop name (e.g., 'Potato', 'Onion', 'Tomato', 'Rice', 'Wheat')
    - state: State name (e.g., 'Punjab', 'Uttar Pradesh')
    
    Returns:
    - Predicted price for next day
    """
    # 1. Load model
    model = load_model(crop, state)
    
    # 2. Get recent data
    ts_recent = get_recent_ts(df, crop, state)
    
    # 3. Prepare features
    X_latest = prepare_latest_features(ts_recent)
    
    # 4. Predict
    predicted_price = model.predict(X_latest)[0]
    
    return round(float(predicted_price), 2)


def forecast_prices(df: pd.DataFrame, crop: str, state: str, days: int = 7) -> List[Tuple]:
    """
    Forecast prices for next N days using recursive strategy
    
    Parameters:
    - df: DataFrame with crop price data
    - crop: Crop name
    - state: State name
    - days: Number of days to forecast
    
    Returns:
    - List of tuples (date, predicted_price)
    """
    model = load_model(crop, state)
    ts = make_daily_ts(df, crop, state)
    
    forecasts = []
    
    for _ in range(days):
        ts_recent = ts.iloc[-60:]
        ts_feat = make_features(ts_recent)
        X_latest = ts_feat.drop(columns=['Price']).iloc[-1:]
        
        next_price = model.predict(X_latest)[0]
        next_price = float(next_price)
        
        next_date = ts.index[-1] + pd.Timedelta(days=1)
        
        ts.loc[next_date] = next_price
        forecasts.append((next_date.date(), round(next_price, 2)))
    
    return forecasts


def get_trend(forecasts: List[Tuple]) -> Tuple[float, str]:
    """
    Calculate trend from forecast prices
    
    Parameters:
    - forecasts: List of tuples (date, price)
    
    Returns:
    - Tuple of (percent_change, trend_description)
    """
    prices = [p for _, p in forecasts]
    
    delta = prices[-1] - prices[0]
    pct_change = (delta / prices[0]) * 100
    
    if pct_change > 5:
        trend = "Strong Upward 📈"
    elif pct_change > 2:
        trend = "Upward 📈"
    elif pct_change < -5:
        trend = "Strong Downward 📉"
    elif pct_change < -2:
        trend = "Downward 📉"
    else:
        trend = "Stable ➝"
    
    return round(pct_change, 2), trend


def forecast_summary(df: pd.DataFrame, crop: str, state: str, days: int = 7) -> Dict:
    """
    Generate forecast summary with trend analysis
    
    Parameters:
    - df: DataFrame with crop price data
    - crop: Crop name
    - state: State name
    - days: Number of days to forecast (default: 7)
    
    Returns:
    - Dictionary with forecast summary including:
        - crop, state, days
        - start_price, end_price
        - percent_change, trend, trend_emoji
        - daily_forecast (list of objects with date and price)
    """
    forecast = forecast_prices(df, crop, state, days)
    pct_change, trend = get_trend(forecast)
    
    start_price = forecast[0][1]
    end_price = forecast[-1][1]
    
    # Extract emoji from trend string
    trend_emoji = trend.split()[-1] if any(c in trend for c in ['📈', '📉', '➝']) else ''
    trend_text = trend.rsplit(' ', 1)[0] if trend_emoji else trend
    
    # Convert forecast tuples to objects for JSON serialization
    daily_forecast = [
        {"date": str(date), "price": price}
        for date, price in forecast
    ]
    
    summary = {
        "crop": crop,
        "state": state,
        "days": days,
        "start_price": start_price,
        "end_price": end_price,
        "percent_change": pct_change,
        "trend": trend_text,
        "trend_emoji": trend_emoji,
        "daily_forecast": daily_forecast
    }
    
    return summary
