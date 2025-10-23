"""
Wi-Fi Signal Strength Analyzer - Main Flask Application
Real-time signal monitoring with SocketIO
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
import random
from datetime import datetime
from wifi_scanner import WiFiScanner
import joblib
import numpy as np
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wifi-signal-analyzer-secret-2025'
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
        print("⚠️ ML model not found. Using basic prediction logic.")
except Exception as e:
    print(f"⚠️ Could not load ML model: {str(e)}")

# Global variables for real-time monitoring
monitoring_active = False
monitoring_thread = None
selected_network = None


def background_monitor():
    """Background thread for continuous WiFi signal monitoring"""
    global monitoring_active, selected_network
    
    print("📡 Starting background WiFi monitoring...")
    
    while monitoring_active:
        try:
            # Scan for WiFi networks
            networks = scanner.scan_networks()
            
            if networks:
                # Emit all networks to frontend
                socketio.emit('networks_update', {
                    'networks': networks,
                    'timestamp': datetime.now().isoformat(),
                    'count': len(networks)
                })
                
                # If a specific network is selected, emit detailed data
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
            else:
                socketio.emit('error', {'message': 'No networks detected'})
            
            # Wait before next scan (adjust for performance)
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error in monitoring: {str(e)}")
            socketio.emit('error', {'message': f'Monitoring error: {str(e)}'})
            time.sleep(5)


@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/test')
def test():
    """Render test page"""
    return render_template('test.html')


@app.route('/ml-demo')
def ml_demo():
    """Render ML prediction demo page"""
    return render_template('ml_demo.html')


@app.route('/api/signal', methods=['GET'])
def get_signal():
    """
    API Endpoint: Get current WiFi signal strength
    Returns: JSON with signal data
    """
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
    """
    API Endpoint: Predict signal quality based on input data
    Expected JSON: 
    - Option 1: { "ssid": "network_name", "signal_strength": -50 }
    - Option 2 (ML): { "location_x": 2.5, "location_y": 3.0 }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No input data provided'
            }), 400
        
        # Check if using ML model with location coordinates
        if 'location_x' in data and 'location_y' in data and ml_model is not None:
            location_x = float(data.get('location_x'))
            location_y = float(data.get('location_y'))
            
            # Predict using ML model
            X_input = np.array([[location_x, location_y]])
            X_scaled = ml_scaler.transform(X_input)
            predicted_rssi = ml_model.predict(X_scaled)[0]
            
            # Calculate quality from predicted RSSI
            quality = scanner.calculate_quality(predicted_rssi)
            
            prediction = {
                'location_x': location_x,
                'location_y': location_y,
                'predicted_rssi': round(predicted_rssi, 2),
                'signal_quality': quality,
                'status': 'Excellent' if quality >= 80 else 'Good' if quality >= 60 else 'Fair' if quality >= 40 else 'Poor',
                'recommendation': get_recommendation(quality),
                'model_used': ml_model_name,
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'prediction': prediction,
                'ml_powered': True
            }), 200
        
        # Fallback to basic prediction with signal strength
        elif 'signal_strength' in data:
            signal_strength = data.get('signal_strength', 0)
            ssid = data.get('ssid', 'Unknown')
            
            # Calculate signal quality percentage
            quality = scanner.calculate_quality(signal_strength)
            
            prediction = {
                'ssid': ssid,
                'signal_strength': signal_strength,
                'signal_quality': quality,
                'status': 'Excellent' if quality >= 80 else 'Good' if quality >= 60 else 'Fair' if quality >= 40 else 'Poor',
                'recommendation': get_recommendation(quality),
                'model_used': 'Basic calculation',
                'timestamp': datetime.now().isoformat()
            }
            
            return jsonify({
                'success': True,
                'prediction': prediction,
                'ml_powered': False
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid input. Provide either (location_x, location_y) or signal_strength'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def get_recommendation(quality):
    """Provide recommendations based on signal quality"""
    if quality >= 80:
        return "Excellent connection! Perfect for streaming and gaming."
    elif quality >= 60:
        return "Good connection. Suitable for most online activities."
    elif quality >= 40:
        return "Fair connection. May experience occasional slowdowns."
    else:
        return "Poor connection. Consider moving closer to the router."


# SocketIO Event Handlers

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"✅ Client connected: {request.sid}")
    emit('connection_status', {
        'status': 'connected',
        'message': 'Successfully connected to WiFi Analyzer',
        'timestamp': datetime.now().isoformat()
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"❌ Client disconnected: {request.sid}")


@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """Start continuous WiFi monitoring"""
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
    else:
        emit('monitoring_status', {
            'status': 'already_running',
            'message': 'Monitoring already active'
        })


@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """Stop continuous WiFi monitoring"""
    global monitoring_active, selected_network
    
    monitoring_active = False
    selected_network = None
    
    emit('monitoring_status', {
        'status': 'stopped',
        'message': 'Monitoring stopped'
    })
    print("⏹️ Monitoring stopped")


@socketio.on('select_network')
def handle_select_network(data):
    """Select a specific network to monitor"""
    global selected_network
    
    selected_network = data.get('ssid', None)
    
    emit('monitoring_status', {
        'status': 'network_selected',
        'selected_network': selected_network
    })
    print(f"📶 Selected network: {selected_network}")


@socketio.on('scan_once')
def handle_scan_once():
    """Perform a single WiFi scan"""
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
    print("\n" + "="*60)
    print("🌐 Wi-Fi Signal Strength Analyzer")
    print("="*60)
    print("📡 Server starting...")
    print("🔗 Access dashboard at: http://localhost:5000")
    print("="*60 + "\n")
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
