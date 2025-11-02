"""
Wi-Fi Signal Strength Analyzer - SIMPLIFIED WORKING VERSION
NO eventlet dependency - uses threading mode
Port: 8080
"""

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from datetime import datetime
from wifi_scanner import WiFiScanner
import sys

print("="*70)
print("🌐 Wi-Fi Signal Strength Analyzer")
print("="*70)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wifi-analyzer-2025'
CORS(app)

# Initialize SocketIO with threading (NO eventlet!)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize WiFi Scanner
scanner = WiFiScanner()

# Global variables
monitoring_active = False
monitoring_thread = None
selected_networks = []  # Support multiple networks

def background_monitor():
    """Background thread for continuous WiFi monitoring - SUPPORTS MULTIPLE NETWORKS"""
    global monitoring_active, selected_networks
    
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
                }, namespace='/')
                
                # If specific networks selected, emit their data
                if selected_networks:
                    for ssid in selected_networks:
                        network_data = next(
                            (n for n in networks if n['ssid'] == ssid),
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
                            }, namespace='/')
            
            time.sleep(2)  # Scan every 2 seconds
            
        except Exception as e:
            print(f"❌ Monitoring error: {str(e)}")
            time.sleep(5)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/multi')
def multi():
    """Multi-network monitoring page"""
    return render_template('index_multi.html')

@app.route('/test')
def test():
    return render_template('test.html')

@app.route('/api/signal', methods=['GET'])
def get_signal():
    try:
        networks = scanner.scan_networks()
        return jsonify({
            'success': True,
            'networks': networks,
            'timestamp': datetime.now().isoformat(),
            'count': len(networks)
        }), 200
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
    global monitoring_active, monitoring_thread, selected_networks
    
    # Support multiple networks - receive as list
    if data and 'ssid' in data:
        # Single network (backward compatibility)
        selected_networks = [data.get('ssid')]
    elif data and 'networks' in data:
        # Multiple networks
        selected_networks = data.get('networks', [])
    else:
        selected_networks = []
    
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=background_monitor)
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        emit('monitoring_status', {
            'status': 'started',
            'message': 'Monitoring started',
            'selected_networks': selected_networks
        })
        print(f"🚀 Monitoring started for {len(selected_networks)} network(s)")

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    global monitoring_active, selected_networks
    
    monitoring_active = False
    selected_networks = []
    
    emit('monitoring_status', {
        'status': 'stopped',
        'message': 'Monitoring stopped'
    })
    print("⏹️  Monitoring stopped")

@socketio.on('select_network')
def handle_select_network(data):
    global selected_networks
    
    ssid = data.get('ssid', None)
    action = data.get('action', 'toggle')  # 'toggle', 'add', 'remove'
    
    if action == 'add' and ssid and ssid not in selected_networks:
        selected_networks.append(ssid)
    elif action == 'remove' and ssid in selected_networks:
        selected_networks.remove(ssid)
    elif action == 'toggle' and ssid:
        if ssid in selected_networks:
            selected_networks.remove(ssid)
        else:
            selected_networks.append(ssid)
    
    emit('monitoring_status', {
        'status': 'network_selected',
        'selected_networks': selected_networks
    })
    print(f"📶 Selected networks: {', '.join(selected_networks) if selected_networks else 'None'}")

@socketio.on('scan_once')
def handle_scan_once():
    try:
        print("📡 Performing single scan...")
        networks = scanner.scan_networks()
        print(f"✅ Found {len(networks)} networks")
        
        emit('networks_update', {
            'networks': networks,
            'timestamp': datetime.now().isoformat(),
            'count': len(networks)
        })
        
    except Exception as e:
        print(f"❌ Scan error: {e}")
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    import os
    
    # Get port from environment variable (for deployment) or use 3000
    port = int(os.environ.get('PORT', 3000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("\n" + "="*70)
    print("📡 Server Configuration:")
    print(f"   URL: http://localhost:{port}")
    print(f"   Mode: Threading (no eventlet)")
    print(f"   WiFi Scanner: ✅ Ready")
    print("="*70)
    print("\n🚀 Starting server...")
    print("⚠️  KEEP THIS WINDOW OPEN while using the application!")
    print("="*70 + "\n")
    
    try:
        socketio.run(app, host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n⏹️  Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
