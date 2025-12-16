// ==========================================
// AGRICULTURAL PRICE FORECAST - JAVASCRIPT
// ==========================================

const API_BASE = window.location.origin;

let selectedCrop = null;
let currentChart = null;

// Crop icons mapping
const cropIcons = {
    'Potato': '🥔',
    'Onion': '🧅',
    'Wheat': '🌾',
    'Tomato': '🍅',
    'Rice': '🌾'
};

// ==========================================
// INITIALIZATION
// ==========================================

document.addEventListener('DOMContentLoaded', () => {
    initializeCropSelector();
    loadStates();
    attachEventListeners();
});

// ==========================================
// CROP SELECTION
// ==========================================

function initializeCropSelector() {
    const cropCards = document.querySelectorAll('.crop-card');
    
    cropCards.forEach(card => {
        card.addEventListener('click', () => {
            // Remove active class from all cards
            cropCards.forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked card
            card.classList.add('active');
            
            // Store selected crop
            selectedCrop = card.dataset.crop;
            
            // Reload states for selected crop
            loadStates(selectedCrop);
        });
    });
    
    // Select first crop by default
    if (cropCards.length > 0) {
        cropCards[0].click();
    }
}

// ==========================================
// LOAD STATES
// ==========================================

async function loadStates(crop = null) {
    const stateSelect = document.getElementById('state');
    stateSelect.innerHTML = '<option value="">Loading states...</option>';
    
    try {
        const url = crop 
            ? `${API_BASE}/api/states?crop=${encodeURIComponent(crop)}`
            : `${API_BASE}/api/states`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        stateSelect.innerHTML = '<option value="">Select a state</option>';
        
        data.states.forEach(state => {
            const option = document.createElement('option');
            option.value = state;
            option.textContent = state;
            stateSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading states:', error);
        stateSelect.innerHTML = '<option value="">Error loading states</option>';
        showError('Failed to load states. Please refresh the page.');
    }
}

// ==========================================
// EVENT LISTENERS
// ==========================================

function attachEventListeners() {
    document.getElementById('predictBtn').addEventListener('click', handlePredict);
    document.getElementById('resetBtn').addEventListener('click', handleReset);
}

// ==========================================
// HANDLE PREDICTION
// ==========================================

async function handlePredict() {
    const state = document.getElementById('state').value;
    const days = parseInt(document.getElementById('days').value);
    
    // Validation
    if (!selectedCrop) {
        showError('Please select a crop');
        return;
    }
    
    if (!state) {
        showError('Please select a state');
        return;
    }
    
    // Show loading
    showLoading();
    hideError();
    hideResults();
    
    try {
        if (days === 1) {
            await fetchPrediction(selectedCrop, state);
        } else {
            await fetchForecast(selectedCrop, state, days);
        }
    } catch (error) {
        console.error('Prediction error:', error);
        showError(error.message || 'An error occurred while fetching the forecast');
    } finally {
        hideLoading();
    }
}

// ==========================================
// FETCH NEXT DAY PREDICTION
// ==========================================

async function fetchPrediction(crop, state) {
    const url = `${API_BASE}/api/predict?crop=${encodeURIComponent(crop)}&state=${encodeURIComponent(state)}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch prediction');
    }
    
    const data = await response.json();
    
    // Display single day prediction
    displaySingleDayResult(data);
}

// ==========================================
// FETCH MULTI-DAY FORECAST
// ==========================================

async function fetchForecast(crop, state, days) {
    const url = `${API_BASE}/api/forecast?crop=${encodeURIComponent(crop)}&state=${encodeURIComponent(state)}&days=${days}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch forecast');
    }
    
    const data = await response.json();
    
    // Display forecast results
    displayForecastResult(data);
}

// ==========================================
// DISPLAY SINGLE DAY RESULT
// ==========================================

function displaySingleDayResult(data) {
    const resultSection = document.getElementById('resultsSection');
    
    // Update crop and state
    document.getElementById('resultCropIcon').textContent = cropIcons[data.crop];
    document.getElementById('resultCrop').textContent = data.crop;
    document.getElementById('resultState').textContent = data.state;
    
    // Update prices (for single day, we show current as 0 and predicted)
    document.getElementById('startPrice').textContent = '-';
    document.getElementById('endPrice').textContent = data.predicted_price.toFixed(2);
    
    // Update trend
    document.getElementById('trendIcon').textContent = '🔮';
    document.getElementById('trendText').textContent = 'Next Day';
    document.getElementById('trendBadge').className = 'trend-badge';
    
    // Update change
    document.getElementById('changePercent').textContent = 'N/A';
    document.getElementById('changeAmount').textContent = `₹${data.predicted_price.toFixed(2)}`;
    
    // Hide chart for single prediction
    document.querySelector('.chart-card').style.display = 'none';
    
    // Create simple table
    const tableBody = document.getElementById('forecastTableBody');
    tableBody.innerHTML = `
        <tr>
            <td>Next Day</td>
            <td>₹${data.predicted_price.toFixed(2)}</td>
            <td>-</td>
        </tr>
    `;
    
    // Show results
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// ==========================================
// DISPLAY FORECAST RESULT
// ==========================================

function displayForecastResult(data) {
    const resultSection = document.getElementById('resultsSection');
    
    // Update crop and state
    document.getElementById('resultCropIcon').textContent = cropIcons[data.crop];
    document.getElementById('resultCrop').textContent = data.crop;
    document.getElementById('resultState').textContent = data.state;
    
    // Update prices
    document.getElementById('startPrice').textContent = data.start_price.toFixed(2);
    document.getElementById('endPrice').textContent = data.end_price.toFixed(2);
    
    // Update trend
    const trendBadge = document.getElementById('trendBadge');
    document.getElementById('trendIcon').textContent = data.trend_emoji;
    document.getElementById('trendText').textContent = data.trend;
    
    // Set trend class
    trendBadge.className = 'trend-badge';
    if (data.percent_change > 0) {
        trendBadge.classList.add('positive');
    } else if (data.percent_change < 0) {
        trendBadge.classList.add('negative');
    } else {
        trendBadge.classList.add('stable');
    }
    
    // Update change
    const changeAmount = data.end_price - data.start_price;
    document.getElementById('changePercent').textContent = `${data.percent_change > 0 ? '+' : ''}${data.percent_change.toFixed(2)}%`;
    document.getElementById('changeAmount').textContent = `${changeAmount > 0 ? '+' : ''}₹${changeAmount.toFixed(2)}`;
    
    // Show chart
    document.querySelector('.chart-card').style.display = 'block';
    
    // Create chart
    createChart(data.daily_forecast);
    
    // Create table
    createTable(data.daily_forecast);
    
    // Show results
    resultSection.style.display = 'block';
    resultSection.scrollIntoView({ behavior: 'smooth' });
}

// ==========================================
// CREATE CHART
// ==========================================

function createChart(forecast) {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Destroy existing chart
    if (currentChart) {
        currentChart.destroy();
    }
    
    const dates = forecast.map(f => {
        const date = new Date(f.date);
        return date.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' });
    });
    
    const prices = forecast.map(f => f.price);
    
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Predicted Price (₹)',
                data: prices,
                borderColor: '#a8e063',
                backgroundColor: 'rgba(168, 224, 99, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointBackgroundColor: '#a8e063',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 7
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#a8e063',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#a8e063',
                    bodyColor: '#fff',
                    borderColor: '#a8e063',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: (context) => `₹${context.parsed.y.toFixed(2)} per quintal`
                    }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#a0a0a0' },
                    grid: { color: '#404040' }
                },
                y: {
                    ticks: { 
                        color: '#a0a0a0',
                        callback: (value) => `₹${value}`
                    },
                    grid: { color: '#404040' }
                }
            }
        }
    });
}

