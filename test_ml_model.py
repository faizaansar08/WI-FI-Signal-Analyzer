# ═══════════════════════════════════════════════════════════════
# 🤖 ML MODEL IS WORKING! Here's How to See It:
# ═══════════════════════════════════════════════════════════════

# The ML model is loaded and working in your Flask app!
# The difference is that NOW you can make INTELLIGENT PREDICTIONS
# based on location coordinates.

# ═══════════════════════════════════════════════════════════════
# 🎯 3 WAYS TO SEE THE ML MODEL IN ACTION:
# ═══════════════════════════════════════════════════════════════

# ────────────────────────────────────────────────────────────────
# METHOD 1: Open the ML Demo Page (EASIEST!)
# ────────────────────────────────────────────────────────────────
# Open your browser and go to:
#
#     http://localhost:5000/ml-demo
#
# This page will:
#   ✓ Show ML model status
#   ✓ Let you input X, Y coordinates
#   ✓ Predict signal strength at that location
#   ✓ Display results instantly
#
# Try these coordinates:
#   • (0.5, 0.5)  - Near training point
#   • (2.5, 2.5)  - Middle of trained area
#   • (3.5, 3.5)  - Another trained point
# ────────────────────────────────────────────────────────────────


# ────────────────────────────────────────────────────────────────
# METHOD 2: Test via PowerShell API Call
# ────────────────────────────────────────────────────────────────
# Run this in PowerShell (new terminal):

"""
$body = @{
    location_x = 2.5
    location_y = 2.5
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/predict" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"
"""

# Expected Response:
"""
{
    "predicted_rssi": -48.2,
    "signal_quality": 68,
    "prediction_source": "ml_model",
    "model_used": "k-Nearest Neighbors",
    "location": {"x": 2.5, "y": 2.5}
}
"""
# ────────────────────────────────────────────────────────────────


# ────────────────────────────────────────────────────────────────
# METHOD 3: Run This Python Test Script
# ────────────────────────────────────────────────────────────────

import requests
import json

def test_ml_prediction():
    """Test the ML model prediction API"""
    
    print("=" * 70)
    print("🤖 TESTING ML MODEL PREDICTIONS")
    print("=" * 70)
    print()
    
    # Test different locations
    test_locations = [
        (0.0, 0.0, "Training Point A"),
        (1.0, 1.0, "Training Point B"),
        (2.5, 2.5, "Middle Area"),
        (3.5, 3.5, "Between C and D"),
        (0.5, 1.5, "Random Location"),
    ]
    
    for x, y, description in test_locations:
        print(f"📍 Testing: {description}")
        print(f"   Location: ({x}, {y})")
        
        try:
            # Make API request
            response = requests.post(
                'http://localhost:5000/api/predict',
                json={'location_x': x, 'location_y': y},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"   ✅ Predicted RSSI: {data.get('predicted_rssi', 'N/A'):.2f} dBm")
                print(f"   📊 Signal Quality: {data.get('signal_quality', 'N/A')}%")
                print(f"   🤖 Model Used: {data.get('model_used', 'N/A')}")
                print(f"   🎯 Source: {data.get('prediction_source', 'N/A')}")
                
                # Determine signal status
                rssi = data.get('predicted_rssi', -100)
                if rssi > -50:
                    status = "🟢 Excellent"
                elif rssi > -60:
                    status = "🟡 Good"
                elif rssi > -70:
                    status = "🟠 Fair"
                else:
                    status = "🔴 Weak"
                print(f"   Status: {status}")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   {response.text}")
        
        except Exception as e:
            print(f"   ❌ Connection Error: {str(e)}")
            print(f"   Make sure Flask app is running on http://localhost:5000")
        
        print("-" * 70)
        print()

if __name__ == "__main__":
    print()
    print("🚀 Make sure Flask app is running first!")
    print("   (It should be running on http://localhost:5000)")
    print()
    input("Press Enter to start testing...")
    print()
    
    test_ml_prediction()
    
    print()
    print("=" * 70)
    print("✅ TESTING COMPLETE!")
    print("=" * 70)
    print()
    print("💡 The ML model predicts signal strength based on location!")
    print("   This is different from the basic dashboard which just scans.")
    print()
    print("📊 Want to see visualizations?")
    print("   Check the 'plots/' folder for 6 generated graphs!")
    print()
