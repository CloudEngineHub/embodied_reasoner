let ws = null;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
   
    ws = new WebSocket(wsUrl);
   
    ws.onopen = function(event) {
        console.log('WebSocket connection successful');
        document.getElementById('connection-status').textContent = 'WebSocket: Connected';
        reconnectAttempts = 0;
        stopPolling(); // WebSocket connected, stop polling
    };
   
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleStateUpdate(data);
    };
   
    ws.onclose = function(event) {
        console.log('WebSocket connection closed');
        document.getElementById('connection-status').textContent = 'WebSocket: Disconnected (Polling Mode)';
       
        // Start polling as a fallback
        startPolling();
       
        if (reconnectAttempts < maxReconnectAttempts) {
            reconnectAttempts++;
            setTimeout(connectWebSocket, 2000 * reconnectAttempts);
        }
    };
   
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
        document.getElementById('connection-status').textContent = 'WebSocket: Connection Error (Polling Mode)';
       
        // WebSocket error, start polling
        startPolling();
    };
}

function handleStateUpdate(data) {
    if (data.type !== 'state_update') return;
   
    // Update task information
    updateCurrentTask(data.current_task);
    updateTaskHistory(data.task_history);
    updateInteractionLog(data.interaction_log);
    updateTaskStats(data.task_stats);
    updateDisambiguationHistory(data.disambiguation_history);
   
    // Update disambiguation interface
    if (data.disambiguation_active && data.disambiguation_data) {
        showDisambiguationPanel(data.disambiguation_data);
    } else {
        hideDisambiguationPanel();
    }
}

function updateCurrentTask(task) {
    if (task) {
        document.getElementById('current-task-name').textContent = task.name;
        document.getElementById('current-task-scene').textContent = `Scene: ${task.scene} | Steps: ${task.step_count}/${task.max_steps}`;
        document.getElementById('system-status').textContent = task.status === 'running' ? 'Running' : 'Idle';
    } else {
        document.getElementById('current-task-name').textContent = 'Waiting...';
        document.getElementById('current-task-scene').textContent = '';
        document.getElementById('system-status').textContent = 'Ready';
    }
}

function updateTaskHistory(history) {
    const container = document.getElementById('task-history');
   
    if (!history || history.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: #7f8c8d; padding: 20px;">No task history available</div>';
        return;
    }
   
    container.innerHTML = history.map(task => {
        const statusIcon = task.status === 'completed' ? (task.success ? ' ' : ' ') : ' ';
        const duration = task.end_time ?
            Math.round((new Date(task.end_time) - new Date(task.start_time)) / 1000) : 0;
       
        return `
            <div class="task-item ${task.status}">
                <div class="task-name">${statusIcon} ${task.name}</div>
                <div class="task-meta">
                    Scene: ${task.scene} | Steps: ${task.step_count} |
                    ${task.end_time ? `Duration: ${duration}s` : 'In progress...'}
                </div>
            </div>
        `;
    }).join('');
}

