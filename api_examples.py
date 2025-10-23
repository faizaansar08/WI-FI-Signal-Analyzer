"""
API Testing Examples - Wi-Fi Signal Analyzer
Use these examples to test the API endpoints
"""

# ============================================================================
# 1. Testing with Python requests library
# ============================================================================

import requests
import json

BASE_URL = "http://localhost:5000"

# Test GET /api/signal
print("Testing GET /api/signal...")
response = requests.get(f"{BASE_URL}/api/signal")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

# Test POST /api/predict
print("Testing POST /api/predict...")
data = {
    "ssid": "TestNetwork",
    "signal_strength": -55
}
response = requests.post(f"{BASE_URL}/api/predict", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# ============================================================================
# 2. PowerShell Examples
# ============================================================================

"""
# Test GET /api/signal
Invoke-RestMethod -Uri "http://localhost:5000/api/signal" -Method Get

# Test POST /api/predict
$body = @{
    ssid = "TestNetwork"
    signal_strength = -55
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/predict" -Method Post -Body $body -ContentType "application/json"
"""

# ============================================================================
# 3. cURL Examples
# ============================================================================

"""
# Test GET /api/signal
curl http://localhost:5000/api/signal

# Test POST /api/predict
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"ssid": "TestNetwork", "signal_strength": -55}'
"""

# ============================================================================
# 4. JavaScript Fetch Examples
# ============================================================================

"""
// Test GET /api/signal
fetch('http://localhost:5000/api/signal')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));

// Test POST /api/predict
fetch('http://localhost:5000/api/predict', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    ssid: 'TestNetwork',
    signal_strength: -55
  })
})
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('Error:', error));
"""

# ============================================================================
# 5. Socket.IO Testing with Python
# ============================================================================

"""
import socketio

sio = socketio.Client()

@sio.on('connect')
def on_connect():
    print('Connected to server')

@sio.on('networks_update')
def on_networks(data):
    print('Networks:', data)

@sio.on('signal_update')
def on_signal(data):
    print('Signal:', data)

sio.connect('http://localhost:5000')

# Start monitoring
sio.emit('start_monitoring', {})

# Wait for updates
sio.wait()
"""

# ============================================================================
# 6. Expected Response Formats
# ============================================================================

EXAMPLE_RESPONSES = {
    "GET /api/signal": {
        "success": True,
        "networks": [
            {
                "ssid": "Home_WiFi_5G",
                "signal_strength": -45,
                "signal_quality": 75,
                "frequency": "5 GHz (Ch 36)",
                "channel": 36,
                "security": "WPA2"
            },
            {
                "ssid": "Office_Network",
                "signal_strength": -55,
                "signal_quality": 58,
                "frequency": "2.4 GHz (Ch 6)",
                "channel": 6,
                "security": "WPA2-Enterprise"
            }
        ],
        "timestamp": "2025-10-22T10:30:00.000Z",
        "count": 2
    },
    
    "POST /api/predict": {
        "success": True,
        "prediction": {
            "ssid": "TestNetwork",
            "signal_strength": -55,
            "signal_quality": 58,
            "status": "Fair",
            "recommendation": "Fair connection. May experience occasional slowdowns.",
            "timestamp": "2025-10-22T10:30:00.000Z"
        }
    }
}

# Print example responses
print("\n" + "="*70)
print("EXAMPLE API RESPONSES")
print("="*70)
for endpoint, response in EXAMPLE_RESPONSES.items():
    print(f"\n{endpoint}:")
    print(json.dumps(response, indent=2))

print("\n" + "="*70)
print("To run these tests:")
print("1. Start the server: python app.py")
print("2. Run this script: python api_examples.py")
print("3. Or use PowerShell/curl commands from comments above")
print("="*70)
