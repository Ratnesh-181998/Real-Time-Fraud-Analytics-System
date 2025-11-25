/**
 * Real-Time Fraud Analytics Dashboard - Main Application
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const UPDATE_INTERVAL = 5000; // 5 seconds

// State
let simulationInterval = null;
let simulationStats = {
    transactions: 0,
    fraud: 0
};
let recentTransactions = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Initializing Fraud Analytics Dashboard...');
    
    // Setup navigation
    setupNavigation();
    
    // Setup form handlers
    setupFormHandlers();
    
    // Setup simulation controls
    setupSimulationControls();
    
    // Setup range inputs
    setupRangeInputs();
    
    // Check API connection
    checkAPIConnection();
    
    // Start periodic updates
    startPeriodicUpdates();
    
    // Initialize charts
    initializeCharts();
    
    console.log('Dashboard initialized successfully');
}

/**
 * Setup navigation between sections
 */
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    const sections = document.querySelectorAll('.content-section');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all items and sections
            navItems.forEach(nav => nav.classList.remove('active'));
            sections.forEach(section => section.classList.remove('active'));
            
            // Add active class to clicked item
            item.classList.add('active');
            
            // Show corresponding section
            const sectionId = item.dataset.section + '-section';
            const targetSection = document.getElementById(sectionId);
            if (targetSection) {
                targetSection.classList.add('active');
            }
        });
    });
}

/**
 * Setup form handlers
 */
function setupFormHandlers() {
    const checkForm = document.getElementById('checkTransactionForm');
    if (checkForm) {
        checkForm.addEventListener('submit', handleCheckTransaction);
    }
}

/**
 * Setup simulation controls
 */
function setupSimulationControls() {
    const startBtn = document.getElementById('startSimulation');
    const stopBtn = document.getElementById('stopSimulation');
    
    if (startBtn) {
        startBtn.addEventListener('click', startSimulation);
    }
    
    if (stopBtn) {
        stopBtn.addEventListener('click', stopSimulation);
    }
}

/**
 * Setup range input displays
 */
function setupRangeInputs() {
    // Transaction rate
    const rateInput = document.getElementById('transactionRate');
    const rateValue = document.getElementById('rateValue');
    if (rateInput && rateValue) {
        rateInput.addEventListener('input', (e) => {
            rateValue.textContent = `${e.target.value} TPS`;
        });
    }
    
    // Fraud probability
    const fraudInput = document.getElementById('fraudProbability');
    const fraudValue = document.getElementById('fraudProbValue');
    if (fraudInput && fraudValue) {
        fraudInput.addEventListener('input', (e) => {
            fraudValue.textContent = `${e.target.value}%`;
        });
    }
    
    // Settings ranges
    const xgboostInput = document.getElementById('xgboostWeight');
    const xgboostValue = document.getElementById('xgboostWeightValue');
    if (xgboostInput && xgboostValue) {
        xgboostInput.addEventListener('input', (e) => {
            const weight = (e.target.value / 100).toFixed(2);
            xgboostValue.textContent = weight;
            // Auto-update autoencoder weight
            const autoencoderInput = document.getElementById('autoencoderWeight');
            if (autoencoderInput) {
                autoencoderInput.value = 100 - e.target.value;
                document.getElementById('autoencoderWeightValue').textContent = 
                    ((100 - e.target.value) / 100).toFixed(2);
            }
        });
    }
    
    const fraudThresholdInput = document.getElementById('fraudThreshold');
    const fraudThresholdValue = document.getElementById('fraudThresholdValue');
    if (fraudThresholdInput && fraudThresholdValue) {
        fraudThresholdInput.addEventListener('input', (e) => {
            fraudThresholdValue.textContent = (e.target.value / 100).toFixed(2);
        });
    }
}

/**
 * Check API connection
 */
async function checkAPIConnection() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        
        if (data.status === 'healthy') {
            updateAPIStatus(true);
            showToast('Connected to API', 'success');
        } else {
            updateAPIStatus(false);
        }
    } catch (error) {
        console.error('API connection error:', error);
        updateAPIStatus(false);
        showToast('Failed to connect to API. Please start the server.', 'error');
    }
}

/**
 * Update API status indicator
 */
