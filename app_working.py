"""
Wi-Fi Signal Strength Analyzer - COMPLETE WORKING VERSION
Includes: WiFi Scanning, Real-time Monitoring, ML Predictions, Socket.IO
Port: 8080 (to avoid Windows port 5000 restrictions)
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from datetime import datetime
from wifi_scanner import WiFiScanner
import joblib
import numpy as np
import os

print("="*70)
print("🌐 Wi-Fi Signal Strength Analyzer - COMPLETE VERSION")
print("="*70)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wifi-analyzer-2025'
CORS(app)

# Initialize SocketIO with eventlet
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize WiFi Scanner
scanner = WiFiScanner()

# Load ML model if available
ml_model = None
ml_scaler = None
ml_model_name = None

try:
    if os.path.exists('wifi_model.pkl'):
        model_data = joblib.load('wifi_model.pkl')
        ml_model = model_data['model']
        ml_scaler = model_data['scaler']
        ml_model_name = model_data['model_name']
        print(f"✅ Loaded ML model: {ml_model_name}")
    else:
        print("⚠️  ML model not found (wifi_model.pkl). ML predictions disabled.")
except Exception as e:
    print(f"⚠️  Could not load ML model: {str(e)}")

# Global variables
monitoring_active = False
monitoring_thread = None
selected_network = None

def background_monitor():
    """Background thread for continuous WiFi monitoring"""
    global monitoring_active, selected_network
    
    print("📡 Background monitoring started")
    
    while monitoring_active:
        try:
            networks = scanner.scan_networks()
            
            if networks:
                # Emit all networks
                socketio.emit('networks_update', {
                    'networks': networks,
                    'timestamp': datetime.now().isoformat(),
                    'count': len(networks)
                })
                
                # If specific network selected, emit its data
                if selected_network:
                    network_data = next(
                        (n for n in networks if n['ssid'] == selected_network),
                        None
                    )
                    
                    if network_data:
                        socketio.emit('signal_update', {
                            'ssid': network_data['ssid'],
                            'signal_strength': network_data['signal_strength'],
                            'signal_quality': network_data['signal_quality'],
                            'frequency': network_data.get('frequency', 'N/A'),
                            'channel': network_data.get('channel', 'N/A'),
                            'security': network_data.get('security', 'N/A'),
                            'timestamp': datetime.now().isoformat()
                        })
            
            time.sleep(2)  # Scan every 2 seconds
            
        except Exception as e:
            print(f"❌ Monitoring error: {str(e)}")
            socketio.emit('error', {'message': f'Monitoring error: {str(e)}'})
            time.sleep(5)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/ml-demo')
def ml_demo():
    return render_template('ml_demo.html')

@app.route('/api/signal', methods=['GET'])
def get_signal():
    try:
        networks = scanner.scan_networks()
        return jsonify({
            'success': True,
            'networks': networks,
            'timestamp': datetime.now().isoformat(),
            'count': len(networks),
            'ml_available': ml_model is not None,
            'model_type': ml_model_name if ml_model_name else None
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/predict', methods=['POST'])
def predict_signal():
    try:
        data = request.get_json()
        
        # ML prediction if coordinates provided
        if 'location_x' in data and 'location_y' in data and ml_model is not None:
            location_x = float(data['location_x'])
            location_y = float(data['location_y'])
            
            X_input = np.array([[location_x, location_y]])
            X_scaled = ml_scaler.transform(X_input)
            predicted_rssi = float(ml_model.predict(X_scaled)[0])
            
            # Convert RSSI to quality percentage
            signal_quality = max(0, min(100, int((predicted_rssi + 100) * 2)))
            
            return jsonify({
                'success': True,
                'predicted_rssi': round(predicted_rssi, 2),
                'signal_quality': signal_quality,
                'prediction_source': 'ml_model',
                'model_used': ml_model_name,
                'location': {'x': location_x, 'y': location_y}
            }), 200
        
        # Basic prediction if signal strength provided
        elif 'signal_strength' in data:
            signal_strength = int(data['signal_strength'])
            quality = max(0, min(100, (signal_strength + 100) * 2))
            
            return jsonify({
                'success': True,
                'signal_strength': signal_strength,
                'signal_quality': quality,
                'prediction_source': 'basic_calculation'
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Socket.IO Events
@socketio.on('connect')
def handle_connect():
    print(f"✅ Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected', 'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"❌ Client disconnected: {request.sid}")

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    global monitoring_active, monitoring_thread, selected_network
    
    selected_network = data.get('ssid', None) if data else None
    
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=background_monitor)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        emit('monitoring_status', {
            'status': 'started',
            'message': 'Monitoring started',
            'selected_network': selected_network
        })
        print("🚀 Monitoring started")

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    global monitoring_active, selected_network
    
    monitoring_active = False
    selected_network = None
    
    emit('monitoring_status', {
        'status': 'stopped',
        'message': 'Monitoring stopped'
    })
    print("⏹️  Monitoring stopped")

@socketio.on('select_network')
def handle_select_network(data):
    global selected_network
    
    selected_network = data.get('ssid', None)
    
    emit('monitoring_status', {
        'status': 'network_selected',
        'selected_network': selected_network
    })
    print(f"📶 Selected network: {selected_network}")

@socketio.on('scan_once')
def handle_scan_once():
    try:
        networks = scanner.scan_networks()
        
        emit('networks_update', {
            'networks': networks,
            'timestamp': datetime.now().isoformat(),
            'count': len(networks)
        })
        
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    print("\n" + "="*70)
    print("📡 Server Configuration:")
    print(f"   URL: http://localhost:8080")
    print(f"   ML Model: {'✅ Loaded' if ml_model else '❌ Not Available'}")
    print(f"   WiFi Scanner: ✅ Ready")
    print("="*70)
    print("\n🚀 Starting server...")
    print("⚠️  KEEP THIS WINDOW OPEN while using the application!")
    print("Press Ctrl+C to stop\n")
    print("="*70 + "\n")
    
    try:
        socketio.run(app, host='0.0.0.0', port=8080, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        input("\nPress Enter to exit...")
