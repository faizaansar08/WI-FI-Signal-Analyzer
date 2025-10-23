/**
 * Wi-Fi Signal Analyzer - MULTI-NETWORK VERSION
 * Monitor multiple WiFi networks simultaneously with individual graphs
 */

// Global variables
let socket;
let selectedNetworks = new Map(); // Map of ssid -> {chart, data}
let isMonitoring = false;
const MAX_CHART_POINTS = 30;

// Chart colors for different networks
const CHART_COLORS = [
    { border: '#2196F3', bg: 'rgba(33, 150, 243, 0.1)' },
    { border: '#4CAF50', bg: 'rgba(76, 175, 80, 0.1)' },
    { border: '#FF9800', bg: 'rgba(255, 152, 0, 0.1)' },
    { border: '#9C27B0', bg: 'rgba(156, 39, 176, 0.1)' },
    { border: '#F44336', bg: 'rgba(244, 67, 54, 0.1)' },
    { border: '#00BCD4', bg: 'rgba(0, 188, 212, 0.1)' },
    { border: '#FFEB3B', bg: 'rgba(255, 235, 59, 0.2)' },
    { border: '#795548', bg: 'rgba(121, 85, 72, 0.1)' }
];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Initializing Multi-Network Wi-Fi Analyzer...');
    
    initializeSocketIO();
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
    
    socket.on('networks_update', function(data) {
        console.log('📶 Networks update:', data.count, 'networks');
        displayNetworks(data.networks);
        updateStatistics(data);
    });
    
    socket.on('signal_update', function(data) {
        console.log('📡 Signal update for:', data.ssid);
        updateNetworkData(data);
    });
    
    socket.on('monitoring_status', function(data) {
        console.log('📊 Monitoring status:', data.status);
        if (data.status === 'started') {
            isMonitoring = true;
            updateMonitoringButtons(true);
            showNotification(`✅ Monitoring ${data.selected_networks?.length || 0} network(s)`, 'success');
        } else if (data.status === 'stopped') {
            isMonitoring = false;
            updateMonitoringButtons(false);
            showNotification('Monitoring stopped', 'info');
        }
    });
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    document.getElementById('scanBtn').addEventListener('click', scanNetworks);
    document.getElementById('startMonitoringBtn').addEventListener('click', startMonitoring);
    document.getElementById('stopMonitoringBtn').addEventListener('click', stopMonitoring);
    document.getElementById('refreshBtn').addEventListener('click', scanNetworks);
}

/**
 * Scan for networks
 */
function scanNetworks() {
    console.log('🔍 Scanning networks...');
    socket.emit('scan_once');
    showNotification('Scanning for networks...', 'info');
}

/**
 * Start monitoring selected networks
 */
function startMonitoring() {
    if (selectedNetworks.size === 0) {
        showNotification('Please select at least one network to monitor', 'warning');
        return;
    }
    
    const networks = Array.from(selectedNetworks.keys());
    console.log('▶️ Starting monitoring for:', networks);
    
    socket.emit('start_monitoring', { networks: networks });
}

/**
 * Stop monitoring
 */
function stopMonitoring() {
    console.log('⏹️ Stopping monitoring');
    socket.emit('stop_monitoring');
}

/**
 * Display available networks
 */
function displayNetworks(networks) {
    const container = document.getElementById('networksContainer');
    const networkCount = document.getElementById('networkCount');
    
    if (!networks || networks.length === 0) {
        container.innerHTML = `
            <div class="no-networks">
                <i class="fas fa-wifi"></i>
                <p>No networks found. Click "Scan Networks" to search.</p>
            </div>`;
        networkCount.textContent = '0 networks';
        return;
    }
    
    networkCount.textContent = `${networks.length} ${networks.length === 1 ? 'network' : 'networks'}`;
    
    container.innerHTML = networks.map(network => {
        const isSelected = selectedNetworks.has(network.ssid);
        const signalClass = getSignalClass(network.signal_quality);
        
        return `
            <div class="network-item ${isSelected ? 'selected' : ''}" 
                 data-ssid="${network.ssid}"
                 onclick="toggleNetworkSelection('${network.ssid.replace(/'/g, "\\'")}')">
                <div class="network-info">
                    <div class="network-name">
                        <i class="fas fa-wifi"></i>
                        <strong>${network.ssid}</strong>
                        ${isSelected ? '<span class="badge badge-success"><i class="fas fa-check"></i> Monitoring</span>' : ''}
                    </div>
                    <div class="network-details">
                        <span><i class="fas fa-signal"></i> ${network.signal_strength} dBm</span>
                        <span><i class="fas fa-broadcast-tower"></i> ${network.frequency}</span>
                        <span><i class="fas fa-lock"></i> ${network.security}</span>
                    </div>
                </div>
                <div class="network-signal">
                    <div class="signal-bar-container">
                        <div class="signal-bar ${signalClass}" style="width: ${network.signal_quality}%"></div>
                    </div>
                    <div class="signal-percentage">${network.signal_quality}%</div>
                </div>
            </div>`;
    }).join('');
}

