"""
Data Preprocessing Module - Member 2 Component
Uses Pandas to clean, normalize, and format WiFi signal data
Handles missing values and inconsistent signals
"""

import pandas as pd
import numpy as np
from datetime import datetime


class WiFiDataPreprocessor:
    """Preprocesses WiFi signal data for machine learning"""
    
    def __init__(self, input_file="wifi_data.csv"):
        self.input_file = input_file
        self.df = None
        self.df_cleaned = None
    
    def load_data(self):
        """Load data from CSV file"""
        try:
            self.df = pd.read_csv(self.input_file)
            print(f"✅ Loaded {len(self.df)} records from {self.input_file}")
            return self.df
        except FileNotFoundError:
            print(f"❌ File not found: {self.input_file}")
            return None
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return None
    
    def inspect_data(self):
        """Display data information"""
        if self.df is None:
            print("⚠️ No data loaded. Call load_data() first.")
            return
        
        print("\n" + "="*70)
        print("📊 DATA INSPECTION")
        print("="*70)
        
        print(f"\n🔢 Dataset Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        
        print("\n📋 Column Names:")
        for i, col in enumerate(self.df.columns, 1):
            print(f"  {i}. {col}")
        
        print("\n📈 Data Types:")
        print(self.df.dtypes)
        
        print("\n🔍 First 5 Records:")
        print(self.df.head())
        
        print("\n📊 Statistical Summary:")
        print(self.df.describe())
        
        print("\n❓ Missing Values:")
        missing = self.df.isnull().sum()
        if missing.sum() == 0:
            print("  ✅ No missing values found!")
        else:
            print(missing[missing > 0])
        
        print("\n🌐 Unique Networks (SSIDs):")
        if 'ssid' in self.df.columns:
            print(f"  Total unique SSIDs: {self.df['ssid'].nunique()}")
            print("  Top 5 networks:")
            print(self.df['ssid'].value_counts().head())
        
        print("\n📍 Unique Locations:")
        if 'location_x' in self.df.columns and 'location_y' in self.df.columns:
            unique_locations = self.df.groupby(['location_x', 'location_y']).size()
            print(f"  Total unique locations: {len(unique_locations)}")
        
        print("="*70)
    
    def clean_data(self):
        """Clean and preprocess the data"""
        if self.df is None:
            print("⚠️ No data loaded. Call load_data() first.")
            return None
        
        print("\n🧹 Cleaning data...")
        
        # Create a copy for cleaning
        df_clean = self.df.copy()
        
        # 1. Handle missing values
        print("  ✓ Handling missing values...")
        
        # Fill missing RSSI with median
        if 'rssi_dbm' in df_clean.columns:
            median_rssi = df_clean['rssi_dbm'].median()
            df_clean['rssi_dbm'].fillna(median_rssi, inplace=True)
        
        # Fill missing signal quality with calculated value
        if 'signal_quality' in df_clean.columns:
            df_clean['signal_quality'].fillna(
                df_clean['signal_quality'].median(), 
                inplace=True
            )
        
        # Fill missing string fields
        string_cols = ['ssid', 'bssid', 'security', 'location_name']
        for col in string_cols:
            if col in df_clean.columns:
                df_clean[col].fillna('Unknown', inplace=True)
        
        # Fill missing numeric fields
        if 'channel' in df_clean.columns:
            df_clean['channel'].fillna(0, inplace=True)
        
        # 2. Remove duplicates
        print("  ✓ Removing duplicates...")
        before_count = len(df_clean)
        df_clean.drop_duplicates(inplace=True)
        after_count = len(df_clean)
        if before_count > after_count:
            print(f"    Removed {before_count - after_count} duplicate rows")
        
        # 3. Handle outliers in RSSI (signal strength)
        print("  ✓ Handling outliers...")
        if 'rssi_dbm' in df_clean.columns:
            # Valid RSSI range: -100 to -20 dBm
            before_outliers = len(df_clean)
            df_clean = df_clean[
                (df_clean['rssi_dbm'] >= -100) & 
                (df_clean['rssi_dbm'] <= -20)
            ]
            after_outliers = len(df_clean)
            if before_outliers > after_outliers:
                print(f"    Removed {before_outliers - after_outliers} outlier rows")
        
        # 4. Ensure signal quality is in valid range (0-100)
        if 'signal_quality' in df_clean.columns:
            df_clean['signal_quality'] = df_clean['signal_quality'].clip(0, 100)
        
        # 5. Convert data types
        print("  ✓ Converting data types...")
        
        # Ensure numeric columns are numeric
        numeric_cols = ['location_x', 'location_y', 'rssi_dbm', 'signal_quality', 'scan_number']
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # 6. Create additional features
        print("  ✓ Creating additional features...")
        
        # Distance from origin (0,0)
        if 'location_x' in df_clean.columns and 'location_y' in df_clean.columns:
            df_clean['distance_from_origin'] = np.sqrt(
                df_clean['location_x']**2 + df_clean['location_y']**2
            )
        
        # Signal category (Excellent, Good, Fair, Poor)
        if 'signal_quality' in df_clean.columns:
            df_clean['signal_category'] = pd.cut(
                df_clean['signal_quality'],
                bins=[0, 40, 60, 80, 100],
                labels=['Poor', 'Fair', 'Good', 'Excellent']
            )
        
        # Frequency band (2.4 GHz or 5 GHz)
        if 'frequency' in df_clean.columns:
            df_clean['frequency_band'] = df_clean['frequency'].apply(
                lambda x: '5GHz' if '5 GHz' in str(x) else '2.4GHz' if '2.4 GHz' in str(x) else 'Unknown'
            )
        
        self.df_cleaned = df_clean
        
        print(f"✅ Cleaning complete! {len(df_clean)} records ready for analysis")
        return df_clean
    
    def normalize_features(self):
        """Normalize numerical features"""
        if self.df_cleaned is None:
            print("⚠️ No cleaned data available. Call clean_data() first.")
            return None
        
        print("\n📊 Normalizing features...")
        
        df_norm = self.df_cleaned.copy()
        
        # Normalize RSSI to 0-1 range
        if 'rssi_dbm' in df_norm.columns:
            rssi_min = df_norm['rssi_dbm'].min()
            rssi_max = df_norm['rssi_dbm'].max()
            df_norm['rssi_normalized'] = (df_norm['rssi_dbm'] - rssi_min) / (rssi_max - rssi_min)
        
        # Normalize signal quality (already 0-100, convert to 0-1)
        if 'signal_quality' in df_norm.columns:
            df_norm['signal_quality_normalized'] = df_norm['signal_quality'] / 100.0
        
        # Normalize location coordinates
        if 'location_x' in df_norm.columns:
            x_min, x_max = df_norm['location_x'].min(), df_norm['location_x'].max()
            if x_max > x_min:
                df_norm['location_x_normalized'] = (df_norm['location_x'] - x_min) / (x_max - x_min)
        
        if 'location_y' in df_norm.columns:
            y_min, y_max = df_norm['location_y'].min(), df_norm['location_y'].max()
            if y_max > y_min:
                df_norm['location_y_normalized'] = (df_norm['location_y'] - y_min) / (y_max - y_min)
        
        print("✅ Normalization complete!")
        return df_norm
    
    def aggregate_by_location(self):
        """Aggregate multiple scans at same location"""
        if self.df_cleaned is None:
            print("⚠️ No cleaned data available. Call clean_data() first.")
            return None
        
        print("\n📍 Aggregating data by location...")
        
        # Group by location and SSID, calculate statistics
        agg_dict = {
            'rssi_dbm': ['mean', 'std', 'min', 'max', 'count'],
            'signal_quality': ['mean', 'std'],
            'scan_number': 'max'
        }
        
        df_agg = self.df_cleaned.groupby(
            ['location_x', 'location_y', 'location_name', 'ssid']
        ).agg(agg_dict).reset_index()
        
        # Flatten column names
        df_agg.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                          for col in df_agg.columns.values]
        
        print(f"✅ Aggregated to {len(df_agg)} unique location-network combinations")
        return df_agg
    
    def save_cleaned_data(self, output_file="wifi_data_cleaned.csv"):
        """Save cleaned data to CSV"""
        if self.df_cleaned is None:
            print("⚠️ No cleaned data to save. Call clean_data() first.")
            return
        
        self.df_cleaned.to_csv(output_file, index=False)
        print(f"✅ Saved cleaned data to {output_file}")
    
    def get_ml_ready_data(self):
        """
        Prepare data specifically for machine learning
        Returns features (X) and target (y)
        """
        if self.df_cleaned is None:
            print("⚠️ No cleaned data available. Call clean_data() first.")
            return None, None
        
        print("\n🤖 Preparing data for machine learning...")
        
        # Select features for ML
        feature_cols = ['location_x', 'location_y']
        target_col = 'rssi_dbm'
        
        # Check if columns exist
        if not all(col in self.df_cleaned.columns for col in feature_cols + [target_col]):
            print("❌ Required columns not found in data")
            return None, None
        
        # Create feature matrix and target vector
        X = self.df_cleaned[feature_cols].values
        y = self.df_cleaned[target_col].values
        
        print(f"✅ Prepared {len(X)} samples for ML")
        print(f"   Features: {feature_cols}")
        print(f"   Target: {target_col}")
        
        return X, y


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧹 WiFi Data Preprocessing Module")
    print("="*70)
    
    # Create preprocessor
    preprocessor = WiFiDataPreprocessor("wifi_data.csv")
    
    # Load data
    df = preprocessor.load_data()
    
    if df is not None:
        # Inspect data
        preprocessor.inspect_data()
        
        # Clean data
        df_cleaned = preprocessor.clean_data()
        
        # Normalize features
        df_normalized = preprocessor.normalize_features()
        
        # Aggregate by location
        df_aggregated = preprocessor.aggregate_by_location()
        
        # Save cleaned data
        preprocessor.save_cleaned_data("wifi_data_cleaned.csv")
        
        # Prepare for ML
        X, y = preprocessor.get_ml_ready_data()
        
        if X is not None:
            print(f"\n📊 ML Data Ready:")
            print(f"   Features shape: {X.shape}")
            print(f"   Target shape: {y.shape}")
