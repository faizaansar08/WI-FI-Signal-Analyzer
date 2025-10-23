# Machine Learning Components - Member 2 Documentation

## Overview
Complete machine learning pipeline for WiFi signal strength prediction based on location coordinates.

---

## 📁 Files Created

### 1. **wifi_data_collector.py**
**Purpose**: Collect WiFi signal strength data with location coordinates

**Key Features**:
- Scans WiFi networks using cross-platform scanner
- Records RSSI (signal strength) at specific (x, y) coordinates
- Supports multiple scans per location for accuracy
- Saves data to CSV format
- Interactive and automated collection modes

**Main Functions**:
```python
collector = WiFiDataCollector("wifi_data.csv")

# Single location
collector.collect_data_point(x=0.0, y=0.0, location_name="Room_A")

# Multiple scans at same location
collector.collect_multiple_scans(x=0.0, y=0.0, location_name="Room_A", num_scans=3)

# Grid survey
collector.collect_grid_survey(grid_size=(5, 5), spacing=1.0, num_scans=3)

# Custom locations
locations = [(0.0, 0.0, "Point_A"), (3.0, 3.0, "Point_B")]
collector.collect_custom_locations(locations, num_scans=3)
```

**Output**: `wifi_data.csv` with columns:
- timestamp, location_x, location_y, location_name
- ssid, bssid, rssi_dbm, signal_quality
- frequency, channel, security, scan_number

---

### 2. **data_preprocessing.py**
**Purpose**: Clean and preprocess WiFi data for machine learning

**Key Features**:
- Loads data from CSV using Pandas
- Handles missing values (median imputation)
- Removes duplicates and outliers
- Normalizes features (0-1 scaling)
- Creates additional engineered features
- Aggregates multiple scans

**Main Functions**:
```python
preprocessor = WiFiDataPreprocessor("wifi_data.csv")

# Load and inspect
preprocessor.load_data()
preprocessor.inspect_data()

# Clean data
df_cleaned = preprocessor.clean_data()

# Normalize
df_normalized = preprocessor.normalize_features()

# Aggregate by location
df_aggregated = preprocessor.aggregate_by_location()

# Save cleaned data
preprocessor.save_cleaned_data("wifi_data_cleaned.csv")

# Prepare for ML
X, y = preprocessor.get_ml_ready_data()
```

**Data Cleaning Steps**:
1. Fill missing RSSI with median
2. Remove duplicates
3. Filter outliers (-100 to -20 dBm)
4. Ensure signal quality in 0-100 range
5. Convert data types
6. Create derived features

---

### 3. **train_model.py**
**Purpose**: Train machine learning models to predict signal strength

**Key Features**:
- Trains k-Nearest Neighbors (kNN) model
- Trains Random Forest model
- Hyperparameter optimization with Grid Search
- Cross-validation for reliability
- Model comparison and selection
- Saves best model to .pkl file

**Main Functions**:
```python
predictor = WiFiSignalPredictor("wifi_data_cleaned.csv")

# Load and prepare
predictor.load_data()
predictor.prepare_features(test_size=0.2)

# Train models
predictor.train_knn_model(optimize=True)
predictor.train_random_forest_model(optimize=True)

# Cross-validate
predictor.cross_validate_models(cv=5)

# Select and save best
predictor.select_best_model()
predictor.save_model("wifi_model.pkl")

# Make predictions
prediction = predictor.predict(location_x=2.5, location_y=3.0)
```

**Models Implemented**:

**kNN (k-Nearest Neighbors)**:
- Hyperparameters: n_neighbors, weights, metric
- Good for: Non-linear patterns
- Fast prediction

**Random Forest**:
- Hyperparameters: n_estimators, max_depth, min_samples_split
- Good for: Complex relationships
- Feature importance analysis

**Output**: `wifi_model.pkl` containing:
- Trained model
- Feature scaler
- Model name and metrics
- Training date

---

### 4. **model_evaluation.py**
**Purpose**: Evaluate model performance and create visualizations

