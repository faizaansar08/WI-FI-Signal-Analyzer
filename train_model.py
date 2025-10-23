"""
Machine Learning Model Training - Member 2 Component
Trains kNN and Random Forest models to predict WiFi signal strength
Saves trained models as .pkl files using joblib
"""

import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler


class WiFiSignalPredictor:
    """Train and manage ML models for WiFi signal prediction"""
    
    def __init__(self, data_file="wifi_data_cleaned.csv"):
        self.data_file = data_file
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = None
        
        # Models
        self.knn_model = None
        self.rf_model = None
        self.best_model = None
        self.best_model_name = None
        
        # Results
        self.results = {}
    
    def load_data(self):
        """Load preprocessed data"""
        try:
            self.df = pd.read_csv(self.data_file)
            print(f"✅ Loaded {len(self.df)} records from {self.data_file}")
            return True
        except FileNotFoundError:
            print(f"❌ File not found: {self.data_file}")
            print("💡 Run data_preprocessing.py first to create cleaned data")
            return False
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def prepare_features(self, test_size=0.2, random_state=42):
        """
        Prepare features and split data
        
        Args:
            test_size: Proportion of data for testing (default: 0.2)
            random_state: Random seed for reproducibility
        """
        if self.df is None:
            print("⚠️ No data loaded. Call load_data() first.")
            return False
        
        print("\n📊 Preparing features...")
        
        # Select features: location coordinates
        feature_cols = ['location_x', 'location_y']
        target_col = 'rssi_dbm'
        
        # Check if columns exist
        if not all(col in self.df.columns for col in feature_cols):
            print(f"❌ Required feature columns not found: {feature_cols}")
            return False
        
        if target_col not in self.df.columns:
            print(f"❌ Target column not found: {target_col}")
            return False
        
        # Create feature matrix and target vector
        X = self.df[feature_cols].values
        y = self.df[target_col].values
        
        # Split data
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale features
        self.scaler = StandardScaler()
        self.X_train = self.scaler.fit_transform(self.X_train)
        self.X_test = self.scaler.transform(self.X_test)
        
        print(f"✅ Data prepared:")
        print(f"   Training set: {len(self.X_train)} samples")
        print(f"   Test set: {len(self.X_test)} samples")
        print(f"   Features: {feature_cols}")
        print(f"   Target: {target_col}")
        
        return True
    
    def train_knn_model(self, n_neighbors=5, optimize=True):
        """
        Train k-Nearest Neighbors model
        
        Args:
            n_neighbors: Number of neighbors (default: 5)
            optimize: Whether to optimize hyperparameters
        """
        print("\n🤖 Training k-Nearest Neighbors (kNN) model...")
        
        if self.X_train is None:
            print("⚠️ Data not prepared. Call prepare_features() first.")
            return None
        
        if optimize:
            print("  🔍 Optimizing hyperparameters with Grid Search...")
            
            param_grid = {
                'n_neighbors': [3, 5, 7, 9, 11],
                'weights': ['uniform', 'distance'],
                'metric': ['euclidean', 'manhattan']
            }
            
            knn = KNeighborsRegressor()
            grid_search = GridSearchCV(
                knn, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1
            )
            grid_search.fit(self.X_train, self.y_train)
            
            self.knn_model = grid_search.best_estimator_
            print(f"  ✅ Best parameters: {grid_search.best_params_}")
        else:
            self.knn_model = KNeighborsRegressor(n_neighbors=n_neighbors)
            self.knn_model.fit(self.X_train, self.y_train)
        
        # Evaluate
        train_score = self.knn_model.score(self.X_train, self.y_train)
        test_score = self.knn_model.score(self.X_test, self.y_test)
        
        y_pred = self.knn_model.predict(self.X_test)
        mse = mean_squared_error(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        rmse = np.sqrt(mse)
        
        self.results['knn'] = {
            'train_r2': train_score,
            'test_r2': test_score,
            'mse': mse,
            'rmse': rmse,
            'mae': mae
        }
        
        print(f"\n  📈 kNN Model Performance:")
        print(f"     Training R² Score:   {train_score:.4f}")
        print(f"     Test R² Score:       {test_score:.4f}")
        print(f"     RMSE:                {rmse:.4f} dBm")
        print(f"     MAE:                 {mae:.4f} dBm")
        
        return self.knn_model
    
    def train_random_forest_model(self, n_estimators=100, optimize=True):
        """
        Train Random Forest model
        
        Args:
            n_estimators: Number of trees (default: 100)
            optimize: Whether to optimize hyperparameters
        """
        print("\n🌲 Training Random Forest model...")
        
        if self.X_train is None:
            print("⚠️ Data not prepared. Call prepare_features() first.")
            return None
        
        if optimize:
            print("  🔍 Optimizing hyperparameters with Grid Search...")
            
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15, None],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            
            rf = RandomForestRegressor(random_state=42)
            grid_search = GridSearchCV(
                rf, param_grid, cv=5, scoring='neg_mean_squared_error', n_jobs=-1
            )
            grid_search.fit(self.X_train, self.y_train)
            
            self.rf_model = grid_search.best_estimator_
            print(f"  ✅ Best parameters: {grid_search.best_params_}")
        else:
            self.rf_model = RandomForestRegressor(
                n_estimators=n_estimators, 
                random_state=42
            )
            self.rf_model.fit(self.X_train, self.y_train)
        
        # Evaluate
        train_score = self.rf_model.score(self.X_train, self.y_train)
        test_score = self.rf_model.score(self.X_test, self.y_test)
        
        y_pred = self.rf_model.predict(self.X_test)
        mse = mean_squared_error(self.y_test, y_pred)
        mae = mean_absolute_error(self.y_test, y_pred)
        rmse = np.sqrt(mse)
        
        self.results['random_forest'] = {
            'train_r2': train_score,
            'test_r2': test_score,
            'mse': mse,
            'rmse': rmse,
            'mae': mae
        }
        
        print(f"\n  📈 Random Forest Model Performance:")
        print(f"     Training R² Score:   {train_score:.4f}")
        print(f"     Test R² Score:       {test_score:.4f}")
        print(f"     RMSE:                {rmse:.4f} dBm")
        print(f"     MAE:                 {mae:.4f} dBm")
        
        # Feature importance
        if hasattr(self.rf_model, 'feature_importances_'):
            print(f"\n  🎯 Feature Importances:")
            for i, importance in enumerate(self.rf_model.feature_importances_):
                feature_name = ['location_x', 'location_y'][i]
                print(f"     {feature_name}: {importance:.4f}")
        
        return self.rf_model
    
    def cross_validate_models(self, cv=5):
        """Perform cross-validation on both models"""
        print(f"\n🔄 Performing {cv}-fold cross-validation...")
        
        if self.X_train is None:
            print("⚠️ Data not prepared. Call prepare_features() first.")
            return
        
        # Combine train and test for cross-validation
        X_all = np.vstack([self.X_train, self.X_test])
        y_all = np.concatenate([self.y_train, self.y_test])
        
        if self.knn_model:
            knn_scores = cross_val_score(
                self.knn_model, X_all, y_all, cv=cv, scoring='r2'
            )
            print(f"\n  kNN Cross-Validation R² Scores:")
            print(f"    Mean: {knn_scores.mean():.4f} (+/- {knn_scores.std() * 2:.4f})")
        
        if self.rf_model:
            rf_scores = cross_val_score(
                self.rf_model, X_all, y_all, cv=cv, scoring='r2'
            )
            print(f"\n  Random Forest Cross-Validation R² Scores:")
            print(f"    Mean: {rf_scores.mean():.4f} (+/- {rf_scores.std() * 2:.4f})")
    
    def select_best_model(self):
        """Select the best performing model"""
        if not self.results:
            print("⚠️ No models trained yet.")
            return None
        
        print("\n🏆 Selecting best model...")
        
        # Compare based on test R² score
        best_score = -float('inf')
        best_name = None
        
        for model_name, metrics in self.results.items():
            if metrics['test_r2'] > best_score:
                best_score = metrics['test_r2']
                best_name = model_name
        
        if best_name == 'knn':
            self.best_model = self.knn_model
            self.best_model_name = 'k-Nearest Neighbors'
        elif best_name == 'random_forest':
            self.best_model = self.rf_model
            self.best_model_name = 'Random Forest'
        
        print(f"  ✅ Best model: {self.best_model_name}")
        print(f"     Test R² Score: {best_score:.4f}")
        
        return self.best_model
    
    def save_model(self, filename="wifi_model.pkl"):
        """Save the best model to file"""
        if self.best_model is None:
            print("⚠️ No best model selected. Call select_best_model() first.")
            return False
        
        try:
            # Save model and scaler together
            model_data = {
                'model': self.best_model,
                'scaler': self.scaler,
                'model_name': self.best_model_name,
                'metrics': self.results.get(
                    'knn' if 'knn' in self.best_model_name.lower() else 'random_forest'
                ),
                'trained_date': datetime.now().isoformat(),
                'feature_names': ['location_x', 'location_y']
            }
            
            joblib.dump(model_data, filename)
            print(f"✅ Model saved to {filename}")
            print(f"   Model type: {self.best_model_name}")
            
            return True
        except Exception as e:
            print(f"❌ Error saving model: {str(e)}")
            return False
    
    def predict(self, location_x, location_y):
        """
        Predict signal strength at a given location
        
        Args:
            location_x: X coordinate
            location_y: Y coordinate
        
        Returns:
            Predicted RSSI in dBm
        """
        if self.best_model is None:
            print("⚠️ No model available for prediction.")
            return None
        
        # Prepare input
        X_input = np.array([[location_x, location_y]])
        X_input_scaled = self.scaler.transform(X_input)
        
        # Predict
        prediction = self.best_model.predict(X_input_scaled)[0]
        
        return prediction
    
    def print_summary(self):
        """Print training summary"""
        print("\n" + "="*70)
        print("📊 MODEL TRAINING SUMMARY")
        print("="*70)
        
        if self.results:
            for model_name, metrics in self.results.items():
                print(f"\n{model_name.upper()} MODEL:")
                print(f"  Training R²: {metrics['train_r2']:.4f}")
                print(f"  Test R²:     {metrics['test_r2']:.4f}")
                print(f"  RMSE:        {metrics['rmse']:.4f} dBm")
                print(f"  MAE:         {metrics['mae']:.4f} dBm")
        
        if self.best_model_name:
            print(f"\n🏆 BEST MODEL: {self.best_model_name}")
        
        print("="*70)


