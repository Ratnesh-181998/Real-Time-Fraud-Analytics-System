/**
 * Real-Time Fraud Analytics Dashboard - Simulation & Charts
 */

// Simulation state
let simulationInterval = null;
let simulationStats = {
    transactions: 0,
    fraud: 0,
    startTime: null
};

// Chart instances
let fraudTrendChart = null;
let riskDistributionChart = null;
let modelComparisonChart = null;
let processingTimeChart = null;
let fraudScoreChart = null;

// Chart data
let chartData = {
    fraudTrend: {
        labels: [],
        legitimate: [],
        fraud: []
    },
    riskDistribution: {
        low: 0,
        medium: 0,
        high: 0
    },
    modelScores: {
        xgboost: [],
        autoencoder: []
    },
    processingTimes: [],
    fraudScores: []
};

/**
 * Initialize all charts
 */
function initializeCharts() {
    initFraudTrendChart();
    initRiskDistributionChart();
    initModelComparisonChart();
    initProcessingTimeChart();
    initFraudScoreChart();
}

/**
 * Initialize Fraud Trend Chart
 */
function initFraudTrendChart() {
    const ctx = document.getElementById('fraudTrendChart');
    if (!ctx) return;

    fraudTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Legitimate',
                    data: [],
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Fraud',
                    data: [],
                    borderColor: 'rgb(239, 68, 68)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#cbd5e1',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y: {
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

/**
 * Initialize Risk Distribution Chart
 */
function initRiskDistributionChart() {
    const ctx = document.getElementById('riskDistributionChart');
    if (!ctx) return;

    riskDistributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: [
                    'rgb(16, 185, 129)',
                    'rgb(245, 158, 11)',
                    'rgb(239, 68, 68)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#cbd5e1',
                        font: {
                            family: 'Inter'
                        },
                        padding: 15
                    }
                }
            }
        }
    });
}

/**
 * Initialize Model Comparison Chart
 */
