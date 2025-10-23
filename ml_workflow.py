"""
Complete ML Workflow - Member 2 Component
End-to-end pipeline: Data Collection → Preprocessing → Training → Evaluation
"""

import os
import sys
from datetime import datetime


def run_complete_workflow(num_locations=5, scans_per_location=3, optimize_model=False):
    """
    Run the complete ML workflow
    
    Args:
        num_locations: Number of sample locations to collect data from
        scans_per_location: Number of scans at each location
        optimize_model: Whether to optimize hyperparameters (slower but better)
    """
    print("\n" + "="*80)
    print("🤖 COMPLETE MACHINE LEARNING WORKFLOW")
    print("   WiFi Signal Strength Prediction System")
    print("="*80)
    
    print(f"\nConfiguration:")
    print(f"  • Sample locations: {num_locations}")
    print(f"  • Scans per location: {scans_per_location}")
    print(f"  • Hyperparameter optimization: {optimize_model}")
    print("\n" + "="*80)
    
    # Step 1: Data Collection
    print("\n📡 STEP 1: DATA COLLECTION")
    print("-" * 80)
    
    from wifi_data_collector import WiFiDataCollector
    
    collector = WiFiDataCollector("wifi_data.csv")
    
    # Create sample locations (can be customized)
    locations = []
    for i in range(num_locations):
        x = i * 1.0
        y = i * 1.0
        name = f"Location_{chr(65+i)}"  # Location_A, Location_B, etc.
        locations.append((x, y, name))
    
    print(f"Collecting data at {num_locations} locations...")
    total_points = collector.collect_custom_locations(locations, num_scans=scans_per_location)
    
    print(f"\n✅ Data collection complete!")
    print(f"   Total data points: {total_points}")
    print(f"   Saved to: wifi_data.csv")
    
    # Step 2: Data Preprocessing
    print("\n" + "="*80)
    print("🧹 STEP 2: DATA PREPROCESSING")
    print("-" * 80)
    
    from data_preprocessing import WiFiDataPreprocessor
    
    preprocessor = WiFiDataPreprocessor("wifi_data.csv")
    
    if preprocessor.load_data() is None:
        print("❌ Failed to load data")
        return False
    
    preprocessor.inspect_data()
    df_cleaned = preprocessor.clean_data()
    preprocessor.save_cleaned_data("wifi_data_cleaned.csv")
    
    print(f"\n✅ Preprocessing complete!")
    print(f"   Saved to: wifi_data_cleaned.csv")
    
    # Step 3: Model Training
    print("\n" + "="*80)
    print("🤖 STEP 3: MODEL TRAINING")
    print("-" * 80)
    
    from train_model import train_and_save_models
    
    predictor = train_and_save_models(
        data_file="wifi_data_cleaned.csv",
        output_file="wifi_model.pkl",
        optimize=optimize_model
    )
    
    if predictor is None:
        print("❌ Failed to train model")
        return False
    
    print(f"\n✅ Model training complete!")
    print(f"   Saved to: wifi_model.pkl")
    
    # Step 4: Model Evaluation
    print("\n" + "="*80)
    print("📊 STEP 4: MODEL EVALUATION & VISUALIZATION")
    print("-" * 80)
    
    from model_evaluation import ModelEvaluator
    
    evaluator = ModelEvaluator("wifi_model.pkl", "wifi_data_cleaned.csv")
    
    if evaluator.load_model() and evaluator.load_data():
        evaluator.generate_all_plots()
        evaluator.create_report_summary()
        
        print(f"\n✅ Evaluation complete!")
        print(f"   Plots saved to: plots/")
        print(f"   Report saved to: plots/evaluation_report.txt")
    
    # Final Summary
    print("\n" + "="*80)
    print("✅ WORKFLOW COMPLETE!")
    print("="*80)
    
    print("\n📂 Generated Files:")
    print("   1. wifi_data.csv              - Raw collected data")
    print("   2. wifi_data_cleaned.csv      - Preprocessed data")
    print("   3. wifi_model.pkl             - Trained ML model")
    print("   4. plots/evaluation_report.txt - Performance report")
    print("   5. plots/actual_vs_predicted.png")
    print("   6. plots/residuals.png")
    print("   7. plots/signal_vs_location.png")
    print("   8. plots/signal_heatmap.png")
    print("   9. plots/signal_3d_surface.png")
    print("   10. plots/network_comparison.png")
    
    print("\n💡 Next Steps:")
    print("   • View plots in 'plots/' directory")
    print("   • Read evaluation report for model performance")
    print("   • Integrate model with Flask app (already done!)")
    print("   • Test predictions via /api/predict endpoint")
    
    print("\n🎉 Machine Learning pipeline ready for use!")
    print("="*80 + "\n")
    
    return True


def quick_demo():
    """Run a quick demo with minimal data"""
    print("\n🚀 Running Quick Demo Mode...")
    print("   This will create a small dataset for testing\n")
    
    return run_complete_workflow(
        num_locations=5,
        scans_per_location=2,
        optimize_model=False
    )


def full_workflow():
    """Run the full workflow with optimization"""
    print("\n🏆 Running Full Workflow Mode...")
    print("   This will create a comprehensive dataset\n")
    
    response = input("Number of locations to survey (default 10): ").strip()
    num_locations = int(response) if response.isdigit() else 10
    
    response = input("Scans per location (default 3): ").strip()
    scans_per_location = int(response) if response.isdigit() else 3
    
    response = input("Optimize hyperparameters? (y/N): ").strip().lower()
    optimize = response == 'y'
    
    return run_complete_workflow(
        num_locations=num_locations,
        scans_per_location=scans_per_location,
        optimize_model=optimize
    )


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🌐 WiFi Signal Strength Prediction - ML Workflow")
    print("="*80)
    
    print("\n📋 Workflow Options:")
    print("   1. Quick Demo (5 locations, 2 scans, no optimization)")
    print("   2. Full Workflow (custom settings)")
    print("   3. Exit")
    
    choice = input("\n👉 Select option (1-3): ").strip()
    
    if choice == '1':
        success = quick_demo()
    elif choice == '2':
        success = full_workflow()
    elif choice == '3':
        print("\n👋 Exiting. Goodbye!")
        sys.exit(0)
    else:
        print("\n❌ Invalid option")
        sys.exit(1)
    
    if success:
        print("\n✅ Workflow completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Workflow failed. Check errors above.")
        sys.exit(1)
