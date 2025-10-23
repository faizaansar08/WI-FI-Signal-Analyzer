"""
Model Evaluation and Visualization - Member 2 Component
Tests accuracy, creates plots and graphs for report
"""

import pandas as pd
import numpy as np
import joblib
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import os


class ModelEvaluator:
    """Evaluate and visualize ML model performance"""
    
    def __init__(self, model_file="wifi_model.pkl", data_file="wifi_data_cleaned.csv"):
        self.model_file = model_file
        self.data_file = data_file
        self.model_data = None
        self.model = None
        self.scaler = None
        self.df = None
        
        # Set plotting style
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
    
    def load_model(self):
        """Load trained model"""
        try:
            self.model_data = joblib.load(self.model_file)
            self.model = self.model_data['model']
            self.scaler = self.model_data['scaler']
            print(f"✅ Loaded model: {self.model_data['model_name']}")
            return True
        except FileNotFoundError:
            print(f"❌ Model file not found: {self.model_file}")
            print("💡 Run train_model.py first to create the model")
            return False
        except Exception as e:
            print(f"❌ Error loading model: {str(e)}")
            return False
    
    def load_data(self):
        """Load test data"""
        try:
            self.df = pd.read_csv(self.data_file)
            print(f"✅ Loaded {len(self.df)} records from {self.data_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def evaluate_model(self):
        """Evaluate model performance"""
        if self.model is None or self.df is None:
            print("⚠️ Load model and data first")
            return None
        
        print("\n📊 Evaluating model performance...")
        
        # Prepare features
        X = self.df[['location_x', 'location_y']].values
        y = self.df['rssi_dbm'].values
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        y_pred = self.model.predict(X_scaled)
        
        # Calculate metrics
        r2 = r2_score(y, y_pred)
        mse = mean_squared_error(y, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y, y_pred)
        
        # Calculate percentage error
        mape = np.mean(np.abs((y - y_pred) / y)) * 100
        
        metrics = {
            'r2_score': r2,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'mape': mape
        }
        
        print("\n📈 Model Performance Metrics:")
        print(f"  R² Score:                {r2:.4f}")
        print(f"  Mean Squared Error:      {mse:.4f}")
        print(f"  Root Mean Squared Error: {rmse:.4f} dBm")
        print(f"  Mean Absolute Error:     {mae:.4f} dBm")
        print(f"  Mean Abs Percentage Err: {mape:.2f}%")
        
        return metrics, y, y_pred
    
    def plot_actual_vs_predicted(self, y_actual, y_pred, output_file="plots/actual_vs_predicted.png"):
        """Plot actual vs predicted values"""
        os.makedirs("plots", exist_ok=True)
        
        plt.figure(figsize=(10, 8))
        
        # Scatter plot
        plt.scatter(y_actual, y_pred, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        
        # Perfect prediction line
        min_val = min(y_actual.min(), y_pred.min())
        max_val = max(y_actual.max(), y_pred.max())
        plt.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
        
        plt.xlabel('Actual RSSI (dBm)', fontsize=12)
        plt.ylabel('Predicted RSSI (dBm)', fontsize=12)
        plt.title('Actual vs Predicted Signal Strength', fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Add R² score
        r2 = r2_score(y_actual, y_pred)
        plt.text(0.05, 0.95, f'R² = {r2:.4f}', transform=plt.gca().transAxes,
                fontsize=12, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Saved plot: {output_file}")
        plt.close()
    
    def plot_residuals(self, y_actual, y_pred, output_file="plots/residuals.png"):
        """Plot residual distribution"""
        os.makedirs("plots", exist_ok=True)
        
        residuals = y_actual - y_pred
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Residual plot
        axes[0].scatter(y_pred, residuals, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        axes[0].axhline(y=0, color='r', linestyle='--', lw=2)
        axes[0].set_xlabel('Predicted RSSI (dBm)', fontsize=12)
        axes[0].set_ylabel('Residuals (dBm)', fontsize=12)
        axes[0].set_title('Residual Plot', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Histogram of residuals
        axes[1].hist(residuals, bins=30, edgecolor='black', alpha=0.7)
        axes[1].axvline(x=0, color='r', linestyle='--', lw=2)
        axes[1].set_xlabel('Residuals (dBm)', fontsize=12)
        axes[1].set_ylabel('Frequency', fontsize=12)
        axes[1].set_title('Distribution of Residuals', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Saved plot: {output_file}")
        plt.close()
    
    def plot_signal_vs_location(self, output_file="plots/signal_vs_location.png"):
        """Plot signal strength vs location"""
        if self.df is None:
            return
        
        os.makedirs("plots", exist_ok=True)
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Signal vs X coordinate
        axes[0].scatter(self.df['location_x'], self.df['rssi_dbm'], 
                       alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
        axes[0].set_xlabel('Location X (meters)', fontsize=12)
        axes[0].set_ylabel('RSSI (dBm)', fontsize=12)
        axes[0].set_title('Signal Strength vs X Coordinate', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Signal vs Y coordinate
        axes[1].scatter(self.df['location_y'], self.df['rssi_dbm'],
                       alpha=0.6, s=50, color='orange', edgecolors='black', linewidth=0.5)
        axes[1].set_xlabel('Location Y (meters)', fontsize=12)
        axes[1].set_ylabel('RSSI (dBm)', fontsize=12)
        axes[1].set_title('Signal Strength vs Y Coordinate', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Saved plot: {output_file}")
        plt.close()
    
    def plot_signal_heatmap(self, grid_size=50, output_file="plots/signal_heatmap.png"):
        """Create signal strength heatmap"""
        if self.model is None or self.df is None:
            return
        
        os.makedirs("plots", exist_ok=True)
        
        # Get data range
        x_min, x_max = self.df['location_x'].min(), self.df['location_x'].max()
        y_min, y_max = self.df['location_y'].min(), self.df['location_y'].max()
        
        # Add padding
        x_range = x_max - x_min
        y_range = y_max - y_min
        x_min -= x_range * 0.1
        x_max += x_range * 0.1
        y_min -= y_range * 0.1
        y_max += y_range * 0.1
        
        # Create grid
        x_grid = np.linspace(x_min, x_max, grid_size)
        y_grid = np.linspace(y_min, y_max, grid_size)
        X_mesh, Y_mesh = np.meshgrid(x_grid, y_grid)
        
        # Predict for each grid point
        grid_points = np.c_[X_mesh.ravel(), Y_mesh.ravel()]
        grid_points_scaled = self.scaler.transform(grid_points)
        Z = self.model.predict(grid_points_scaled).reshape(X_mesh.shape)
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        
        # Contour plot
        contour = plt.contourf(X_mesh, Y_mesh, Z, levels=20, cmap='RdYlGn', alpha=0.8)
        plt.colorbar(contour, label='Signal Strength (dBm)')
        
        # Overlay actual data points
        scatter = plt.scatter(self.df['location_x'], self.df['location_y'], 
                            c=self.df['rssi_dbm'], s=100, cmap='RdYlGn',
                            edgecolors='black', linewidth=1.5, alpha=0.9)
        
        plt.xlabel('Location X (meters)', fontsize=12)
        plt.ylabel('Location Y (meters)', fontsize=12)
        plt.title('WiFi Signal Strength Heatmap', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Saved heatmap: {output_file}")
        plt.close()
    
    def plot_3d_surface(self, grid_size=50, output_file="plots/signal_3d_surface.png"):
        """Create 3D surface plot of signal strength"""
        if self.model is None or self.df is None:
            return
        
        os.makedirs("plots", exist_ok=True)
        
        from mpl_toolkits.mplot3d import Axes3D
        
        # Get data range
        x_min, x_max = self.df['location_x'].min(), self.df['location_x'].max()
        y_min, y_max = self.df['location_y'].min(), self.df['location_y'].max()
        
        # Create grid
        x_grid = np.linspace(x_min, x_max, grid_size)
        y_grid = np.linspace(y_min, y_max, grid_size)
        X_mesh, Y_mesh = np.meshgrid(x_grid, y_grid)
        
        # Predict
        grid_points = np.c_[X_mesh.ravel(), Y_mesh.ravel()]
        grid_points_scaled = self.scaler.transform(grid_points)
        Z = self.model.predict(grid_points_scaled).reshape(X_mesh.shape)
        
        # Create 3D plot
        fig = plt.figure(figsize=(14, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Surface plot
        surf = ax.plot_surface(X_mesh, Y_mesh, Z, cmap='RdYlGn', alpha=0.8)
        
        # Scatter actual points
        ax.scatter(self.df['location_x'], self.df['location_y'], self.df['rssi_dbm'],
                  c='black', s=50, alpha=0.6)
        
        ax.set_xlabel('Location X (meters)', fontsize=10)
        ax.set_ylabel('Location Y (meters)', fontsize=10)
        ax.set_zlabel('Signal Strength (dBm)', fontsize=10)
        ax.set_title('3D Signal Strength Surface', fontsize=14, fontweight='bold')
        
        fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label='RSSI (dBm)')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Saved 3D plot: {output_file}")
        plt.close()
    
    def plot_network_comparison(self, output_file="plots/network_comparison.png"):
        """Compare signal strength across different networks"""
        if self.df is None or 'ssid' not in self.df.columns:
            return
        
        os.makedirs("plots", exist_ok=True)
        
        # Get top 5 networks by number of measurements
        top_networks = self.df['ssid'].value_counts().head(5).index
        df_filtered = self.df[self.df['ssid'].isin(top_networks)]
        
        plt.figure(figsize=(12, 8))
        
        # Box plot
        sns.boxplot(data=df_filtered, x='ssid', y='rssi_dbm', palette='Set2')
        
        plt.xlabel('Network SSID', fontsize=12)
        plt.ylabel('Signal Strength (dBm)', fontsize=12)
        plt.title('Signal Strength Comparison Across Networks', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Saved plot: {output_file}")
        plt.close()
    
    def generate_all_plots(self):
        """Generate all visualization plots"""
        print("\n📊 Generating all plots...")
        
        # Evaluate model first
        metrics, y_actual, y_pred = self.evaluate_model()
        
        if metrics is None:
            return
        
        # Generate plots
        self.plot_actual_vs_predicted(y_actual, y_pred)
        self.plot_residuals(y_actual, y_pred)
        self.plot_signal_vs_location()
        self.plot_signal_heatmap()
        self.plot_3d_surface()
        self.plot_network_comparison()
        
        print("\n✅ All plots generated successfully!")
        print("   Check the 'plots/' directory")
    
    def create_report_summary(self, output_file="plots/evaluation_report.txt"):
        """Create text summary for report"""
        os.makedirs("plots", exist_ok=True)
        
        metrics, y_actual, y_pred = self.evaluate_model()
        
        if metrics is None:
            return
        
        with open(output_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("   WI-FI SIGNAL STRENGTH PREDICTION - MODEL EVALUATION REPORT\n")
            f.write("="*70 + "\n\n")
            
            f.write(f"Model Type: {self.model_data['model_name']}\n")
            f.write(f"Training Date: {self.model_data['trained_date']}\n\n")
            
            f.write("PERFORMANCE METRICS:\n")
            f.write("-" * 70 + "\n")
            f.write(f"R² Score:                    {metrics['r2_score']:.4f}\n")
            f.write(f"Mean Squared Error (MSE):    {metrics['mse']:.4f}\n")
            f.write(f"Root MSE (RMSE):             {metrics['rmse']:.4f} dBm\n")
            f.write(f"Mean Absolute Error (MAE):   {metrics['mae']:.4f} dBm\n")
            f.write(f"Mean Absolute % Error:       {metrics['mape']:.2f}%\n\n")
            
            f.write("INTERPRETATION:\n")
            f.write("-" * 70 + "\n")
            
            if metrics['r2_score'] >= 0.9:
                f.write("• Model shows EXCELLENT predictive performance (R² ≥ 0.9)\n")
            elif metrics['r2_score'] >= 0.7:
                f.write("• Model shows GOOD predictive performance (R² ≥ 0.7)\n")
            elif metrics['r2_score'] >= 0.5:
                f.write("• Model shows MODERATE predictive performance (R² ≥ 0.5)\n")
            else:
                f.write("• Model shows LIMITED predictive performance (R² < 0.5)\n")
            
            f.write(f"• Average prediction error: ±{metrics['mae']:.2f} dBm\n")
            f.write(f"• Model explains {metrics['r2_score']*100:.1f}% of variance in signal strength\n\n")
            
            f.write("DATASET STATISTICS:\n")
            f.write("-" * 70 + "\n")
            f.write(f"Total Samples:         {len(self.df)}\n")
            f.write(f"Unique Locations:      {self.df[['location_x', 'location_y']].drop_duplicates().shape[0]}\n")
            if 'ssid' in self.df.columns:
                f.write(f"Unique Networks:       {self.df['ssid'].nunique()}\n")
            f.write(f"Signal Range:          {self.df['rssi_dbm'].min():.1f} to {self.df['rssi_dbm'].max():.1f} dBm\n")
            f.write(f"Average Signal:        {self.df['rssi_dbm'].mean():.2f} dBm\n\n")
            
            f.write("GENERATED VISUALIZATIONS:\n")
            f.write("-" * 70 + "\n")
            f.write("1. actual_vs_predicted.png  - Actual vs Predicted scatter plot\n")
            f.write("2. residuals.png            - Residual analysis plots\n")
            f.write("3. signal_vs_location.png   - Signal vs location coordinates\n")
            f.write("4. signal_heatmap.png       - 2D signal strength heatmap\n")
            f.write("5. signal_3d_surface.png    - 3D signal strength surface\n")
            f.write("6. network_comparison.png   - Network-wise signal comparison\n\n")
            
            f.write("="*70 + "\n")
        
        print(f"✅ Saved evaluation report: {output_file}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("📊 Wi-Fi Signal Prediction - Model Evaluation")
    print("="*70)
    
    evaluator = ModelEvaluator("wifi_model.pkl", "wifi_data_cleaned.csv")
    
    # Load model and data
    if evaluator.load_model() and evaluator.load_data():
        # Generate all plots
        evaluator.generate_all_plots()
        
        # Create report
        evaluator.create_report_summary()
        
        print("\n✅ Evaluation complete!")
        print("   Check the 'plots/' directory for all visualizations")
    else:
        print("\n❌ Could not complete evaluation")
        print("💡 Make sure to run train_model.py first")
