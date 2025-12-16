# Agri Price Forecast 🌾

AI-Powered Agricultural Market Intelligence Platform for predicting crop prices in Indian markets.

**Developer**: Suraj Singh  
**Email**: surajsingh@gmail.com

---

## 🚀 Live Demo

**Access the live application**: [https://agri-price-forecast.onrender.com](https://agri-price-forecast.onrender.com)

---

## 🎯 Features

- 🔮 **Next-Day Price Prediction** - Get accurate price predictions for the next day
- 📈 **Multi-Day Forecasting** - Forecast prices up to 30 days ahead
- 📊 **Visual Analytics** - Interactive charts and trend analysis
- 🌾 **Multiple Crops** - Support for Potato, Onion, Wheat, Tomato, and Rice
- 🗺️ **State-wise Data** - Predictions for 20+ Indian states
- 🎨 **Modern UI** - Beautiful dark-themed responsive interface

## 📸 Screenshots

The application features:
- Interactive crop selection cards
- State dropdown with dynamic filtering
- Real-time price forecasting
- Beautiful chart visualizations with Chart.js
- Trend indicators with emoji icons
- Responsive design for all devices

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **scikit-learn** - Machine learning models (Random Forest Regressor)
- **pandas** - Data processing and manipulation
- **NumPy** - Numerical computations
- **joblib** - Model serialization

### Frontend
- **HTML5/CSS3** - Modern UI with dark theme
- **Vanilla JavaScript** - No framework dependencies for better performance
- **Chart.js** - Interactive price visualization and trend charts

### Machine Learning
- **Algorithm**: Random Forest Regressor
- **Features**: 
  - Temporal features (day, month, day of week, week of year)
  - Lag features (1, 7, 14, 30 days)
  - Moving averages (7, 14, 30 days)
  - Rolling statistics (7-day standard deviation)
- **Training**: 297,181+ data points from Indian agricultural markets
- **Model Performance**: Optimized with 500 estimators, depth 15

## 📁 Project Structure

```
crop-price-prediction/
│
├── app.py                          # FastAPI application entry point
├── requirements.txt                # Python dependencies
├── Procfile                        # Render deployment configuration
├── render.yaml                     # Render service blueprint
├── croppriceprediction.ipynb       # Model training notebook
│
├── models/                         # Trained ML models (92 files)
│   ├── Potato_Punjab.pkl
│   ├── Onion_Maharashtra.pkl
│   ├── Rice_West_Bengal.pkl
│   └── ... (all crop-state combinations)
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   └── predict.py                  # Prediction and forecasting logic
│
├── static/                         # Frontend assets
│   ├── index.html                  # Main UI
│   ├── style.css                   # Styling with dark theme
│   └── script.js                   # Frontend logic and API calls
│
└── data/                           # Dataset
    └── Agriculture_price_dataset.csv (297,181 records)
```

## 💻 Installation & Local Development

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd crop-price-prediction
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify data files**
   - Ensure `data/Agriculture_price_dataset.csv` exists
   - Ensure `models/` folder contains `.pkl` model files

4. **Run the application**
```bash
python app.py
```
   The server will start on `http://0.0.0.0:8000`

5. **Access the application**
   - **Web Interface**: `http://localhost:8000`
   - **API Documentation**: `http://localhost:8000/docs`
   - **API Status**: `http://localhost:8000/api`

## 🌐 API Documentation

## 🌐 API Documentation

### Base URL
- Local: `http://localhost:8000`
- Production: `https://agri-price-forecast.onrender.com`

### Endpoints

#### 1. **Get Available Crops**
```http
GET /api/crops
```

**Response:**
```json
{
  "crops": ["Potato", "Onion", "Wheat", "Tomato", "Rice"]
}
```

---

#### 2. **Get Available States**
```http
GET /api/states
GET /api/states?crop=Potato
```

**Parameters:**
- `crop` (optional): Filter states by crop availability

**Response:**
```json
{
  "states": ["Andhra Pradesh", "Assam", "Bihar", "Chandigarh", ...]
}
```

---

#### 3. **Predict Next Day Price**
```http
GET /api/predict?crop=Potato&state=Punjab
```

**Parameters:**
- `crop` (required): Crop name (Potato, Onion, Wheat, Tomato, Rice)
- `state` (required): State name

**Response:**
```json
{
  "success": true,
  "crop": "Potato",
  "state": "Punjab",
  "predicted_price": 1245.67,
  "unit": "₹ per quintal",
  "horizon": "next day"
}
```

---

#### 4. **Forecast Multiple Days**
```http
GET /api/forecast?crop=Potato&state=Punjab&days=7
```

**Parameters:**
- `crop` (required): Crop name
- `state` (required): State name
- `days` (optional): Number of days to forecast (1-30, default: 7)

**Response:**
```json
{
  "success": true,
  "crop": "Potato",
  "state": "Punjab",
  "days": 7,
  "start_price": 1200.00,
  "end_price": 1280.50,
  "percent_change": 6.71,
  "trend": "Upward",
  "trend_emoji": "📈",
  "unit": "₹ per quintal",
  "daily_forecast": [
    {"date": "2025-12-17", "price": 1205.32},
    {"date": "2025-12-18", "price": 1215.67},
    {"date": "2025-12-19", "price": 1225.10},
    ...
  ]
}
```

---

## 🤖 Machine Learning Pipeline

### Data Processing
1. **Data Loading**: 297,181 records from Indian agricultural markets
2. **Preprocessing**:
   - Date parsing with error handling
   - State name normalization (fixing variations)
   - Missing value interpolation
   - Price outlier detection and handling

### Feature Engineering
The model uses 12 features for prediction:

**Temporal Features:**
- `day`: Day of month (1-31)
- `month`: Month of year (1-12)
- `dayofweek`: Day of week (0-6)
- `weekofyear`: Week number (1-52)

**Lag Features:**
- `lag_1`: Price 1 day ago
- `lag_7`: Price 7 days ago
- `lag_14`: Price 14 days ago
- `lag_30`: Price 30 days ago

**Rolling Statistics:**
- `ma_7`: 7-day moving average
- `ma_14`: 14-day moving average
- `ma_30`: 30-day moving average
- `std_7`: 7-day standard deviation

### Model Architecture
- **Algorithm**: Random Forest Regressor
- **Parameters**:
  - n_estimators: 500 trees
  - max_depth: 15
  - min_samples_leaf: 5
  - n_jobs: -1 (parallel processing)
  - random_state: 42
- **Training**: 80/20 train-test split
- **Models**: 92 separate models (one per crop-state combination)

### Model Performance
- Evaluated using MAE (Mean Absolute Error) and RMSE
- Quality filters applied per crop type
- Minimum data requirements enforced for reliable predictions

### Training New Models
To retrain models with updated data:

1. Open `croppriceprediction.ipynb` in Jupyter
2. Update the dataset in `data/Agriculture_price_dataset.csv`
3. Run all cells sequentially
4. Models will be saved to `models/` folder
5. Restart the FastAPI application

---

## 🎨 UI Design

### Color Scheme
Modern dark theme with agricultural accent colors:

- **Background**: Deep Black (#0a0a0a) & Dark Gray (#1a1a1a)
- **Cards**: Charcoal (#2d2d2d)
- **Primary Accent**: Lime Green (#a8e063)
- **Secondary Accent**: Forest Green (#56ab2f)
- **Highlights**: Vibrant Orange (#ff6b35)
- **Success**: Green (#4caf50)
- **Warning**: Yellow (#ffc107)
- **Error**: Red (#ff4444)

### Features
- Responsive grid layout
- Smooth animations and transitions
- Interactive hover effects
- Loading states with spinners
- Error handling with user-friendly messages
- Chart tooltips and legends
- Mobile-optimized interface

---

## 📊 Dataset Information

- **Source**: Indian Agricultural Market Data
- **Size**: 297,181 records
- **Date Range**: Historical market prices (2020-2024)
- **Crops**: Potato, Onion, Wheat, Tomato, Rice
- **States**: 20+ Indian states
- **Columns**:
  - STATE: State name
  - District Name: District
  - Market Name: Market/Mandi name
  - Commodity: Crop name
  - Variety: Crop variety
  - Grade: Quality grade
  - Min_Price: Minimum price (₹/quintal)
  - Max_Price: Maximum price (₹/quintal)
  - Modal_Price: Most common price (₹/quintal)
  - Price Date: Date of price record

---

## 🔧 Troubleshooting

### Common Issues

**Issue**: Models not loading
- **Solution**: Ensure all `.pkl` files are in the `models/` folder and not corrupted

**Issue**: No data found for crop/state
- **Solution**: Check if the combination exists in the dataset and a model was trained

**Issue**: Server not starting
- **Solution**: Verify all dependencies are installed: `pip install -r requirements.txt`

**Issue**: Slow predictions
- **Solution**: Normal for first request after server restart (model loading)

**Issue**: Port already in use
- **Solution**: Kill process on port 8000 or change port in `app.py`

---

## 📈 Future Enhancements

- [ ] Integration with weather data for improved accuracy
- [ ] Real-time market news and alerts
- [ ] Price comparison across markets
- [ ] Historical price charts and trends
- [ ] SMS/Email notifications for price alerts
- [ ] Mobile application (Android/iOS)
- [ ] Support for more crops and states
- [ ] User authentication and personalized dashboards
- [ ] LLM integration for natural language queries
- [ ] Export reports in PDF/Excel format

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Contact & Support

**Developer**: Suraj Singh  
**Email**: surajsingh@gmail.com

For questions, bug reports, or feature requests:
- Open an issue on GitHub
- Send an email to surajsingh@gmail.com

---

**Made with ❤️ for Indian Farmers**

*Empowering farmers with AI-driven market intelligence*
