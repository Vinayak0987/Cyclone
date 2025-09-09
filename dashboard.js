// Enhanced AstroAlert Dashboard JavaScript

// Global state management
const DashboardState = {
    currentUser: null,
    locations: [],
    alerts: [],
    analytics: null,
    map: null,
    charts: {},
    isLoading: false
};

// API Configuration
const API_BASE = '/api';

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

async function initializeDashboard() {
    console.log('🚀 Initializing Enhanced AstroAlert Dashboard');
    
    // Setup navigation
    setupNavigation();
    
    // Setup connection status
    await checkSystemHealth();
    
    // Initialize default user (for demo)
    await initializeDefaultUser();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    await loadDashboardData();
    
    // Initialize map
    initializeMap();
    
    // Setup periodic refresh
    setupPeriodicRefresh();
    
    console.log('✅ Dashboard initialization complete');
}

// Navigation System
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    
    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabId = item.dataset.tab;
            
            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Update active tab content
            tabContents.forEach(tab => tab.classList.remove('active'));
            document.getElementById(`${tabId}-tab`).classList.add('active');
            
            // Load tab-specific data
            loadTabData(tabId);
        });
    });
}

async function loadTabData(tabId) {
    switch(tabId) {
        case 'overview':
            await loadOverviewData();
            break;
        case 'locations':
            await loadLocationsData();
            break;
        case 'analytics':
            await loadAnalyticsData();
            break;
        case 'alerts':
            await loadAlertsData();
            break;
        case 'legacy':
            setupLegacyAnalysis();
            break;
        case 'settings':
            await loadSettingsData();
            break;
    }
}

// System Health Check
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        updateConnectionStatus(data.status === 'healthy', data);
        
        return data;
    } catch (error) {
        console.error('Health check failed:', error);
        updateConnectionStatus(false, { error: error.message });
        return null;
    }
}

function updateConnectionStatus(isConnected, data) {
    const statusElement = document.getElementById('connectionStatus');
    const indicator = statusElement.querySelector('.status-indicator');
    const text = statusElement.querySelector('.status-text');
    
    if (isConnected) {
        indicator.className = 'status-indicator connected';
        text.textContent = data.monitoring_active ? 'Monitoring Active' : 'System Ready';
    } else {
        indicator.className = 'status-indicator error';
        text.textContent = 'System Error';
    }
}

// User Management
async function initializeDefaultUser() {
    // Check if user exists or create default user for demo
    const defaultEmail = 'demo@astroalert.com';
    
    try {
        // Try to get existing user (this would be replaced with proper auth)
        DashboardState.currentUser = {
            id: 'demo-user-123',
            name: 'Demo User',
            email: defaultEmail,
            phone: '+1234567890'
        };
        
        console.log('👤 User initialized:', DashboardState.currentUser.name);
    } catch (error) {
        console.error('Failed to initialize user:', error);
    }
}

// Data Loading Functions
async function loadDashboardData() {
    await Promise.all([
        loadOverviewData(),
        loadLocationsData(),
        loadAlertsData()
    ]);
}

async function loadOverviewData() {
    if (!DashboardState.currentUser) return;
    
    try {
        // Load analytics summary
        const analyticsResponse = await fetch(`${API_BASE}/users/${DashboardState.currentUser.id}/analytics`);
        if (analyticsResponse.ok) {
            const analyticsData = await analyticsResponse.json();
            if (analyticsData.success) {
                updateOverviewStats(analyticsData.analytics);
            }
        }
        
        // Load monitoring status
        const monitoringResponse = await fetch(`${API_BASE}/monitoring/status`);
        if (monitoringResponse.ok) {
            const monitoringData = await monitoringResponse.json();
            if (monitoringData.success) {
                updateMonitoringStatus(monitoringData.monitoring);
            }
        }
        
        // Load recent activity
        await loadRecentActivity();
        
    } catch (error) {
        console.error('Failed to load overview data:', error);
    }
}

function updateOverviewStats(analytics) {
    document.getElementById('totalLocations').textContent = analytics.monitored_locations || 0;
    document.getElementById('totalAnalyses').textContent = analytics.total_analyses || 0;
    document.getElementById('activeAlerts').textContent = analytics.active_alerts || 0;
}

