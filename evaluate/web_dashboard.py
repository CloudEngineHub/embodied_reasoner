#!/usr/bin/env python3
# Web Dashboard for Embodied Agent Monitor

import asyncio
import json
import os
import time
import threading
import webbrowser
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import deque

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, FileResponse  
import uvicorn
FASTAPI_AVAILABLE = True


class AgentMonitor:    
    def __init__(self):
        self.current_task = None
        self.task_history = []
        self.interaction_log = deque(maxlen=10)  # Recent 10 interactions
        self.active_connections: List[WebSocket] = []
        self.disambiguation_active = False
        self.disambiguation_data = None
        self.user_selection = None
        self.task_stats = {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'current_task_index': 0
        }
   
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Send current state
        await self.broadcast_state_update()
   
    def disconnect(self, websocket: WebSocket):
        """Disconnect WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
   
    async def broadcast_state_update(self):
        """Broadcast state update to all connected clients"""
        if not self.active_connections:
            return
           
        state_data = {
            'type': 'state_update',
            'current_task': self.current_task,
            'task_history': list(self.task_history),
            'interaction_log': list(self.interaction_log),
            'task_stats': self.task_stats,
            'disambiguation_active': self.disambiguation_active,
            'disambiguation_data': self.disambiguation_data,
            'timestamp': datetime.now().isoformat()
        }
       
        message = json.dumps(state_data, ensure_ascii=False)
        disconnected = []
       
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
       
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
   
    def _schedule_broadcast(self):
        """Safely schedule broadcast updates - simplified version"""
        if not self.active_connections:
            return  # No connected clients, no need to broadcast
           
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self.broadcast_state_update())
            # print("WebSocket push scheduled")
            return
        except RuntimeError:
            # No event loop, use a simplified thread pool method
            import concurrent.futures
            import threading
           
            # Use a thread pool executor to avoid creating too many threads
            if not hasattr(self, '_executor'):
                self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="dashboard-broadcast")
           
            def broadcast_sync():
                try:
                    # Create a temporary event loop
                    loop = asyncio.new_event_loop()
                    try:
                        loop.run_until_complete(self.broadcast_state_update())
                        # print("Data pushed to Dashboard")
                    finally:
                        loop.close()
                except Exception as e:
                    print(f"Push failed: {e}")
           
            # Submit to thread pool
            self._executor.submit(broadcast_sync)
   
    def start_task(self, task_data: Dict):
        """Start a new task"""
        self.current_task = {
            'id': task_data.get('identity', 'unknown'),
            'name': task_data.get('taskquery', 'Unknown task'),
            'scene': task_data.get('scene', 'Unknown'),
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'step_count': 0,
            'max_steps': task_data.get('max_steps', 20)
        }
       
        self.task_stats['current_task_index'] += 1
       
        # Clear interaction log
        self.interaction_log.clear()
        self.disambiguation_active = False
        self.disambiguation_data = None
       
        # Schedule broadcast if event loop is running
        self._schedule_broadcast()
   
    def add_interaction(self, interaction_data: Dict):
        """Add interaction log entry"""
        interaction = {
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'type': interaction_data.get('type', 'action'),
            'action': interaction_data.get('action', ''),
            'content': interaction_data.get('content', ''),
            'image_path': interaction_data.get('image_path', ''),
            'step': interaction_data.get('step', 0)
        }
       
        self.interaction_log.append(interaction)
       
        # Update current task step count
        if self.current_task:
            self.current_task['step_count'] = interaction.get('step', 0)
       
        # Schedule broadcast if event loop is running
        self._schedule_broadcast()
   
    def complete_task(self, success: bool, result_data: Dict = None):
        """Complete the current task"""
        if not self.current_task:
            return
           
        self.current_task.update({
            'status': 'completed' if success else 'failed',
            'end_time': datetime.now().isoformat(),
            'success': success,
            'result': result_data or {}
        })
       
        # Add to history
        self.task_history.append(self.current_task.copy())
       
        # Update stats
        self.task_stats['total_tasks'] = len(self.task_history)
        if success:
            self.task_stats['completed_tasks'] += 1
        else:
            self.task_stats['failed_tasks'] += 1
           
        # Schedule broadcast if event loop is running
        self._schedule_broadcast()
       
        # Clear current task
        self.current_task = None
   
    def start_disambiguation(self, disambiguation_data: Dict):
        """Start multi-object disambiguation"""
        self.disambiguation_active = True
        self.disambiguation_data = disambiguation_data
        self.user_selection = None
        # Schedule broadcast if event loop is running
        self._schedule_broadcast()
   
    def set_user_selection(self, selection: int):
        """Set user selection"""
        self.user_selection = selection
        self.disambiguation_active = False
        self.disambiguation_data = None
        # Schedule broadcast if event loop is running
        self._schedule_broadcast()
   
    def add_vlm_call(self, vlm_data: Dict):
        """Add VLM call record - enhanced version"""
        analysis_type = vlm_data.get('analysis_type', 'general')
       
        if vlm_data.get('success', True):  # Successful VLM call
            action_text = f"VLM Analysis: {analysis_type}"
            if 'duration' in vlm_data:
                action_text += f" ({vlm_data['duration']}s)"
               
            content_parts = []
            if 'response_preview' in vlm_data:
                content_parts.append(f"Response: {vlm_data['response_preview']}")
            if 'prompt_preview' in vlm_data:
                content_parts.append(f"Prompt: {vlm_data['prompt_preview']}")
            if 'confidence' in vlm_data:
                content_parts.append(f"Confidence: {vlm_data['confidence']}%")
               
            content = " | ".join(content_parts)
           
        else:  # Failed VLM call
            action_text = f"VLM Analysis Failed: {analysis_type}"
            if 'duration' in vlm_data:
                action_text += f" ({vlm_data['duration']}s)"
            content = f"Error: {vlm_data.get('error', 'Unknown error')}"
       
        self.add_interaction({
            'type': 'vlm_call',
            'action': action_text,
            'content': content,
            'image_path': vlm_data.get('image_path', ''),
            'step': vlm_data.get('step', 0),
            'vlm_details': vlm_data
        })


# Global monitor instance
monitor = AgentMonitor()


def create_dashboard_html():
    """Generate dashboard HTML"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Embodied Agent Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
       
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }
       
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
       
        .header h1 {
            font-size: 2em;
            margin-bottom: 10px;
        }
       
        .status-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 20px;
            background: white;
            margin: 0 20px 20px 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
       
        .status-card {
            text-align: center;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9ff;
            border-left: 4px solid #667eea;
        }
       
        .status-card h3 { color: #667eea; font-size: 1.1em; margin-bottom: 8px; }
        .status-card .value { font-size: 1.5em; font-weight: bold; color: #2c3e50; }
        .status-card .label { font-size: 0.9em; color: #7f8c8d; }
       
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin: 10px 0;
        }
       
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
       
        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin: 0 20px;
        }
       
        .panel {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
       
        .panel h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
            border-bottom: 2px solid #f1f3f4;
            padding-bottom: 10px;
        }
       
        .task-history {
            max-height: 400px;
            overflow-y: auto;
        }
       
        .task-item {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            border-left: 4px solid;
            background: #f8f9ff;
        }
       
        .task-item.completed { border-left-color: #27ae60; }
        .task-item.failed { border-left-color: #e74c3c; }
        .task-item.running { border-left-color: #f39c12; animation: pulse 2s infinite; }
       
        .task-item .task-name { font-weight: bold; margin-bottom: 5px; }
        .task-item .task-meta { font-size: 0.85em; color: #7f8c8d; }
       
        .interaction-log {
            max-height: 500px;
            overflow-y: auto;
        }
       
        .interaction-item {
            padding: 10px;
            margin: 5px 0;
            border-radius: 6px;
            border-left: 3px solid;
            background: #fafbfc;
        }
       
        .interaction-item.action { border-left-color: #3498db; }
        .interaction-item.vlm_call { border-left-color: #9b59b6; }
        .interaction-item.navigate { border-left-color: #e67e22; }
       
        .interaction-item .timestamp {
            float: right;
            font-size: 0.8em;
            color: #95a5a6;
        }
       
        .disambiguation-panel {
            margin-top: 20px;
            padding: 20px;
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
        }
       
        .candidate-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 15px 0;
        }
       
        .candidate-card {
            border: 2px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
       
        .candidate-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        .candidate-card.high-confidence { border-color: #27ae60; }
        .candidate-card.medium-confidence { border-color: #f39c12; }
        .candidate-card.low-confidence { border-color: #e74c3c; }
       
        .candidate-image {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 4px;
            margin-bottom: 10px;
        }
       
        .select-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9em;
        }
       
        .select-btn:hover { background: #5a6fd8; }
       
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
       
        .hidden { display: none; }
       
        @media (max-width: 768px) {
            .main-content { grid-template-columns: 1fr; }
            .status-bar { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Embodied Agent Monitor</h1>
        <p>Real-time monitoring of AI2-THOR navigation tasks</p>
    </div>
   
    <div class="status-bar">
        <div class="status-card">
            <h3>Current Task</h3>
            <div class="value" id="current-task-name">Waiting...</div>
            <div class="label" id="current-task-scene"></div>
        </div>
        <div class="status-card">
            <h3>Task Progress</h3>
            <div class="value" id="task-progress">0 / 0</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
            </div>
        </div>
        <div class="status-card">
            <h3>Success Rate</h3>
            <div class="value" id="success-rate">0%</div>
            <div class="label">Completed Tasks</div>
        </div>
        <div class="status-card">
            <h3>System Status</h3>
            <div class="value" id="system-status">Ready</div>
            <div class="label" id="connection-status">WebSocket: Connecting...</div>
        </div>
    </div>
   
    <div class="main-content">
        <div class="panel">
            <h2>Task History</h2>
            <div class="task-history" id="task-history">
                <div style="text-align: center; color: #7f8c8d; padding: 20px;">
                    No task history available
                </div>
            </div>
        </div>
       
        <div class="panel">
            <h2>Real-time Interaction Log</h2>
            <div class="interaction-log" id="interaction-log">
                <div style="text-align: center; color: #7f8c8d; padding: 20px;">
                    Waiting for interaction data...
                </div>
            </div>
        </div>
    </div>
   
    <div class="disambiguation-panel hidden" id="disambiguation-panel">
        <h2>Multi-Object Disambiguation</h2>
        <p id="disambiguation-task">Please select the most suitable object from the candidates below:</p>
        <div class="candidate-grid" id="candidate-grid">
                    </div>
    </div>
   
    <script>
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
    </script>
</body>
</html>
'''


if FASTAPI_AVAILABLE:
    # FastAPI Application
    app = FastAPI(title="Embodied Agent Monitor", description="Real-time monitoring dashboard")
   
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        return create_dashboard_html()
   
    @app.get("/api/state")
    async def get_current_state():
        """Provide current state REST API for polling"""
        state_data = {
            'type': 'state_update',
            'current_task': monitor.current_task,
            'task_history': list(monitor.task_history),
            'interaction_log': list(monitor.interaction_log),
            'task_stats': monitor.task_stats,
            'disambiguation_active': monitor.disambiguation_active,
            'disambiguation_data': monitor.disambiguation_data,
            'timestamp': datetime.now().isoformat()
        }
        return state_data
   
    @app.get("/image/{image_path:path}")
    async def serve_image(image_path: str):
        """Serve image files"""
        try:
            # Security check to prevent path traversal
            if ".." in image_path or image_path.startswith("/"):
                raise HTTPException(status_code=403, detail="Access denied")
               
            full_path = os.path.join("/home/jiajunliu/embodied_reasoner", image_path)
           
            if os.path.exists(full_path) and os.path.isfile(full_path):
                return FileResponse(full_path)
            else:
                raise HTTPException(status_code=404, detail="Image not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
   
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await monitor.connect(websocket)
        try:
            while True:
                # Receive client message
                data = await websocket.receive_text()
                message = json.loads(data)
               
                # Process user selection
                if message.get('type') == 'user_selection':
                    monitor.set_user_selection(message.get('selection'))
                   
        except WebSocketDisconnect:
            monitor.disconnect(websocket)


def start_dashboard_server(port: int = 8888, auto_open: bool = True):
    if not FASTAPI_AVAILABLE:
        print("FastAPI not installed. Please install with: pip install fastapi uvicorn websockets")
        return None
   
    def run_server():
        try:
            uvicorn.run(app, host="0.0.0.0", port=port, log_level="error")
        except Exception as e:
            print(f"Dashboard server failed to start: {e}")
   
    # Start the server thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
   
    # Wait for the server to start
    time.sleep(2)
   
    url = f"http://localhost:{port}"
    print(f"Dashboard available at: {url}")
   
    if auto_open:
        try:
            webbrowser.open(url)
            print("Browser opened automatically")
        except:
            print("Could not auto-open browser, please visit the URL manually")
   
    return server_thread


# Convenient global functions for RocAgent to call
def log_task_start(task_data: Dict):
    """Log task start"""
    monitor.start_task(task_data)

def log_interaction(interaction_data: Dict):
    """Log interaction"""
    monitor.add_interaction(interaction_data)

def log_task_complete(success: bool, result_data: Dict = None):
    """Log task completion"""
    monitor.complete_task(success, result_data)

def log_vlm_call(vlm_data: Dict):
    """Log VLM call"""
    monitor.add_vlm_call(vlm_data)

def start_disambiguation_web(disambiguation_data: Dict) -> Optional[int]:
    try:
        #  print(f"Starting Web disambiguation interface for: {disambiguation_data.get('object_type', 'Object')}")
        monitor.start_disambiguation(disambiguation_data)
       
        timeout = 30
        start_time = time.time()
       
        while monitor.user_selection is None:
            time.sleep(0.5)
            if time.time() - start_time > timeout:
                print(f"Web disambiguation timed out ({timeout}s), using smart recommendation")
                # Timeout, use the highest confidence option
                if disambiguation_data.get('candidates'):
                    best_idx = max(range(len(disambiguation_data['candidates'])),
                                 key=lambda i: disambiguation_data['candidates'][i].get('confidence', 0))
                    selection = best_idx + 1
                    monitor.set_user_selection(selection)
                    print(f"Automatically selected highest confidence option: Option {selection}")
                else:
                    # If no candidates, return 1 as default
                    monitor.set_user_selection(1)
                    print(f"No candidates, using default option: Option 1")
                break
       
        result = monitor.user_selection
        print(f"Web disambiguation completed, selection: Option {result}")
        return result
       
    except Exception as e:
        print(f"Web disambiguation failed: {e}")
        return 1


if __name__ == "__main__":
    print("Starting Web Dashboard test server...")
    start_dashboard_server(port=8888, auto_open=True)
   
    # Simulate some test data
    test_task = {
        'identity': 'test_1',
        'taskquery': 'Find the CreditCard in the room',
        'scene': 'FloorPlan1',
        'max_steps': 20
    }
   
    log_task_start(test_task)
   
    # Keep the server running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDashboard server stopped")