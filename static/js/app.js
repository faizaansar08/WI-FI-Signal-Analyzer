/**
 * Wi-Fi Signal Analyzer - Frontend JavaScript
 * Real-time monitoring with Socket.IO and Chart.js visualization
 */

// Global variables
let socket;
let signalChart;
let selectedNetwork = null;
let isMonitoring = false;
let chartData = {
    labels: [],
    datasets: [{
        label: 'Signal Strength (dBm)',
        data: [],
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        borderWidth: 2,
        tension: 0.4,
        fill: true
    }]
};
const MAX_CHART_POINTS = 20;

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Wi-Fi Signal Analyzer...');
    
    initializeSocketIO();
    initializeChart();
    initializeEventListeners();
});

/**
 * Initialize Socket.IO connection
 */
function initializeSocketIO() {
    console.log('🔌 Connecting to Socket.IO server on port 3000...');
    
    socket = io('http://localhost:3000', {
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
    });
    
    // Connection events
    socket.on('connect', function() {
        console.log('✅ Connected to server');
        updateConnectionStatus(true);
        showNotification('Connected to server', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('❌ Disconnected from server');
        updateConnectionStatus(false);
        showNotification('Disconnected from server', 'error');
    });
    
    socket.on('connect_error', function(error) {
        console.error('Connection error:', error);
        updateConnectionStatus(false);
    });
    
    // Data events
    socket.on('connection_status', function(data) {
        console.log('Connection status:', data);
    });
    
    socket.on('networks_update', function(data) {
        console.log('📶 Networks update:', data);
        displayNetworks(data.networks);
        updateStatistics(data);
    });
    
    socket.on('signal_update', function(data) {
        console.log('📡 Signal update:', data);
        updateCurrentSignal(data);
        updateChart(data);
    });
    
    socket.on('monitoring_status', function(data) {
        console.log('📊 Monitoring status:', data.status, data);
        if (data.status === 'started') {
            isMonitoring = true;
            updateMonitoringButtons(true);
            showNotification('✅ Monitoring started - Graph updating every 2 seconds', 'success');
        } else if (data.status === 'stopped') {
            isMonitoring = false;
            updateMonitoringButtons(false);
            showNotification('Monitoring stopped', 'info');
        } else if (data.status === 'network_selected') {
            console.log('Network selected:', data.selected_network);
        }
    });
    
    socket.on('error', function(data) {
        console.error('Error:', data.message);
        showNotification(data.message, 'error');
    });
}

/**
 * Initialize Chart.js
 */
function initializeChart() {
    const ctx = document.getElementById('signalChart').getContext('2d');
    
    signalChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,  // Changed to false to fill container
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: '#ffffff'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    callbacks: {
                        label: function(context) {
                            return `Signal: ${context.parsed.y} dBm`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time',
                        color: '#b0b0b0'
                    },
                    ticks: {
                        color: '#b0b0b0'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Signal Strength (dBm)',
                        color: '#b0b0b0'
                    },
                    ticks: {
                        color: '#b0b0b0'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    min: -100,
                    max: -20
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

/**
 * Initialize event listeners for buttons
 */
function initializeEventListeners() {
    document.getElementById('scanBtn').addEventListener('click', scanNetworks);
    document.getElementById('startMonitoringBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopMonitoringBtn').addEventListener('click', stopMonitoring);
    document.getElementById('refreshBtn').addEventListener('click', refreshData);
}

/**
 * Scan for WiFi networks
 */
function scanNetworks() {
    console.log('🔍 Scanning networks...');
    socket.emit('scan_once');
    showNotification('Scanning for networks...', 'info');
}

/**
 * Start continuous monitoring
 */
function startMonitoring() {
    console.log('▶️ Starting monitoring...');
    const data = selectedNetwork ? { ssid: selectedNetwork } : {};
    socket.emit('start_monitoring', data);
}

/**
 * Stop monitoring
 */
function stopMonitoring() {
    console.log('⏹️ Stopping monitoring...');
    socket.emit('stop_monitoring');
}

/**
 * Refresh data
 */
function refreshData() {
    console.log('🔄 Refreshing data...');
    chartData.labels = [];
    chartData.datasets[0].data = [];
    signalChart.update();
    scanNetworks();
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    const dotElement = statusElement.querySelector('.status-dot');
    const textElement = statusElement.querySelector('.status-text');
    
    if (connected) {
        dotElement.classList.add('connected');
        textElement.textContent = 'Connected';
    } else {
        dotElement.classList.remove('connected');
        textElement.textContent = 'Disconnected';
    }
}

/**
 * Display available networks
 */
function displayNetworks(networks) {
    console.log('📋 Displaying networks:', networks);
    const container = document.getElementById('networksContainer');
    const countElement = document.getElementById('networkCount');
    
    if (!networks || networks.length === 0) {
        console.log('⚠️ No networks to display');
        container.innerHTML = `
            <div class="no-networks">
                <i class="fas fa-wifi"></i>
                <p>No networks found. Click "Scan Networks" to search again.</p>
            </div>
        `;
        countElement.textContent = '0 networks';
        return;
    }
    
    console.log(`✅ Found ${networks.length} network(s)`);
    
    // Sort by signal strength
    networks.sort((a, b) => b.signal_strength - a.signal_strength);
    
    const networksHTML = networks.map(network => {
        console.log('  - Network:', network.ssid, network.signal_strength, 'dBm');
        return `
        <div class="network-item ${selectedNetwork === network.ssid ? 'selected' : ''}" 
             onclick="selectNetwork('${network.ssid.replace(/'/g, "\\'")}')">
            <div class="network-info">
                <div class="network-ssid">
                    <i class="fas fa-wifi"></i> ${network.ssid}
                </div>
                <div class="network-details">
                    <span><i class="fas fa-signal"></i> ${network.signal_strength} dBm</span>
                    <span><i class="fas fa-broadcast-tower"></i> ${network.frequency}</span>
                    <span><i class="fas fa-shield-alt"></i> ${network.security}</span>
                </div>
            </div>
            <div class="network-signal">
                <div class="signal-bar">
                    <div class="signal-fill" style="width: ${network.signal_quality}%; background: ${getSignalColor(network.signal_quality)}"></div>
                </div>
                <span class="signal-value" style="color: ${getSignalColor(network.signal_quality)}">
                    ${network.signal_quality}%
                </span>
            </div>
        </div>
    `;
    }).join('');
    
    console.log('📝 Setting innerHTML with', networks.length, 'networks');
    container.innerHTML = networksHTML;
    countElement.textContent = `${networks.length} network${networks.length !== 1 ? 's' : ''}`;
    console.log('✅ Networks displayed successfully');
}

/**
 * Select a network for monitoring
 */
function selectNetwork(ssid) {
    console.log('🎯 Selecting network:', ssid);
    selectedNetwork = ssid;
    socket.emit('select_network', { ssid: ssid });
    
    // Update UI
    document.querySelectorAll('.network-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.target.closest('.network-item').classList.add('selected');
    
    showNotification(`Selected network: ${ssid}`, 'success');
    
    // Automatically start monitoring when network is selected
    if (isMonitoring) {
        console.log('🔄 Restarting monitoring with new network...');
        stopMonitoring();
        setTimeout(() => startMonitoring(), 500);
    } else {
        console.log('▶️ Auto-starting monitoring...');
        setTimeout(() => startMonitoring(), 300);
    }
}

/**
 * Update current signal display
 */
function updateCurrentSignal(data) {
    const percentage = data.signal_quality;
    
    // Update circle
    const circle = document.querySelector('.signal-circle');
    circle.style.setProperty('--signal-percent', percentage);
    
    document.getElementById('signalPercentage').textContent = `${percentage}%`;
    document.getElementById('currentSSID').textContent = data.ssid || 'N/A';
    document.getElementById('currentStrength').textContent = `${data.signal_strength} dBm`;
    document.getElementById('currentFrequency').textContent = data.frequency || 'N/A';
    document.getElementById('currentChannel').textContent = data.channel || 'N/A';
    document.getElementById('currentSecurity').textContent = data.security || 'N/A';
    
    // Update status badge
    const status = getSignalStatus(percentage);
    const statusBadge = document.getElementById('statusBadge');
    statusBadge.innerHTML = `<span class="badge badge-${status.class}">${status.text}</span>`;
    
    // Update circle color
    circle.style.background = `conic-gradient(
        ${getSignalColor(percentage)} 0deg,
        ${getSignalColor(percentage)} ${percentage * 3.6}deg,
        rgba(255, 255, 255, 0.1) ${percentage * 3.6}deg
    )`;
}

/**
 * Update chart with new data point
 */
function updateChart(data) {
    const time = new Date().toLocaleTimeString();
    
    chartData.labels.push(time);
    chartData.datasets[0].data.push(data.signal_strength);
    
    // Keep only last MAX_CHART_POINTS points
    if (chartData.labels.length > MAX_CHART_POINTS) {
        chartData.labels.shift();
        chartData.datasets[0].data.shift();
    }
    
    signalChart.update('none'); // Update without animation for performance
    
    // Update data points stat
    document.getElementById('dataPoints').textContent = chartData.labels.length;
}

/**
 * Update statistics panel
 */
function updateStatistics(data) {
    document.getElementById('totalNetworks').textContent = data.count || 0;
    document.getElementById('lastUpdate').textContent = new Date(data.timestamp).toLocaleTimeString();
    
    if (data.networks && data.networks.length > 0) {
        const avgSignal = data.networks.reduce((sum, n) => sum + n.signal_strength, 0) / data.networks.length;
        document.getElementById('avgSignal').textContent = `${avgSignal.toFixed(1)} dBm`;
    }
}

/**
 * Update monitoring button states
 */
function updateMonitoringButtons(monitoring) {
    document.getElementById('startMonitoringBtn').disabled = monitoring;
    document.getElementById('stopMonitoringBtn').disabled = !monitoring;
}

/**
 * Get signal color based on quality percentage
 */
function getSignalColor(quality) {
    if (quality >= 80) return '#4CAF50'; // Excellent
    if (quality >= 60) return '#8BC34A'; // Good
    if (quality >= 40) return '#FFC107'; // Fair
    return '#FF5722'; // Poor
}

/**
 * Get signal status text and class
 */
function getSignalStatus(quality) {
    if (quality >= 80) return { text: 'Excellent', class: 'excellent' };
    if (quality >= 60) return { text: 'Good', class: 'good' };
    if (quality >= 40) return { text: 'Fair', class: 'fair' };
    return { text: 'Poor', class: 'poor' };
}

/**
 * Show notification (simple toast)
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 25px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 300px;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Add CSS animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

console.log('✅ Wi-Fi Signal Analyzer initialized');