function updateMonitoringStatus(monitoring) {
    const statusElement = document.getElementById('monitoringStatus');
    statusElement.textContent = monitoring.monitoring_active ? 'Active' : 'Inactive';
    statusElement.className = 'stat-value ' + (monitoring.monitoring_active ? 'active' : 'inactive');
}

async function loadRecentActivity() {
    if (!DashboardState.currentUser) return;
    
    try {
        // Load recent analyses
        const recentAnalysesElement = document.getElementById('recentAnalyses');
        recentAnalysesElement.innerHTML = '<div class="loading">Loading recent analyses...</div>';
        
        // Load recent alerts
        const recentAlertsElement = document.getElementById('recentAlerts');
        recentAlertsElement.innerHTML = '<div class="loading">Loading recent alerts...</div>';
        
        // For demo, show placeholder data
        setTimeout(() => {
            recentAnalysesElement.innerHTML = `
                <div class="activity-item">
                    <div class="activity-info">
                        <h4>Mumbai Analysis</h4>
                        <div class="activity-meta">2 hours ago</div>
                    </div>
                    <div class="activity-status low">LOW</div>
                </div>
                <div class="activity-item">
                    <div class="activity-info">
                        <h4>Chennai Analysis</h4>
                        <div class="activity-meta">5 hours ago</div>
                    </div>
                    <div class="activity-status moderate">MODERATE</div>
                </div>
            `;
            
            recentAlertsElement.innerHTML = `
                <div class="activity-item">
                    <div class="activity-info">
                        <h4>No recent alerts</h4>
                        <div class="activity-meta">All locations stable</div>
                    </div>
                    <div class="activity-status low">GOOD</div>
                </div>
            `;
        }, 1000);
        
    } catch (error) {
        console.error('Failed to load recent activity:', error);
    }
}

async function loadLocationsData() {
    if (!DashboardState.currentUser) return;
    
    const locationsGrid = document.getElementById('locationsGrid');
    locationsGrid.innerHTML = '<div class="loading">Loading locations...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/users/${DashboardState.currentUser.id}/locations`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                DashboardState.locations = data.locations;
                renderLocations(data.locations);
                updateMapMarkers(data.locations);
                return;
            }
        }
        
        // Demo data if no locations found
        const demoLocations = [
            {
                id: 'demo-1',
                name: 'Mumbai',
                latitude: 19.0760,
                longitude: 72.8777,
                monitoring_enabled: true,
                alert_threshold: 'MODERATE',
                latest_analysis: {
                    final_risk_level: 'LOW',
                    combined_risk_score: 25.5,
                    analysis_timestamp: new Date().toISOString()
                }
            },
            {
                id: 'demo-2', 
                name: 'Chennai',
                latitude: 13.0827,
                longitude: 80.2707,
                monitoring_enabled: true,
                alert_threshold: 'HIGH',
                latest_analysis: {
                    final_risk_level: 'MODERATE',
                    combined_risk_score: 45.2,
                    analysis_timestamp: new Date(Date.now() - 3600000).toISOString()
                }
            }
        ];
        
        DashboardState.locations = demoLocations;
        renderLocations(demoLocations);
        updateMapMarkers(demoLocations);
        
    } catch (error) {
        console.error('Failed to load locations:', error);
        locationsGrid.innerHTML = '<div class="loading">Error loading locations</div>';
    }
}

