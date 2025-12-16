"""
Agricultural Crop Price Prediction API
FastAPI backend for crop price forecasting
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
from typing import Optional
import os

from utils.predict import (
    predict_next_day_price,
    forecast_summary
)

# Initialize FastAPI app
app = FastAPI(
    title="Agri Market Price Forecast API",
    description="Crop price prediction & forecasting for Indian agricultural markets",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data once at startup
DATA_PATH = "data/Agriculture_price_dataset.csv"
if os.path.exists("croppricedata/Agriculture_price_dataset.csv"):
    DATA_PATH = "croppricedata/Agriculture_price_dataset.csv"

print(f"Loading data from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

# Data preprocessing
df.rename(columns={
    'Price Date': 'Date',
    'Modal_Price': 'Price',
    'Market Name': 'Market',
    'District Name': 'District'
}, inplace=True)

df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df = df.dropna(subset=['Date', 'Price'])

# Normalize state names
df['STATE'] = df['STATE'].str.strip()
state_map = {
    'Chattisgarh': 'Chhattisgarh',
    'Orissa': 'Odisha',
    'Uttrakhand': 'Uttarakhand',
    'Tamilnadu': 'Tamil Nadu',
    'Jammu & Kashmir': 'Jammu and Kashmir'
}
df['STATE'] = df['STATE'].replace(state_map)

print(f"Data loaded successfully! Shape: {df.shape}")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    """Serve frontend"""
    return FileResponse("static/index.html")


@app.get("/api")
def api_root():
    """API status endpoint"""
    return {
        "status": "online",
        "service": "Agri Market Price Forecast API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/api/predict?crop={crop}&state={state}",
            "forecast": "/api/forecast?crop={crop}&state={state}&days={days}",
            "crops": "/api/crops",
            "states": "/api/states"
        }
    }


@app.get("/api/crops")
def get_crops():
    """Get list of available crops"""
    crops = ['Potato', 'Onion', 'Wheat', 'Tomato', 'Rice']
    return {"crops": crops}


@app.get("/api/states")
def get_states(crop: Optional[str] = None):
    """Get list of available states, optionally filtered by crop"""
    if crop:
        states = df[df['Commodity'] == crop]['STATE'].unique().tolist()
    else:
        states = df['STATE'].unique().tolist()
    
    states.sort()
    return {"states": states}


@app.get("/api/predict")
def predict(crop: str, state: str):
    """
    Predict next day's crop price
    
    Parameters:
    - crop: Crop name (e.g., Potato, Onion, Wheat, Tomato, Rice)
    - state: State name (e.g., Punjab, Uttar Pradesh)
    
    Returns:
    - Predicted price for next day
    """
    try:
        price = predict_next_day_price(df, crop, state)
        return {
            "success": True,
            "crop": crop,
            "state": state,
            "predicted_price": price,
            "unit": "₹ per quintal",
            "horizon": "next day"
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found for {crop} in {state}. Please train the model first."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/forecast")
def forecast(crop: str, state: str, days: int = 7):
    """
    Forecast crop prices for multiple days
    
    Parameters:
    - crop: Crop name (e.g., Potato, Onion, Wheat, Tomato, Rice)
    - state: State name (e.g., Punjab, Uttar Pradesh)
    - days: Number of days to forecast (default: 7, max: 30)
    
    Returns:
    - Daily price forecast with trend analysis
    """
    if days < 1 or days > 30:
        raise HTTPException(
            status_code=400,
            detail="Days must be between 1 and 30"
        )
    
    try:
        summary = forecast_summary(df, crop, state, days)
        summary['success'] = True
        summary['unit'] = "₹ per quintal"
        return summary
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Model not found for {crop} in {state}. Please train the model first."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