def train_and_save_models(data_file="wifi_data_cleaned.csv", 
                         output_file="wifi_model.pkl",
                         optimize=True):
    """
    Complete training pipeline
    
    Args:
        data_file: Input CSV file
        output_file: Output model file
        optimize: Whether to optimize hyperparameters
    """
    print("\n" + "="*70)
    print("🤖 Wi-Fi Signal Prediction - Model Training Pipeline")
    print("="*70)
    
    # Initialize predictor
    predictor = WiFiSignalPredictor(data_file)
    
    # Load data
    if not predictor.load_data():
        return None
    
    # Prepare features
    if not predictor.prepare_features():
        return None
    
    # Train models
    predictor.train_knn_model(optimize=optimize)
    predictor.train_random_forest_model(optimize=optimize)
    
    # Cross-validate
    predictor.cross_validate_models()
    
    # Select best model
    predictor.select_best_model()
    
    # Save model
    predictor.save_model(output_file)
    
    # Print summary
    predictor.print_summary()
    
    return predictor


if __name__ == "__main__":
    # Check if cleaned data exists
    if not os.path.exists("wifi_data_cleaned.csv"):
        print("\n⚠️ wifi_data_cleaned.csv not found!")
        print("💡 Creating sample data for demonstration...")
        
        # Create sample data
        from wifi_data_collector import WiFiDataCollector
        from data_preprocessing import WiFiDataPreprocessor
        
        # Collect sample data
        collector = WiFiDataCollector("wifi_data.csv")
        sample_locations = [
            (0.0, 0.0, "Point_A"),
            (1.0, 1.0, "Point_B"),
            (2.0, 2.0, "Point_C"),
            (3.0, 3.0, "Point_D"),
            (4.0, 4.0, "Point_E")
        ]
        
        for x, y, name in sample_locations:
            collector.collect_multiple_scans(x, y, name, num_scans=2, delay=1)
        
        # Preprocess
        preprocessor = WiFiDataPreprocessor("wifi_data.csv")
        preprocessor.load_data()
        preprocessor.clean_data()
        preprocessor.save_cleaned_data("wifi_data_cleaned.csv")
    
    # Train models
    predictor = train_and_save_models(
        data_file="wifi_data_cleaned.csv",
        output_file="wifi_model.pkl",
        optimize=False  # Set to True for better models (takes longer)
    )
    
    # Test prediction
    if predictor:
        print("\n🧪 Testing prediction...")
        test_x, test_y = 2.5, 2.5
        prediction = predictor.predict(test_x, test_y)
        print(f"  Predicted signal at ({test_x}, {test_y}): {prediction:.2f} dBm")