function updateInteractionLog(log) {
    const container = document.getElementById('interaction-log');
   
    if (!log || log.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: #7f8c8d; padding: 20px;">Waiting for interaction data...</div>';
        return;
    }
   
    container.innerHTML = log.map(item => `
        <div class="interaction-item ${item.type}">
            <span class="timestamp">[${item.timestamp}]</span>
            <div><strong>${item.action}</strong></div>
            ${item.content ? `<div style="font-size: 0.9em; color: #666;">${item.content}</div>` : ''}
            ${item.image_path ? `<div style="font-size: 0.8em; color: #999;">Image: ${item.image_path}</div>` : ''}
        </div>
    `).join('');
   
    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function updateTaskStats(stats) {
    const total = stats.total_tasks || 0;
    const completed = stats.completed_tasks || 0;
    const current = stats.current_task_index || 0;
   
    document.getElementById('task-progress').textContent = `${current} / ${total}`;
   
    const progressPercent = total > 0 ? (completed / total * 100) : 0;
    document.getElementById('progress-fill').style.width = `${progressPercent}%`;
   
    const successRate = total > 0 ? Math.round(completed / total * 100) : 0;
    document.getElementById('success-rate').textContent = `${successRate}%`;
}

function updateDisambiguationHistory(history) {
    const container = document.getElementById('disambiguation-history');
   
    if (!history || history.length === 0) {
        container.innerHTML = '<div style="text-align: center; color: #7f8c8d; padding: 20px;">No disambiguation history available</div>';
        return;
    }
   
    container.innerHTML = history.map(item => {
        const startTime = new Date(item.start_time).toLocaleTimeString();
        const duration = item.end_time ? 
            Math.round((new Date(item.end_time) - new Date(item.start_time)) / 1000) : 0;
        
        const statusClass = item.selection_method === 'user_choice' ? 'completed' : 'auto-selected';
        const statusText = item.selection_method === 'user_choice' ? 'User Selected' : 'Auto Selected';
        
        let candidatesHtml = '';
        if (item.candidates) {
            candidatesHtml = `
                <div class="disambiguation-candidates">
                    ${item.candidates.map((candidate, idx) => `
                        <div class="disambiguation-candidate ${idx === (item.user_selection - 1) ? 'selected' : ''}">
                            Option ${idx + 1}: ${candidate.confidence}%
                        </div>
                    `).join('')}
                </div>
            `;
        }
        
        let selectedChoiceHtml = '';
        if (item.selected_object) {
            selectedChoiceHtml = `
                <div class="selected-choice">
                    <strong>Selected:</strong> Option ${item.user_selection}<br>
                    <strong>Confidence:</strong> ${item.selected_object.confidence}%<br>
                    <strong>Reasoning:</strong> ${item.selected_object.reasoning || 'N/A'}
                </div>
            `;
        }
        
        return `
            <div class="disambiguation-item ${statusClass}">
                <div class="disambiguation-header">
                    <span>${item.object_type || 'Object'} Selection - Step ${item.step}</span>
                    <span class="disambiguation-time">${startTime} (${duration}s)</span>
                </div>
                <div class="disambiguation-details">
                    <strong>Task:</strong> ${item.task_name || 'Navigation Task'}<br>
                    <strong>Status:</strong> ${statusText}<br>
                    <strong>Candidates:</strong> ${item.candidates ? item.candidates.length : 0}
                </div>
                ${candidatesHtml}
                ${selectedChoiceHtml}
            </div>
        `;
    }).join('');
   
    // Scroll to bottom to show latest
    container.scrollTop = container.scrollHeight;
}

function showDisambiguationPanel(data) {
    const panel = document.getElementById('disambiguation-panel');
    const grid = document.getElementById('candidate-grid');
   
    document.getElementById('disambiguation-task').textContent =
        `Task: ${data.task_name || 'Navigation Task'} - Please select the most suitable ${data.object_type || 'object'}:`;
   
    grid.innerHTML = data.candidates.map((candidate, index) => {
        const confidenceClass = candidate.confidence >= 70 ? 'high-confidence' :
                              candidate.confidence >= 50 ? 'medium-confidence' : 'low-confidence';
       
        return `
            <div class="candidate-card ${confidenceClass}">
                <img class="candidate-image" src="/image/${encodeURIComponent(candidate.image_path)}" alt="Candidate ${index + 1}">
                <h4>Option ${index + 1} - Confidence: ${candidate.confidence}%</h4>
                <p style="font-size: 0.9em; margin: 8px 0;">${candidate.reasoning}</p>
                <button class="select-btn" onclick="selectCandidate(${index + 1})">Select</button>
            </div>
        `;
    }).join('');
   
    panel.classList.remove('hidden');
}

function hideDisambiguationPanel() {
    document.getElementById('disambiguation-panel').classList.add('hidden');
}

function selectCandidate(selection) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'user_selection',
            selection: selection
        }));
    }
    hideDisambiguationPanel();
}

// Polling mechanism (fallback)
let pollingInterval = null;
let lastUpdateTimestamp = null;

function startPolling() {
    if (pollingInterval) return;
    console.log('Starting polling mode');
    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/state');
            if (response.ok) {
                const data = await response.json();
                // Check for new data
                if (!lastUpdateTimestamp || data.timestamp !== lastUpdateTimestamp) {
                    lastUpdateTimestamp = data.timestamp;
                    handleStateUpdate(data);
                    console.log('New data fetched via polling');
                }
            }
        } catch (error) {
            console.log('Polling request failed:', error);
        }
    }, 2000); // Poll every 2 seconds
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
        console.log('Stopping polling mode');
    }
}

// Auto-refresh mechanism (final fallback)
let autoRefreshInterval = null;

function startAutoRefresh() {
    if (autoRefreshInterval) return;
    autoRefreshInterval = setInterval(() => {
        // Check WebSocket status, if disconnected and no reconnection is happening, refresh the page
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            console.log('Both WebSocket and polling are down, refreshing page');
            location.reload();
        }
    }, 15000); // Check every 15 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Connect WebSocket after the page loads
document.addEventListener('DOMContentLoaded', function() {
    connectWebSocket();
    startAutoRefresh();
});