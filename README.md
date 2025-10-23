# 🌐 Wi-Fi Signal Strength Analyzer

A real-time Wi-Fi signal strength monitoring and visualization application with a beautiful web dashboard.

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

### Backend (Flask + SocketIO)
- 🔄 **Real-time Communication**: WebSocket-based live updates using Socket.IO
- 📡 **WiFi Scanner**: Cross-platform WiFi signal detection (Windows/Linux/macOS)
- 🎯 **REST API Endpoints**: `/api/signal` and `/api/predict` for signal data
- 🔌 **Background Monitoring**: Continuous signal strength tracking
- 🛡️ **Error Handling**: Robust error management and fallback mechanisms

### Frontend (HTML/CSS/JavaScript)
- 📊 **Live Dashboard**: Beautiful, responsive UI with real-time updates
- 📈 **Signal Graph**: Interactive Chart.js visualization of signal history
- 🎨 **Modern Design**: Dark theme with smooth animations
- 📱 **Responsive**: Works on desktop and mobile devices
- 🌈 **Color-coded Signals**: Visual indicators for signal quality (Excellent/Good/Fair/Poor)

### Key Capabilities
- ✅ Real-time WiFi signal strength monitoring
- ✅ Multiple network detection and comparison
- ✅ Signal quality percentage calculation
- ✅ Historical signal strength timeline (last 20 data points)
- ✅ Network selection for focused monitoring
- ✅ Frequency, channel, and security information
- ✅ Statistics dashboard with averages and counts

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Administrator/sudo privileges (for WiFi scanning on some systems)

### Installation

1. **Clone or navigate to the project directory:**
```powershell
cd "d:\cn project"
```

2. **Install dependencies:**
```powershell
pip install -r requirements.txt
```

### Running the Application

#### Option 1: Using the Startup Script (Recommended)
```powershell
.\start.ps1
```

#### Option 2: Manual Start
```powershell
python app.py
```

3. **Open your browser:**
   - Navigate to: `http://localhost:5000`
   - The dashboard will load automatically

## 📖 Usage Guide

### Dashboard Controls

1. **Scan Networks**
   - Click "Scan Networks" to discover available WiFi networks
   - Networks are displayed sorted by signal strength

2. **Start Monitoring**
   - Select a network from the list (optional)
   - Click "Start Monitoring" for continuous real-time updates
   - Signal graph will update every 2 seconds

3. **Stop Monitoring**
   - Click "Stop Monitoring" to pause real-time updates

4. **Refresh**
   - Click "Refresh" to clear the graph and rescan networks

### Dashboard Components

#### 1. Current Signal Display
- **Signal Circle**: Visual representation of signal quality (0-100%)
- **Network Details**: SSID, strength (dBm), frequency, channel, security
- **Status Badge**: Color-coded quality indicator

#### 2. Signal Strength Timeline
- **Live Graph**: Real-time Chart.js line graph
- **X-axis**: Time stamps
- **Y-axis**: Signal strength in dBm (-100 to -20)
- **History**: Last 20 data points

#### 3. Available Networks List
- **Network Cards**: All detected WiFi networks
- **Signal Bars**: Visual quality indicators
- **Click to Select**: Choose a network for focused monitoring

#### 4. Statistics Panel
- **Average Signal**: Mean signal strength across all networks
- **Networks Found**: Total count of detected networks
- **Last Update**: Timestamp of most recent scan
- **Data Points**: Number of points in the graph

## 🔌 API Documentation

### REST Endpoints

#### GET `/api/signal`
Get current WiFi signal strength for all networks.

**Response:**
```json
{
  "success": true,
  "networks": [
    {
      "ssid": "Home_WiFi_5G",
      "signal_strength": -45,
      "signal_quality": 75,
      "frequency": "5 GHz (Ch 36)",
      "channel": 36,
      "security": "WPA2"
    }
  ],
  "timestamp": "2025-10-22T10:30:00.000Z",
  "count": 6
}
```

#### POST `/api/predict`
Predict signal quality based on input data.

**Request:**
```json
{
  "ssid": "MyNetwork",
  "signal_strength": -50
}
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "ssid": "MyNetwork",
    "signal_strength": -50,
    "signal_quality": 67,
    "status": "Good",
    "recommendation": "Good connection. Suitable for most online activities.",
    "timestamp": "2025-10-22T10:30:00.000Z"
  }
}
```

### SocketIO Events