function updateAPIStatus(isConnected) {
    const statusDot = document.getElementById('apiStatus');
    const statusText = document.getElementById('apiStatusText');
    
    if (statusDot && statusText) {
        if (isConnected) {
            statusDot.style.background = 'var(--success)';
            statusDot.style.boxShadow = '0 0 10px var(--success)';
            statusText.textContent = 'API Connected';
        } else {
            statusDot.style.background = 'var(--danger)';
            statusDot.style.boxShadow = '0 0 10px var(--danger)';
            statusText.textContent = 'API Disconnected';
        }
    }
}

/**
 * Start periodic updates
 */
function startPeriodicUpdates() {
    // Update stats immediately
    updateStatistics();
    
    // Then update every 5 seconds
    setInterval(updateStatistics, UPDATE_INTERVAL);
    
    // Update uptime every second
    setInterval(updateUptime, 1000);
}

/**
 * Update statistics from API
 */
async function updateStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();
        
        // Update metric cards
        updateElement('totalTransactions', data.total_requests);
        updateElement('fraudDetected', data.fraud_detected);
        updateElement('legitimateTransactions', data.legitimate_transactions);
        updateElement('avgResponseTime', `${data.avg_processing_time_ms.toFixed(1)}ms`);
        
        // Update fraud rate change
        const fraudRate = (data.fraud_rate * 100).toFixed(1);
        const fraudChange = document.getElementById('fraudChange');
        if (fraudChange) {
            fraudChange.innerHTML = `<i class="fas fa-chart-line"></i> ${fraudRate}%`;
        }
        
        // Update system info
        if (data.detector_stats) {
            updateElement('usersTracked', data.detector_stats.users_tracked);
        }
        
        // Update charts
        updateCharts(data);
        
    } catch (error) {
        console.error('Error updating statistics:', error);
    }
}

/**
 * Update uptime display
 */
let startTime = Date.now();
function updateUptime() {
    const uptime = Math.floor((Date.now() - startTime) / 1000);
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    const seconds = uptime % 60;
    
    const uptimeText = `Uptime: ${hours}h ${minutes}m ${seconds}s`;
    updateElement('uptime', uptimeText);
}

/**
 * Handle check transaction form submission
 */