**Key Features**:
- Calculates performance metrics (R², RMSE, MAE)
- Generates 6 types of plots for report
- Creates evaluation summary report
- Professional publication-quality graphs

**Main Functions**:
```python
evaluator = ModelEvaluator("wifi_model.pkl", "wifi_data_cleaned.csv")

# Load and evaluate
evaluator.load_model()
evaluator.load_data()
metrics, y_actual, y_pred = evaluator.evaluate_model()

# Generate all plots
evaluator.generate_all_plots()

# Create report
evaluator.create_report_summary()
```

**Generated Plots**:
1. **actual_vs_predicted.png** - Scatter plot with R² score
2. **residuals.png** - Residual analysis (2 subplots)
3. **signal_vs_location.png** - Signal vs X and Y coordinates
4. **signal_heatmap.png** - 2D heatmap with contours
5. **signal_3d_surface.png** - 3D surface plot
6. **network_comparison.png** - Box plot across networks

**Performance Metrics**:
- R² Score (coefficient of determination)
- MSE (Mean Squared Error)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- MAPE (Mean Absolute Percentage Error)

---

### 5. **ml_workflow.py**
**Purpose**: Complete automated pipeline

**Workflow Steps**:
1. Data Collection → wifi_data.csv
2. Preprocessing → wifi_data_cleaned.csv
3. Model Training → wifi_model.pkl
4. Evaluation → plots/ + report

**Usage**:
```bash
python ml_workflow.py
```

---

## 🚀 Quick Start Guide

### Option 1: Complete Automated Workflow
```bash
# Run the complete pipeline
python ml_workflow.py

# Select:
# 1 = Quick demo (5 locations, fast)
# 2 = Full workflow (custom settings)
```

### Option 2: Step-by-Step Manual

**Step 1: Collect Data**
```bash
python wifi_data_collector.py
```
Output: `wifi_data.csv`

**Step 2: Preprocess Data**
```bash
python data_preprocessing.py
```
Output: `wifi_data_cleaned.csv`

**Step 3: Train Model**
```bash
python train_model.py
```
Output: `wifi_model.pkl`

**Step 4: Evaluate Model**
```bash
python model_evaluation.py
```
Output: `plots/` directory with visualizations

---

## 📊 Integration with Flask App

The ML model is automatically integrated with the main Flask application (`app.py`).

### API Endpoint: `/api/predict`

**With ML Model (Location-based prediction)**:
```bash
# PowerShell
$body = @{location_x=2.5; location_y=3.0} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/predict" -Method Post -Body $body -ContentType "application/json"
```

Response:
```json
{
  "success": true,
  "prediction": {
    "location_x": 2.5,
    "location_y": 3.0,
    "predicted_rssi": -58.34,
    "signal_quality": 62,
    "status": "Good",
    "model_used": "Random Forest"
  },
  "ml_powered": true
}
```

**Without ML Model (Signal-based)**:
```bash
$body = @{ssid="MyNetwork"; signal_strength=-55} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/predict" -Method Post -Body $body -ContentType "application/json"
```

---

## 📈 Model Performance Expectations

### Typical Results:

**Good Performance**:
- R² Score: 0.70 - 0.95
- RMSE: 3-7 dBm
- MAE: 2-5 dBm

**Factors Affecting Performance**:
- Number of data points (more is better)
- Spatial coverage of measurements
- Number of scans per location
- Environmental consistency
- Network stability

### Improving Model Performance:

1. **Collect More Data**:
   - Increase number of locations
   - More scans per location (3-5 recommended)
   - Cover entire area uniformly

2. **Enable Hyperparameter Optimization**:
   ```python
   predictor.train_random_forest_model(optimize=True)
   ```

3. **Add More Features**:
   - Time of day
   - Device orientation
   - Building materials
   - Interference sources

---

## 🎯 Use Cases

### 1. Network Planning
- Predict signal coverage before installing router
- Optimize router placement
- Identify dead zones

### 2. Troubleshooting
- Diagnose weak signal areas
- Compare actual vs expected signal
- Validate network improvements

### 3. Research & Education
- Study signal propagation patterns
- Learn machine learning concepts
- Demonstrate regression techniques