#### Client → Server

| Event | Data | Description |
|-------|------|-------------|
| `start_monitoring` | `{ssid: "optional"}` | Start continuous monitoring |
| `stop_monitoring` | `{}` | Stop monitoring |
| `select_network` | `{ssid: "network_name"}` | Select specific network |
| `scan_once` | `{}` | Perform single scan |

#### Server → Client

| Event | Data | Description |
|-------|------|-------------|
| `connection_status` | `{status, message}` | Connection confirmation |
| `networks_update` | `{networks, timestamp, count}` | All available networks |
| `signal_update` | `{ssid, signal_strength, ...}` | Selected network update |
| `monitoring_status` | `{status, message}` | Monitoring state change |
| `error` | `{message}` | Error notification |

## 📁 Project Structure

```
d:\cn project\
│
├── app.py                      # Main Flask application
├── wifi_scanner.py             # WiFi scanning module
├── requirements.txt            # Python dependencies
├── start.ps1                   # PowerShell startup script
├── README.md                   # This file
│
├── templates/
│   └── index.html              # Main dashboard HTML
│
└── static/
    ├── css/
    │   └── style.css           # Dashboard styles
    └── js/
        └── app.js              # Frontend JavaScript + SocketIO
```

## 🛠️ Technical Details

### Backend Stack
- **Flask**: Web framework
- **Flask-SocketIO**: WebSocket support
- **Flask-CORS**: Cross-origin resource sharing
- **psutil**: System utilities (optional)
- **eventlet**: Async networking

### Frontend Stack
- **Socket.IO Client**: Real-time bidirectional communication
- **Chart.js**: Data visualization
- **Font Awesome**: Icons
- **Vanilla JavaScript**: No framework dependencies

### WiFi Scanning Methods

#### Windows
```powershell
netsh wlan show networks mode=Bssid
```

#### Linux
```bash
nmcli dev wifi
# or
iwlist wlan0 scan
```

#### macOS
```bash
/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -s
```

## 📊 Signal Quality Calculation

Signal strength is measured in **dBm** (decibel-milliwatts):

| Range | Quality | Status | Description |
|-------|---------|--------|-------------|
| -30 to -50 dBm | 80-100% | 🟢 Excellent | Perfect for all activities |
| -50 to -60 dBm | 60-80% | 🟡 Good | Suitable for most activities |
| -60 to -70 dBm | 40-60% | 🟠 Fair | May experience slowdowns |
| -70 to -90 dBm | 0-40% | 🔴 Poor | Limited connectivity |

## 🔧 Troubleshooting

### Issue: No Networks Found
**Solution:**
- Run as Administrator (Windows) or with sudo (Linux/macOS)
- Check if WiFi adapter is enabled
- Verify network drivers are installed

### Issue: Connection Failed
**Solution:**
- Ensure port 5000 is not in use
- Check firewall settings
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Issue: Mock Data Displayed
**Solution:**
- This is normal if WiFi scanning fails
- The app uses simulated data for testing
- Fix WiFi scanning permissions to get real data

### Issue: Chart Not Updating
**Solution:**
- Check browser console for JavaScript errors
- Verify Socket.IO connection (green status dot)
- Click "Refresh" to reset the connection

## 🎯 Use Cases

1. **Network Optimization**: Find the best WiFi router placement
2. **Troubleshooting**: Diagnose connectivity issues
3. **Coverage Mapping**: Identify dead zones in your space
4. **Network Comparison**: Compare signal strength across multiple networks
5. **Real-time Monitoring**: Track signal stability over time

## 🔐 Security Notes

- The application runs locally on your machine
- No data is sent to external servers
- WiFi passwords are NOT collected or displayed
- Only publicly available network information is shown

## 🚀 Future Enhancements

- [ ] Heatmap visualization for signal coverage
- [ ] Export data to CSV/JSON
- [ ] Signal prediction using ML models
- [ ] Mobile app version
- [ ] Network speed testing
- [ ] Multi-language support
- [ ] Dark/Light theme toggle

## 📝 License

This project is open source and available under the MIT License.

## 👥 Credits

Developed as part of a Computer Networks project for Wi-Fi signal analysis and visualization.

## 📞 Support

If you encounter any issues or have questions:
1. Check the Troubleshooting section above
2. Review the browser console for errors
3. Verify all dependencies are installed correctly

---

**Enjoy monitoring your Wi-Fi signals! 📶✨**