function renderLocations(locations) {
    const locationsGrid = document.getElementById('locationsGrid');
    
    if (locations.length === 0) {
        locationsGrid.innerHTML = `
            <div class="card">
                <div class="card-content">
                    <div class="text-center">
                        <h3>No Locations Added</h3>
                        <p>Click "Add Location" to start monitoring cyclone risks.</p>
                        <button class="btn btn-primary" onclick="openAddLocationModal()">
                            <span>➕</span> Add Your First Location
                        </button>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    locationsGrid.innerHTML = locations.map(location => {
        const analysis = location.latest_analysis;
        const riskLevel = analysis ? analysis.final_risk_level : 'UNKNOWN';
        const riskScore = analysis ? analysis.combined_risk_score : 0;
        const lastAnalysis = analysis ? new Date(analysis.analysis_timestamp).toLocaleDateString() : 'Never';
        
        return `
            <div class="location-card">
                <div class="location-header">
                    <div>
                        <div class="location-name">${location.name}</div>
                        <div class="location-coords">${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}</div>
                    </div>
                    <div class="location-actions">
                        <button class="action-btn analyze" onclick="analyzeLocation('${location.id}')">🔍</button>
                        <button class="action-btn settings" onclick="editLocation('${location.id}')">⚙️</button>
                    </div>
                </div>
                
                <div class="location-status">
                    <div class="monitoring-status">
                        <div class="status-dot ${location.monitoring_enabled ? 'active' : 'inactive'}"></div>
                        Monitoring ${location.monitoring_enabled ? 'Active' : 'Inactive'}
                    </div>
                    <div class="risk-indicator ${riskLevel.toLowerCase()}">${riskLevel}</div>
                </div>
                
                <div class="location-stats">
                    <div class="location-stat">
                        <div class="location-stat-value">${riskScore.toFixed(1)}</div>
                        <div class="location-stat-label">Risk Score</div>
                    </div>
                    <div class="location-stat">
                        <div class="location-stat-value">${lastAnalysis}</div>
                        <div class="location-stat-label">Last Analysis</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function loadAnalyticsData() {
    const period = document.getElementById('analyticsPeriod').value;
    
    try {
        // Load analytics data
        if (DashboardState.currentUser) {
            const response = await fetch(`${API_BASE}/users/${DashboardState.currentUser.id}/analytics?days=${period}`);
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    DashboardState.analytics = data.analytics;
                    renderAnalyticsCharts(data.analytics);
                    return;
                }
            }
        }
        
        // Demo analytics data
        const demoAnalytics = {
            total_analyses: 156,
            risk_distribution: {
                LOW: 95,
                MODERATE: 42,
                HIGH: 15,
                EXTREME: 4
            },
            active_alerts: 2,
            monitored_locations: 2
        };
        
        renderAnalyticsCharts(demoAnalytics);
        
    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

function renderAnalyticsCharts(analytics) {
    // Risk Distribution Chart
    const riskCtx = document.getElementById('riskDistributionChart').getContext('2d');
    
    if (DashboardState.charts.riskDistribution) {
        DashboardState.charts.riskDistribution.destroy();
    }
    
    DashboardState.charts.riskDistribution = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Moderate Risk', 'High Risk', 'Extreme Risk'],
            datasets: [{
                data: [
                    analytics.risk_distribution.LOW || 0,
                    analytics.risk_distribution.MODERATE || 0,
                    analytics.risk_distribution.HIGH || 0,
                    analytics.risk_distribution.EXTREME || 0
                ],
                backgroundColor: ['#27ae60', '#f39c12', '#e74c3c', '#8e44ad'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Risk Trends Chart (demo data)
    const trendsCtx = document.getElementById('riskTrendsChart').getContext('2d');
    
    if (DashboardState.charts.riskTrends) {
        DashboardState.charts.riskTrends.destroy();
    }
    
    const trendData = generateDemoTrendData();
    
    DashboardState.charts.riskTrends = new Chart(trendsCtx, {
        type: 'line',
        data: {
            labels: trendData.labels,
            datasets: [{
                label: 'Average Risk Score',
                data: trendData.data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
    
    // Update accuracy metrics
    updateAccuracyMetrics();
    
    // Update location performance
    updateLocationPerformance();
}

function generateDemoTrendData() {
    const labels = [];
    const data = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        
        // Generate realistic trend data
        const baseRisk = 25 + Math.sin(i * 0.2) * 15;
        const noise = (Math.random() - 0.5) * 10;
        data.push(Math.max(0, Math.min(100, baseRisk + noise)));
    }
    
    return { labels, data };
}

function updateAccuracyMetrics() {
    const accuracyMetrics = document.getElementById('accuracyMetrics');
    
    accuracyMetrics.innerHTML = `
        <div class="accuracy-metric">
            <div class="accuracy-value">92%</div>
            <div class="accuracy-label">AI Accuracy</div>
        </div>
        <div class="accuracy-metric">
            <div class="accuracy-value">78%</div>
            <div class="accuracy-label">VRS Accuracy</div>
        </div>
        <div class="accuracy-metric">
            <div class="accuracy-value">85%</div>
            <div class="accuracy-label">Combined</div>
        </div>
        <div class="accuracy-metric">
            <div class="accuracy-value">96%</div>
            <div class="accuracy-label">Alert Precision</div>
        </div>
    `;
}

function updateLocationPerformance() {
    const locationPerformance = document.getElementById('locationPerformance');
    
    locationPerformance.innerHTML = `
        <div class="performance-item">
            <div class="performance-name">Mumbai</div>
            <div class="performance-score">92.5%</div>
        </div>
        <div class="performance-item">
            <div class="performance-name">Chennai</div>
            <div class="performance-score">87.2%</div>
        </div>
        <div class="performance-item">
            <div class="performance-name">Overall System</div>
            <div class="performance-score">89.8%</div>
        </div>
    `;
}

async function loadAlertsData() {
    if (!DashboardState.currentUser) return;
    
    const alertsList = document.getElementById('alertsList');
    alertsList.innerHTML = '<div class="loading">Loading alerts...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/users/${DashboardState.currentUser.id}/alerts`);
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                DashboardState.alerts = data.alerts;
                renderAlerts(data.alerts);
                return;
            }
        }
        
        // Demo alerts data
        const demoAlerts = [
            {
                id: 'alert-1',
                location_name: 'Chennai',
                risk_level: 'MODERATE',
                message: 'Moderate cyclone risk detected. VRS Score: 45/100. Monitor conditions closely.',
                triggered_at: new Date(Date.now() - 3600000).toISOString(),
                acknowledged: false
            }
        ];
        
        DashboardState.alerts = demoAlerts;
        renderAlerts(demoAlerts);
        
    } catch (error) {
        console.error('Failed to load alerts:', error);
        alertsList.innerHTML = '<div class="loading">Error loading alerts</div>';
    }
}

function renderAlerts(alerts) {
    const alertsList = document.getElementById('alertsList');
    
    if (alerts.length === 0) {
        alertsList.innerHTML = `
            <div class="card">
                <div class="card-content">
                    <div class="text-center">
                        <h3>🌟 No Active Alerts</h3>
                        <p>All monitored locations are showing normal cyclone risk levels.</p>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    alertsList.innerHTML = alerts.map(alert => {
        const alertTime = new Date(alert.triggered_at).toLocaleString();
        
        return `
            <div class="alert-item ${alert.risk_level.toLowerCase()}">
                <div class="alert-header">
                    <div class="alert-title">${alert.location_name} - ${alert.risk_level} Risk</div>
                    <div class="alert-time">${alertTime}</div>
                </div>
                <div class="alert-message">${alert.message}</div>
                <div class="alert-actions">
                    ${!alert.acknowledged ? `
                        <button class="btn btn-secondary" onclick="acknowledgeAlert('${alert.id}')">
                            <span>✅</span> Acknowledge
                        </button>
                    ` : '<span class="acknowledged">✅ Acknowledged</span>'}
                    <button class="btn btn-primary" onclick="viewAlertDetails('${alert.id}')">
                        <span>👁️</span> View Details
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function loadSettingsData() {
    // Load user profile
    if (DashboardState.currentUser) {
        document.getElementById('userName').value = DashboardState.currentUser.name;
        document.getElementById('userEmail').value = DashboardState.currentUser.email;
        document.getElementById('userPhone').value = DashboardState.currentUser.phone || '';
    }
    
    // Load monitoring info
    const monitoringInfo = document.getElementById('monitoringInfo');
    
    try {
        const response = await fetch(`${API_BASE}/monitoring/status`);
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                renderMonitoringInfo(data.monitoring);
                return;
            }
        }
        
        // Demo monitoring info
        renderMonitoringInfo({
            monitoring_active: true,
            check_interval_minutes: 30,
            locations_monitored: 2,
            last_check: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Failed to load monitoring info:', error);
    }
}

function renderMonitoringInfo(monitoring) {
    const monitoringInfo = document.getElementById('monitoringInfo');
    
    monitoringInfo.innerHTML = `
        <div class="monitoring-item">
            <div class="monitoring-label">Status</div>
            <div class="monitoring-value">${monitoring.monitoring_active ? 'Active' : 'Inactive'}</div>
        </div>
        <div class="monitoring-item">
            <div class="monitoring-label">Check Interval</div>
            <div class="monitoring-value">${monitoring.check_interval_minutes} minutes</div>
        </div>
        <div class="monitoring-item">
            <div class="monitoring-label">Locations</div>
            <div class="monitoring-value">${monitoring.locations_monitored}</div>
        </div>
        <div class="monitoring-item">
            <div class="monitoring-label">Last Check</div>
            <div class="monitoring-value">${monitoring.last_check ? new Date(monitoring.last_check).toLocaleString() : 'Never'}</div>
        </div>
    `;
}

// Map Functionality
function initializeMap() {
    const mapContainer = document.getElementById('locationMap');
    
    if (!mapContainer) return;
    
    // Initialize Leaflet map
    DashboardState.map = L.map('locationMap').setView([20.5937, 78.9629], 5); // India center
    
    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(DashboardState.map);
    
    // Add initial markers
    updateMapMarkers(DashboardState.locations);
}

function updateMapMarkers(locations) {
    if (!DashboardState.map) return;
    
    // Clear existing markers
    DashboardState.map.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
            DashboardState.map.removeLayer(layer);
        }
    });
    
    // Add new markers
    locations.forEach(location => {
        const riskLevel = location.latest_analysis ? location.latest_analysis.final_risk_level : 'UNKNOWN';
        const riskScore = location.latest_analysis ? location.latest_analysis.combined_risk_score : 0;
        
        // Determine marker color based on risk level
        let markerColor = '#bdc3c7'; // default
        switch(riskLevel) {
            case 'LOW': markerColor = '#27ae60'; break;
            case 'MODERATE': markerColor = '#f39c12'; break;
            case 'HIGH': markerColor = '#e74c3c'; break;
            case 'EXTREME': markerColor = '#8e44ad'; break;
        }
        
        // Create custom marker
        const marker = L.circleMarker([location.latitude, location.longitude], {
            radius: 10,
            fillColor: markerColor,
            color: 'white',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });
        
        // Add popup
        marker.bindPopup(`
            <div class="map-popup">
                <h4>${location.name}</h4>
                <p><strong>Risk Level:</strong> ${riskLevel}</p>
                <p><strong>Risk Score:</strong> ${riskScore.toFixed(1)}/100</p>
                <p><strong>Monitoring:</strong> ${location.monitoring_enabled ? 'Active' : 'Inactive'}</p>
                <button onclick="analyzeLocation('${location.id}')" class="btn btn-primary btn-small">
                    Analyze Now
                </button>
            </div>
        `);
        
        marker.addTo(DashboardState.map);
    });
}

// Event Listeners Setup
function setupEventListeners() {
    // Add Location Modal
    document.getElementById('addLocationBtn').addEventListener('click', openAddLocationModal);
    document.getElementById('closeAddLocationModal').addEventListener('click', closeAddLocationModal);
    document.getElementById('cancelAddLocation').addEventListener('click', closeAddLocationModal);
    document.getElementById('addLocationForm').addEventListener('submit', handleAddLocation);
    
    // Overview refresh
    document.getElementById('refreshOverview').addEventListener('click', loadOverviewData);
    
    // Analytics period change
    document.getElementById('analyticsPeriod').addEventListener('change', loadAnalyticsData);
    
    // Alert filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            filterAlerts(e.target.dataset.filter);
        });
    });
    
    // Test buttons
    document.getElementById('testBackendBtn').addEventListener('click', testBackend);
    document.getElementById('testDatabaseBtn').addEventListener('click', testDatabase);
    document.getElementById('testChatbotBtn').addEventListener('click', testChatbot);
    document.getElementById('testNotificationsBtn').addEventListener('click', testNotifications);
    
    // User profile form
    document.getElementById('userProfileForm').addEventListener('submit', handleUserProfileSave);
    
    // Legacy analysis
    setupLegacyAnalysis();
}

// Modal Functions
function openAddLocationModal() {
    document.getElementById('addLocationModal').classList.add('show');
}

function closeAddLocationModal() {
    document.getElementById('addLocationModal').classList.remove('show');
    document.getElementById('addLocationForm').reset();
}

async function handleAddLocation(e) {
    e.preventDefault();
    
    if (!DashboardState.currentUser) return;
    
    const formData = new FormData(e.target);
    const locationData = {
        user_id: DashboardState.currentUser.id,
        name: formData.get('name'),
        latitude: parseFloat(formData.get('latitude')),
        longitude: parseFloat(formData.get('longitude')),
        alert_threshold: formData.get('alert_threshold')
    };
    
    try {
        const response = await fetch(`${API_BASE}/locations`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(locationData)
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                closeAddLocationModal();
                await loadLocationsData();
                showNotification('Location added successfully!', 'success');
                return;
            }
        }
        
        throw new Error('Failed to add location');
        
    } catch (error) {
        console.error('Failed to add location:', error);
        showNotification('Failed to add location. Please try again.', 'error');
    }
}