async function handleCheckTransaction(e) {
    e.preventDefault();
    
    const formData = {
        transaction_id: document.getElementById('transactionId').value,
        user_id: document.getElementById('userId').value,
        merchant_id: document.getElementById('merchantId').value,
        amount: parseFloat(document.getElementById('amount').value),
        transaction_type: document.getElementById('transactionType').value,
        timestamp: document.getElementById('timestamp').value || new Date().toISOString()
    };
    
    try {
        showToast('Analyzing transaction...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/api/check-fraud`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        // Display result
        displayCheckResult(result);
        
        // Add to recent transactions
        addToRecentTransactions(result);
        
        showToast('Analysis complete', 'success');
        
    } catch (error) {
        console.error('Error checking transaction:', error);
        showToast('Error analyzing transaction', 'error');
    }
}

/**
 * Display check result
 */
function displayCheckResult(result) {
    const resultCard = document.getElementById('checkResult');
    const resultContent = resultCard.querySelector('.result-content');
    
    const riskClass = result.risk_level.toLowerCase();
    const statusClass = result.is_fraud ? 'fraud' : 'legitimate';
    
    resultContent.innerHTML = `
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
            <div class="info-item">
                <span class="info-label">Transaction ID</span>
                <span class="info-value">${result.transaction_id}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Fraud Score</span>
                <span class="info-value">${(result.fraud_score * 100).toFixed(1)}%</span>
            </div>
            <div class="info-item">
                <span class="info-label">Risk Level</span>
                <span class="badge ${riskClass}">${result.risk_level}</span>
            </div>
            <div class="info-item">
                <span class="info-label">Status</span>
                <span class="badge ${statusClass}">${result.is_fraud ? 'FRAUD' : 'LEGITIMATE'}</span>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary);">Model Scores</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div class="info-item">
                    <span class="info-label">XGBoost</span>
                    <span class="info-value">${(result.xgboost_score * 100).toFixed(1)}%</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Autoencoder</span>
                    <span class="info-value">${(result.autoencoder_score * 100).toFixed(1)}%</span>
                </div>
            </div>
        </div>
        
        <div>
            <h4 style="margin-bottom: 0.5rem; color: var(--text-secondary);">Risk Factors</h4>
            <ul style="list-style: none; padding: 0;">
                ${result.risk_factors.map(factor => `
                    <li style="padding: 0.5rem; background: var(--bg-tertiary); border-radius: var(--radius-md); margin-bottom: 0.5rem;">
                        <i class="fas fa-exclamation-circle" style="color: var(--warning); margin-right: 0.5rem;"></i>
                        ${factor}
                    </li>
                `).join('')}
            </ul>
        </div>
        
        <div style="margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid var(--border-color); color: var(--text-muted); font-size: 0.875rem;">
            Processing Time: ${result.processing_time_ms.toFixed(2)}ms
        </div>
    `;
    
    resultCard.style.display = 'block';
}

/**
 * Close result card
 */
function closeResult() {
    const resultCard = document.getElementById('checkResult');
    resultCard.style.display = 'none';
}

/**
 * Generate random transaction
 */
function generateRandomTransaction() {
    const transactionId = 'TXN' + Math.random().toString(36).substr(2, 9).toUpperCase();
    const userId = 'USER' + Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    const merchantId = 'MERCH' + Math.floor(Math.random() * 500).toString().padStart(3, '0');
    const amount = (Math.random() * 2000 + 10).toFixed(2);
    
    document.getElementById('transactionId').value = transactionId;
    document.getElementById('userId').value = userId;
    document.getElementById('merchantId').value = merchantId;
    document.getElementById('amount').value = amount;
    
    // Set current time
    const now = new Date();
    const timestamp = now.toISOString().slice(0, 16);
    document.getElementById('timestamp').value = timestamp;
    
    showToast('Random transaction generated', 'info');
}

/**
 * Add transaction to recent transactions table
 */
function addToRecentTransactions(result) {
    recentTransactions.unshift(result);
    if (recentTransactions.length > 10) {
        recentTransactions.pop();
    }
    
    updateTransactionsTable();
}

/**
 * Update transactions table
 */
function updateTransactionsTable() {
    const tbody = document.getElementById('transactionsTableBody');
    
    if (recentTransactions.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>No transactions yet. Start simulation to see data.</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = recentTransactions.map(txn => {
        const riskClass = txn.risk_level.toLowerCase();
        const statusClass = txn.is_fraud ? 'fraud' : 'legitimate';
        const timestamp = new Date(txn.timestamp).toLocaleString();
        
        return `
            <tr>
                <td><code>${txn.transaction_id}</code></td>
                <td>${timestamp}</td>
                <td>$${(Math.random() * 1000).toFixed(2)}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <div style="flex: 1; background: var(--bg-tertiary); height: 6px; border-radius: 3px; overflow: hidden;">
                            <div style="width: ${txn.fraud_score * 100}%; height: 100%; background: ${txn.fraud_score > 0.75 ? 'var(--danger)' : txn.fraud_score > 0.5 ? 'var(--warning)' : 'var(--success)'}; transition: width 0.3s;"></div>
                        </div>
                        <span style="min-width: 50px;">${(txn.fraud_score * 100).toFixed(1)}%</span>
                    </div>
                </td>
                <td><span class="badge ${riskClass}">${txn.risk_level}</span></td>
                <td><span class="badge ${statusClass}">${txn.is_fraud ? 'FRAUD' : 'SAFE'}</span></td>
                <td>
                    <button class="btn-icon" onclick="viewTransactionDetails('${txn.transaction_id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Refresh transactions
 */
function refreshTransactions() {
    updateTransactionsTable();
    showToast('Transactions refreshed', 'info');
}

/**
 * View transaction details
 */
function viewTransactionDetails(transactionId) {
    const txn = recentTransactions.find(t => t.transaction_id === transactionId);
    if (txn) {
        displayCheckResult(txn);
        // Switch to check section
        document.querySelector('.nav-item[data-section="check"]').click();
    }
}

/**
 * Helper function to update element text
 */
function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = 'toast';
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    const colors = {
        success: 'var(--success)',
        error: 'var(--danger)',
        warning: 'var(--warning)',
        info: 'var(--info)'
    };
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fas ${icons[type]}" style="color: ${colors[type]}; font-size: 1.25rem;"></i>
            <span>${message}</span>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'toastOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Export functions for global use
window.generateRandomTransaction = generateRandomTransaction;
window.closeResult = closeResult;
window.refreshTransactions = refreshTransactions;
window.viewTransactionDetails = viewTransactionDetails;
window.clearFeed = clearFeed;