### 4. Heatmap Generation
- Create coverage maps
- Visualize signal distribution
- Plan network expansions

---

## 📝 Report Components

For academic/professional reports, you have:

### Deliverables Checklist:
- [x] wifi_data.csv - Raw data
- [x] train_model.py - Training code
- [x] wifi_model.pkl - Trained model
- [x] Graphs/plots (6 types) in plots/
- [x] Evaluation report (text summary)
- [x] Documentation (this file)

### Sections for Report:

**1. Data Collection**
- Methodology (netsh/pywifi)
- Sample locations and coordinates
- Number of scans performed
- Data format and structure

**2. Data Preprocessing**
- Cleaning steps (missing values, outliers)
- Normalization techniques
- Feature engineering
- Statistics summary

**3. Model Development**
- Algorithms used (kNN, Random Forest)
- Hyperparameters optimized
- Training/test split (80/20)
- Cross-validation approach

**4. Evaluation**
- Performance metrics
- Comparison of models
- Actual vs predicted analysis
- Residual analysis

**5. Visualizations**
- Heatmaps
- 3D surface plots
- Scatter plots
- Network comparisons

**6. Results & Discussion**
- Model accuracy
- Prediction errors
- Limitations
- Future improvements

---

## 🔧 Troubleshooting

### Issue: Not Enough Data
**Solution**: 
```python
# Run ml_workflow.py and select more locations
# Or manually collect more data:
collector.collect_grid_survey(grid_size=(10, 10), num_scans=3)
```

### Issue: Low Model Accuracy
**Solutions**:
1. Collect more diverse locations
2. Enable hyperparameter optimization
3. Increase scans per location
4. Check data quality (inspect_data())

### Issue: Plots Not Generating
**Solution**:
```bash
pip install matplotlib seaborn
# Make sure plots/ directory is writable
```

### Issue: Model Not Loading in Flask
**Solution**:
```bash
# Make sure wifi_model.pkl exists
ls wifi_model.pkl

# Retrain if needed
python train_model.py
```

---

## 🎓 Academic Notes

### Machine Learning Concepts Demonstrated:

1. **Supervised Learning**: Predicting continuous values (regression)
2. **Feature Engineering**: Creating location-based features
3. **Model Selection**: Comparing multiple algorithms
4. **Cross-Validation**: K-fold validation for reliability
5. **Hyperparameter Tuning**: Grid search optimization
6. **Model Evaluation**: Multiple metrics (R², RMSE, MAE)
7. **Visualization**: Professional scientific plots

### Scikit-learn Functions Used:
- `train_test_split()` - Data splitting
- `KNeighborsRegressor()` - kNN algorithm
- `RandomForestRegressor()` - Random Forest
- `GridSearchCV()` - Hyperparameter search
- `cross_val_score()` - Cross-validation
- `StandardScaler()` - Feature scaling
- Performance metrics from `sklearn.metrics`

---

## 📚 References

- Scikit-learn Documentation: https://scikit-learn.org/
- Pandas Documentation: https://pandas.pydata.org/
- Matplotlib Gallery: https://matplotlib.org/stable/gallery/
- WiFi Signal Propagation: IEEE 802.11 standards

---

## ✅ Verification Checklist

Before submitting your project:

- [ ] wifi_data.csv exists and has data
- [ ] wifi_data_cleaned.csv created
- [ ] wifi_model.pkl trained and saved
- [ ] All 6 plots generated in plots/
- [ ] Evaluation report created
- [ ] Model R² score > 0.5
- [ ] Flask API integration tested
- [ ] Documentation reviewed

---

## 🎉 Success!

You now have a complete machine learning pipeline for WiFi signal prediction!

**Next Steps**:
1. Run `python ml_workflow.py` to generate all components
2. Review plots in `plots/` directory
3. Test predictions via Flask API
4. Include results in your project report

**For Questions**:
- Check error messages in console
- Review this documentation
- Inspect generated files
- Test each component individually

---

*Last Updated: October 22, 2025*
*Member 2 - Data Collection, Analysis & Machine Learning Component*