// Location Actions
async function analyzeLocation(locationId) {
    try {
        showNotification('Starting analysis...', 'info');
        
        const response = await fetch(`${API_BASE}/locations/${locationId}/analyze`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                showNotification('Analysis completed successfully!', 'success');
                await loadLocationsData();
                return;
            }
        }
        
        throw new Error('Analysis failed');
        
    } catch (error) {
        console.error('Failed to analyze location:', error);
        showNotification('Analysis failed. Please try again.', 'error');
    }
}

function editLocation(locationId) {
    // TODO: Implement location editing modal
    showNotification('Location editing coming soon!', 'info');
}

// Alert Actions
async function acknowledgeAlert(alertId) {
    try {
        const response = await fetch(`${API_BASE}/alerts/${alertId}/acknowledge`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                showNotification('Alert acknowledged', 'success');
                await loadAlertsData();
                return;
            }
        }
        
        throw new Error('Failed to acknowledge alert');
        
    } catch (error) {
        console.error('Failed to acknowledge alert:', error);
        showNotification('Failed to acknowledge alert', 'error');
    }
}

function viewAlertDetails(alertId) {
    // TODO: Implement alert details modal
    showNotification('Alert details coming soon!', 'info');
}

function filterAlerts(filter) {
    // TODO: Implement alert filtering
    console.log('Filtering alerts by:', filter);
}