function initModelComparisonChart() {
    const ctx = document.getElementById('modelComparisonChart');
    if (!ctx) return;

    modelComparisonChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Precision', 'Recall', 'F1-Score', 'AUC-ROC'],
            datasets: [
                {
                    label: 'XGBoost',
                    data: [0.94, 0.89, 0.91, 0.96],
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderColor: 'rgb(99, 102, 241)',
                    borderWidth: 1
                },
                {
                    label: 'Autoencoder',
                    data: [0.87, 0.85, 0.86, 0.91],
                    backgroundColor: 'rgba(139, 92, 246, 0.8)',
                    borderColor: 'rgb(139, 92, 246)',
                    borderWidth: 1
                },
                {
                    label: 'Ensemble',
                    data: [0.96, 0.92, 0.94, 0.98],
                    backgroundColor: 'rgba(236, 72, 153, 0.8)',
                    borderColor: 'rgb(236, 72, 153)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#cbd5e1',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y: {
                    beginAtZero: true,
                    max: 1,
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

/**
 * Initialize Processing Time Chart
 */
function initProcessingTimeChart() {
    const ctx = document.getElementById('processingTimeChart');
    if (!ctx) return;

    processingTimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Processing Time (ms)',
                data: [],
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: {
                        color: '#cbd5e1',
                        font: {
                            family: 'Inter'
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8',
                        callback: function (value) {
                            return value + 'ms';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize Fraud Score Distribution Chart
 */
function initFraudScoreChart() {
    const ctx = document.getElementById('fraudScoreChart');
    if (!ctx) return;

    fraudScoreChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'],
            datasets: [{
                label: 'Transaction Count',
                data: [0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(245, 158, 11, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: '#334155'
                    },
                    ticks: {
                        color: '#94a3b8',
                        precision: 0
                    }
                }
            }
        }
    });
}

/**
 * Update charts with new data
 */
function updateCharts(stats) {
    // Update fraud trend chart
    if (fraudTrendChart) {
        const now = new Date().toLocaleTimeString();

        if (chartData.fraudTrend.labels.length > 20) {
            chartData.fraudTrend.labels.shift();
            chartData.fraudTrend.legitimate.shift();
            chartData.fraudTrend.fraud.shift();
        }

        chartData.fraudTrend.labels.push(now);
        chartData.fraudTrend.legitimate.push(stats.legitimate_transactions);
        chartData.fraudTrend.fraud.push(stats.fraud_detected);

        fraudTrendChart.data.labels = chartData.fraudTrend.labels;
        fraudTrendChart.data.datasets[0].data = chartData.fraudTrend.legitimate;
        fraudTrendChart.data.datasets[1].data = chartData.fraudTrend.fraud;
        fraudTrendChart.update('none');
    }

    // Update risk distribution chart
    if (riskDistributionChart && stats.total_requests > 0) {
        const low = Math.floor(stats.legitimate_transactions * 0.7);
        const medium = Math.floor(stats.legitimate_transactions * 0.2);
        const high = stats.fraud_detected;

        riskDistributionChart.data.datasets[0].data = [low, medium, high];
        riskDistributionChart.update('none');
    }
}

/**
 * Update processing time chart
 */
function updateProcessingTimeChart(processingTime) {
    if (!processingTimeChart) return;

    const now = new Date().toLocaleTimeString();

    if (chartData.processingTimes.length > 50) {
        processingTimeChart.data.labels.shift();
        chartData.processingTimes.shift();
    }

    processingTimeChart.data.labels.push(now);
    chartData.processingTimes.push(processingTime);
    processingTimeChart.data.datasets[0].data = chartData.processingTimes;
    processingTimeChart.update('none');
}

/**
 * Update fraud score distribution chart
 */
function updateFraudScoreChart(fraudScore) {
    if (!fraudScoreChart) return;

    const bucket = Math.floor(fraudScore * 5);
    const index = Math.min(bucket, 4);

    fraudScoreChart.data.datasets[0].data[index]++;
    fraudScoreChart.update('none');
}

/**
 * Start simulation
 */
async function startSimulation() {
    const rate = parseInt(document.getElementById('transactionRate').value);
    const fraudProb = parseInt(document.getElementById('fraudProbability').value) / 100;

    // Reset stats
    simulationStats = {
        transactions: 0,
        fraud: 0,
        startTime: Date.now()
    };

    // Update UI
    document.getElementById('startSimulation').style.display = 'none';
    document.getElementById('stopSimulation').style.display = 'inline-flex';

    // Clear feed
    const feed = document.getElementById('liveFeed');
    feed.innerHTML = '';

    showToast('Simulation started', 'success');

    // Calculate interval (1000ms / rate)
    const interval = Math.max(100, Math.floor(1000 / rate));

    simulationInterval = setInterval(async () => {
        await generateAndCheckTransaction(fraudProb);
        updateSimulationStats();
    }, interval);
}

/**
 * Stop simulation
 */
function stopSimulation() {
    if (simulationInterval) {
        clearInterval(simulationInterval);
        simulationInterval = null;
    }

    // Update UI
    document.getElementById('startSimulation').style.display = 'inline-flex';
    document.getElementById('stopSimulation').style.display = 'none';

    showToast('Simulation stopped', 'info');
}

/**
 * Generate and check a random transaction
 */
async function generateAndCheckTransaction(fraudProb) {
    const isFraudSimulated = Math.random() < fraudProb;

    const transaction = {
        transaction_id: 'SIM' + Math.random().toString(36).substr(2, 9).toUpperCase(),
        user_id: 'USER' + Math.floor(Math.random() * 1000).toString().padStart(3, '0'),
        merchant_id: 'MERCH' + Math.floor(Math.random() * 500).toString().padStart(3, '0'),
        amount: isFraudSimulated
            ? Math.random() * 5000 + 1000  // Higher amounts for fraud
            : Math.random() * 500 + 10,    // Normal amounts
        transaction_type: 'purchase',
        timestamp: new Date().toISOString()
    };

    try {
        const response = await fetch(`${API_BASE_URL}/api/check-fraud`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transaction)
        });

        const result = await response.json();

        // Update simulation stats
        simulationStats.transactions++;
        if (result.is_fraud) {
            simulationStats.fraud++;
        }

        // Add to live feed
        addToLiveFeed(result);

        // Update charts
        updateProcessingTimeChart(result.processing_time_ms);
        updateFraudScoreChart(result.fraud_score);

        // Add to recent transactions
        addToRecentTransactions(result);

    } catch (error) {
        console.error('Error in simulation:', error);
    }
}

/**
 * Update simulation statistics display
 */
function updateSimulationStats() {
    updateElement('simTransactions', simulationStats.transactions);
    updateElement('simFraud', simulationStats.fraud);

    // Calculate rate
    const elapsed = (Date.now() - simulationStats.startTime) / 1000;
    const rate = elapsed > 0 ? (simulationStats.transactions / elapsed).toFixed(1) : 0;
    updateElement('simRate', `${rate} TPS`);
}

/**
 * Add transaction to live feed
 */
function addToLiveFeed(result) {
    const feed = document.getElementById('liveFeed');

    // Remove empty state if present
    const emptyState = feed.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }

    const feedItem = document.createElement('div');
    feedItem.className = 'feed-item';

    const riskClass = result.risk_level.toLowerCase();
    const statusClass = result.is_fraud ? 'fraud' : 'legitimate';

    feedItem.innerHTML = `
        <div style="flex: 1;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.25rem;">
                <code style="font-size: 0.875rem;">${result.transaction_id}</code>
                <span class="badge ${statusClass}">${result.is_fraud ? 'FRAUD' : 'SAFE'}</span>
                <span class="badge ${riskClass}">${result.risk_level}</span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">
                Score: ${(result.fraud_score * 100).toFixed(1)}% | 
                Time: ${result.processing_time_ms.toFixed(1)}ms
            </div>
        </div>
        <div style="text-align: right;">
            <div style="font-weight: 600; color: var(--text-primary);">
                $${(Math.random() * 1000).toFixed(2)}
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted);">
                ${new Date(result.timestamp).toLocaleTimeString()}
            </div>
        </div>
    `;

    // Add to top of feed
    feed.insertBefore(feedItem, feed.firstChild);

    // Keep only last 50 items
    while (feed.children.length > 50) {
        feed.removeChild(feed.lastChild);
    }
}

/**
 * Clear live feed
 */
function clearFeed() {
    const feed = document.getElementById('liveFeed');
    feed.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-stream"></i>
            <p>Start simulation to see live transactions</p>
        </div>
    `;
    showToast('Feed cleared', 'info');
}

// Export functions
window.startSimulation = startSimulation;
window.stopSimulation = stopSimulation;
window.updateCharts = updateCharts;
window.initializeCharts = initializeCharts;