/**
 * Toggle network selection for monitoring
 */
function toggleNetworkSelection(ssid) {
    if (selectedNetworks.has(ssid)) {
        // Deselect network
        selectedNetworks.delete(ssid);
        removeNetworkChart(ssid);
        console.log('❌ Deselected:', ssid);
    } else {
        // Select network
        addNetworkChart(ssid);
        console.log('✅ Selected:', ssid);
    }
    
    // Update UI
    const networkItem = document.querySelector(`[data-ssid="${ssid}"]`);
    if (networkItem) {
        networkItem.classList.toggle('selected');
    }
    
    // Notify server if monitoring is active
    if (isMonitoring) {
        socket.emit('select_network', { 
            ssid: ssid, 
            action: 'toggle' 
        });
    }
}

/**
 * Add chart for a network
 */
function addNetworkChart(ssid) {
    const chartsContainer = document.getElementById('chartsContainer') || createChartsContainer();
    const colorIndex = selectedNetworks.size % CHART_COLORS.length;
    const colors = CHART_COLORS[colorIndex];
    
    // Create chart container
    const chartDiv = document.createElement('div');
    chartDiv.className = 'card graph-container';
    chartDiv.id = `chart-${ssid.replace(/[^a-zA-Z0-9]/g, '_')}`;
    chartDiv.innerHTML = `
        <div class="card-header">
            <h3><i class="fas fa-chart-line"></i> ${ssid}</h3>
            <button class="btn-close" onclick="toggleNetworkSelection('${ssid.replace(/'/g, "\\'")}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div class="card-body">
            <canvas id="canvas-${ssid.replace(/[^a-zA-Z0-9]/g, '_')}"></canvas>
        </div>`;
    
    chartsContainer.appendChild(chartDiv);
    
    // Initialize chart
    const canvas = chartDiv.querySelector('canvas');
    const ctx = canvas.getContext('2d');
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: `${ssid} Signal (dBm)`,
                data: [],
                borderColor: colors.border,
                backgroundColor: colors.bg,
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: -90,
                    max: -30,
                    title: {
                        display: true,
                        text: 'Signal Strength (dBm)'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            },
            animation: {
                duration: 300
            }
        }
    });
    
    selectedNetworks.set(ssid, { chart: chart, data: [] });
}

/**
 * Remove chart for a network
 */
function removeNetworkChart(ssid) {
    const chartData = selectedNetworks.get(ssid);
    if (chartData) {
        chartData.chart.destroy();
        selectedNetworks.delete(ssid);
        
        const chartDiv = document.getElementById(`chart-${ssid.replace(/[^a-zA-Z0-9]/g, '_')}`);
        if (chartDiv) {
            chartDiv.remove();
        }
    }
}

/**
 * Create charts container if it doesn't exist
 */
function createChartsContainer() {
    let container = document.getElementById('chartsContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'chartsContainer';
        container.className = 'charts-grid';
        
        const dashboard = document.querySelector('.dashboard');
        const networksCard = document.querySelector('.networks-list');
        dashboard.insertBefore(container, networksCard);
    }
    return container;
}

/**
 * Update network data (from signal_update event)
 */
function updateNetworkData(data) {
    const networkData = selectedNetworks.get(data.ssid);
    if (!networkData) return;
    
    const time = new Date().toLocaleTimeString();
    const chart = networkData.chart;
    
    // Add new data point
    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(data.signal_strength);
    
    // Keep only last MAX_CHART_POINTS
    if (chart.data.labels.length > MAX_CHART_POINTS) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    
    chart.update('none'); // Update without animation for smoothness
}

/**
 * Update statistics
 */
function updateStatistics(data) {
    document.getElementById('totalNetworks').textContent = data.count || 0;
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
    
    const dataPointsTotal = Array.from(selectedNetworks.values())
        .reduce((sum, net) => sum + net.chart.data.labels.length, 0);
    document.getElementById('dataPoints').textContent = dataPointsTotal;
}

/**
 * Update connection status
 */
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connectionStatus');
    const statusDot = statusElement.querySelector('.status-dot');
    const statusText = statusElement.querySelector('.status-text');
    
    if (connected) {
        statusDot.style.backgroundColor = '#4CAF50';
        statusText.textContent = 'Connected';
        statusElement.classList.add('connected');
    } else {
        statusDot.style.backgroundColor = '#F44336';
        statusText.textContent = 'Disconnected';
        statusElement.classList.remove('connected');
    }
}

/**
 * Update monitoring buttons
 */
function updateMonitoringButtons(monitoring) {
    document.getElementById('startMonitoringBtn').disabled = monitoring;
    document.getElementById('stopMonitoringBtn').disabled = !monitoring;
}

/**
 * Get signal strength class
 */
function getSignalClass(quality) {
    if (quality >= 70) return 'signal-excellent';
    if (quality >= 50) return 'signal-good';
    if (quality >= 30) return 'signal-fair';
    return 'signal-poor';
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Make functions globally accessible
window.toggleNetworkSelection = toggleNetworkSelection;
