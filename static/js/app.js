// DOM Elements
const attackForm = document.getElementById('attackForm');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const targetInput = document.getElementById('target');
const threadsInput = document.getElementById('threads');
const modeSelect = document.getElementById('mode');

// Stats elements
const statTotal = document.getElementById('statTotal');
const statSuccess = document.getElementById('statSuccess');
const statFailed = document.getElementById('statFailed');
const statRPS = document.getElementById('statRPS');
const statDuration = document.getElementById('statDuration');
const statRate = document.getElementById('statRate');
const statusValue = document.getElementById('statusValue');
const statusTarget = document.getElementById('statusTarget');
const statusThreads = document.getElementById('statusThreads');
const statusMode = document.getElementById('statusMode');
const errorsSection = document.getElementById('errorsSection');
const errorsList = document.getElementById('errorsList');

let attackStartTime = null;
let statsInterval = null;
let statusPollInterval = null;
let currentAttackId = null;

// Form submission
attackForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await startAttack();
});

// Stop button
stopBtn.addEventListener('click', async () => {
    await stopAttack();
});

// Start attack
async function startAttack() {
    const target = targetInput.value.trim();
    const threads = parseInt(threadsInput.value);
    const mode = modeSelect.value;

    if (!target) {
        alert('Please enter a target');
        return;
    }

    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target, threads, mode })
        });

        const data = await response.json();

        if (response.ok) {
            currentAttackId = data.attack_id;
            attackStartTime = Date.now();
            startBtn.disabled = true;
            stopBtn.disabled = false;
            attackForm.style.pointerEvents = 'none';
            updateStatus('Attacking', 'running');
            statusTarget.textContent = target;
            statusThreads.textContent = threads;
            statusMode.textContent = mode.charAt(0).toUpperCase() + mode.slice(1);
            
            // Start duration timer and status polling
            startStatsTimer();
            startStatusPolling();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error starting attack:', error);
        alert('Failed to start attack: ' + error.message);
    }
}

// Stop attack
async function stopAttack() {
    if (!currentAttackId) {
        alert('No active attack to stop');
        return;
    }

    try {
        const response = await fetch('/api/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ attack_id: currentAttackId })
        });

        const data = await response.json();

        if (response.ok) {
            startBtn.disabled = false;
            stopBtn.disabled = true;
            attackForm.style.pointerEvents = 'auto';
            updateStatus('Stopped', 'stopped');
            
            if (data.stats) {
                updateStats(data.stats);
            }
            
            stopStatsTimer();
            stopStatusPolling();
            currentAttackId = null;
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error stopping attack:', error);
        alert('Failed to stop attack: ' + error.message);
    }
}

// Poll for status updates
function startStatusPolling() {
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
    }
    
    statusPollInterval = setInterval(async () => {
        if (currentAttackId) {
            try {
                const response = await fetch(`/api/status?attack_id=${currentAttackId}`);
                const data = await response.json();
                
                if (data.running) {
                    updateStats(data);
                } else {
                    // Attack stopped
                    stopStatusPolling();
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                    attackForm.style.pointerEvents = 'auto';
                    updateStatus('Stopped', 'stopped');
                    if (data.total !== undefined) {
                        updateStats(data);
                    }
                    currentAttackId = null;
                }
            } catch (error) {
                console.error('Error polling status:', error);
            }
        }
    }, 1000); // Poll every second
}

// Stop status polling
function stopStatusPolling() {
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
}

// Update statistics
function updateStats(stats) {
    statTotal.textContent = formatNumber(stats.total);
    statSuccess.textContent = formatNumber(stats.success);
    statFailed.textContent = formatNumber(stats.failed);
    
    // Calculate RPS
    const duration = stats.duration || 0;
    const rps = duration > 0 ? (stats.total / duration).toFixed(1) : '0.0';
    statRPS.textContent = rps;
    
    // Calculate success rate
    const rate = stats.total > 0 ? ((stats.success / stats.total) * 100).toFixed(1) : '0.0';
    statRate.textContent = rate + '%';
    
    // Update errors
    if (stats.errors && Object.keys(stats.errors).length > 0) {
        errorsSection.style.display = 'block';
        errorsList.innerHTML = '';
        for (const [errorType, count] of Object.entries(stats.errors)) {
            const errorItem = document.createElement('div');
            errorItem.className = 'error-item';
            errorItem.innerHTML = `
                <span>${errorType}</span>
                <span>${formatNumber(count)}</span>
            `;
            errorsList.appendChild(errorItem);
        }
    } else {
        errorsSection.style.display = 'none';
    }
}

// Update status
function updateStatus(status, className) {
    statusValue.textContent = status;
    statusValue.className = 'status-value ' + className;
}

// Start stats timer
function startStatsTimer() {
    if (statsInterval) {
        clearInterval(statsInterval);
    }
    
    statsInterval = setInterval(() => {
        if (attackStartTime) {
            const duration = Math.floor((Date.now() - attackStartTime) / 1000);
            statDuration.textContent = formatDuration(duration);
        }
    }, 1000);
}

// Stop stats timer
function stopStatsTimer() {
    if (statsInterval) {
        clearInterval(statsInterval);
        statsInterval = null;
    }
}

// Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Format duration
function formatDuration(seconds) {
    if (seconds < 60) {
        return seconds + 's';
    } else if (seconds < 3600) {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return mins + 'm ' + secs + 's';
    } else {
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return hours + 'h ' + mins + 'm ' + secs + 's';
    }
}

// Initialize on page load
window.addEventListener('load', () => {
    updateStatus('Ready', 'ready');
});