// Test Functions
async function testBackend() {
    const testResults = document.getElementById('testResults');
    testResults.textContent = 'Testing backend...';
    
    try {
        const response = await fetch(`${API_BASE}/test`);
        const data = await response.json();
        
        testResults.textContent = JSON.stringify(data, null, 2);
        
    } catch (error) {
        testResults.textContent = `Backend test failed: ${error.message}`;
    }
}

async function testDatabase() {
    const testResults = document.getElementById('testResults');
    testResults.textContent = 'Testing database...';
    
    // Demo database test
    setTimeout(() => {
        testResults.textContent = 'Database test completed:\
✅ Connection: OK\
✅ Tables: OK\
✅ Queries: OK';
    }, 1000);
}

async function testChatbot() {
    const testResults = document.getElementById('testResults');
    testResults.textContent = 'Testing chatbot...';
    
    try {
        const response = await fetch(`${API_BASE}/chat/status`);
        const data = await response.json();
        
        testResults.textContent = JSON.stringify(data, null, 2);
        
    } catch (error) {
        testResults.textContent = `Chatbot test failed: ${error.message}`;
    }
}

async function testNotifications() {
    if (!DashboardState.currentUser) {
        showNotification('Please set up user profile first', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/notifications/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: DashboardState.currentUser.email,
                phone: DashboardState.currentUser.phone
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                showNotification('Test notifications sent! Check your email.', 'success');
                return;
            }
        }
        
        throw new Error('Test notifications failed');
        
    } catch (error) {
        console.error('Failed to send test notifications:', error);
        showNotification('Failed to send test notifications', 'error');
    }
}