// ==========================================
// CREATE TABLE
// ==========================================

function createTable(forecast) {
    const tableBody = document.getElementById('forecastTableBody');
    tableBody.innerHTML = '';
    
    forecast.forEach((item, index) => {
        const row = document.createElement('tr');
        
        const date = new Date(item.date);
        const formattedDate = date.toLocaleDateString('en-IN', { 
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
        
        let change = '-';
        if (index > 0) {
            const diff = item.price - forecast[index - 1].price;
            const percent = ((diff / forecast[index - 1].price) * 100).toFixed(2);
            const sign = diff > 0 ? '+' : '';
            change = `<span style="color: ${diff > 0 ? '#a8e063' : '#ff4444'}">${sign}${diff.toFixed(2)} (${sign}${percent}%)</span>`;
        }
        
        row.innerHTML = `
            <td>${formattedDate}</td>
            <td><strong>₹${item.price.toFixed(2)}</strong></td>
            <td>${change}</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// ==========================================
// RESET
// ==========================================

function handleReset() {
    // Reset selections
    document.querySelectorAll('.crop-card').forEach(card => {
        card.classList.remove('active');
    });
    
    document.getElementById('state').value = '';
    document.getElementById('days').value = '7';
    
    selectedCrop = null;
    
    // Hide results
    hideResults();
    hideError();
    
    // Reinitialize
    initializeCropSelector();
}

// ==========================================
// UI HELPERS
// ==========================================

function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    document.getElementById('errorText').textContent = message;
    errorDiv.style.display = 'flex';
}

function hideError() {
    document.getElementById('errorMessage').style.display = 'none';
}

function hideResults() {
    document.getElementById('resultsSection').style.display = 'none';
}