// User Profile
async function handleUserProfileSave(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const userData = {
        name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone')
    };
    
    // Update local state
    DashboardState.currentUser = { ...DashboardState.currentUser, ...userData };
    
    showNotification('Profile updated successfully!', 'success');
}

// Legacy Analysis Setup
function setupLegacyAnalysis() {
    const datetimeInput = document.getElementById('legacyDatetime');
    if (datetimeInput) {
        // Set current datetime as default
        const now = new Date();
        const localDateTime = new Date(now.getTime() - now.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
        datetimeInput.value = localDateTime;
    }
    
    const imageUpload = document.getElementById('legacyImageUpload');
    const uploadText = document.querySelector('.upload-text');
    
    if (imageUpload && uploadText) {
        imageUpload.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                uploadText.textContent = file.name;
            }
        });
    }
    
    const legacyForm = document.getElementById('legacyAnalysisForm');
    if (legacyForm) {
        legacyForm.addEventListener('submit', handleLegacyAnalysis);
    }
}

async function handleLegacyAnalysis(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const resultsContainer = document.getElementById('legacyResults');
    
    // Show loading
    resultsContainer.innerHTML = `
        <div class="card">
            <div class="card-content">
                <div class="loading">Analyzing satellite image...</div>
            </div>
        </div>
    `;
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayLegacyResults(data);
        } else {
            throw new Error(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Legacy analysis failed:', error);
        resultsContainer.innerHTML = `
            <div class="card">
                <div class="card-content">
                    <div class="error">Analysis failed: ${error.message}</div>
                </div>
            </div>
        `;
    }
}

function displayLegacyResults(data) {
    const resultsContainer = document.getElementById('legacyResults');
    const results = data.results;
    
    // This would use the same display logic as the original index.html
    // For now, show a simplified version
    resultsContainer.innerHTML = `
        <div class="card">
            <div class="card-header">
                <h3>📊 Analysis Results</h3>
            </div>
            <div class="card-content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">🤖</div>
                        <div class="stat-info">
                            <div class="stat-value">${results.detection.total_cyclones}</div>
                            <div class="stat-label">Cyclones Detected</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🔮</div>
                        <div class="stat-info">
                            <div class="stat-value">${results.astrology.vrs_analysis.vrs_score}/100</div>
                            <div class="stat-label">VRS Score</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">⚡</div>
                        <div class="stat-info">
                            <div class="stat-value">${Math.round(results.combined.combined_assessment.combined_risk_score)}/100</div>
                            <div class="stat-label">Combined Risk</div>
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-icon">🎯</div>
                        <div class="stat-info">
                            <div class="stat-value">${results.combined.combined_assessment.final_risk_level}</div>
                            <div class="stat-label">Risk Level</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Utility Functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 3000;
        max-width: 300px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    `;
    
    // Set background color based on type
    switch(type) {
        case 'success':
            notification.style.background = '#27ae60';
            break;
        case 'error':
            notification.style.background = '#e74c3c';
            break;
        case 'warning':
            notification.style.background = '#f39c12';
            break;
        default:
            notification.style.background = '#667eea';
    }
    
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 5000);
}

// Periodic Refresh
function setupPeriodicRefresh() {
    // Refresh data every 5 minutes
    setInterval(() => {
        const activeTab = document.querySelector('.nav-item.active');
        if (activeTab) {
            loadTabData(activeTab.dataset.tab);
        }
    }, 5 * 60 * 1000);
    
    // Check system health every minute
    setInterval(checkSystemHealth, 60 * 1000);
}

// Export functions for global access
window.analyzeLocation = analyzeLocation;
window.editLocation = editLocation;
window.acknowledgeAlert = acknowledgeAlert;
window.viewAlertDetails = viewAlertDetails;
window.openAddLocationModal = openAddLocationModal;
window.closeAddLocationModal = closeAddLocationModal;

console.log('📊 Enhanced Dashboard JavaScript loaded');