# Web UI Components

This directory contains the modular web dashboard components for the Embodied Agent Monitor.

## File Structure

```
web_ui/
├── __init__.py                 # Package initialization and exports
├── monitor.py                  # AgentMonitor class for state management
├── server.py                   # FastAPI server and API endpoints
├── README.md                   # This documentation file
├── static/                     # Static web assets
│   ├── css/
│   │   └── dashboard.css      # Main stylesheet
│   ├── js/
│   │   └── dashboard.js       # JavaScript functionality
│   └── images/                # Image assets
│       └── embodied-reasoner-logo.png  # Main logo
└── templates/
    └── dashboard.html         # Main HTML template
```

## Components

### 1. monitor.py
- `AgentMonitor` class: Manages application state
- Handles WebSocket connections
- Broadcasts state updates to clients
- Manages task history, interaction logs, and disambiguation

### 2. server.py
- FastAPI application setup
- REST API endpoints (`/api/state`, `/image/*`)
- WebSocket endpoint (`/ws`)
- Static file serving
- Server startup functions

### 3. templates/dashboard.html
- Clean HTML template without embedded CSS/JS
- Links to external stylesheets and scripts
- Semantic HTML structure

### 4. static/css/dashboard.css
- Complete CSS styling for the dashboard
- Responsive design with grid layouts
- Animation and transition effects
- Mobile-friendly media queries

### 5. static/js/dashboard.js
- WebSocket connection handling
- State update processing
- UI interaction functions
- Polling fallback mechanism

## Usage

### Basic Usage
```python
from web_ui import start_dashboard_server

# Start the server
start_dashboard_server(port=8888, auto_open=True)
```

### Logging Functions
```python
from web_ui import log_task_start, log_interaction, log_task_complete

# Log a task start
log_task_start({
    'identity': 'task_1',
    'taskquery': 'Find the apple',
    'scene': 'Kitchen',
    'max_steps': 20
})

# Log an interaction
log_interaction({
    'type': 'action',
    'action': 'MoveAhead',
    'content': 'Moving forward',
    'step': 5
})

# Log task completion
log_task_complete(success=True, result_data={'steps': 10})
```

## Customization

### Modifying Styles
Edit `static/css/dashboard.css` to change:
- Color schemes
- Layout structure
- Typography
- Animations

### Modifying Layout
Edit `templates/dashboard.html` to change:
- HTML structure
- Add new panels
- Reorganize content

### Adding Features
Edit `static/js/dashboard.js` to add:
- New UI interactions
- Additional data processing
- Custom visualizations

### Backend Changes
Edit `server.py` or `monitor.py` to:
- Add new API endpoints
- Modify state management
- Add new data processing

## Advantages of Modular Structure

1. **Better Maintainability**: Each component has a single responsibility
2. **Easier Debugging**: Issues can be isolated to specific files
3. **Improved Performance**: Browser can cache static assets
4. **Better Development**: Multiple developers can work on different parts
5. **Easier Customization**: Users can modify specific aspects without touching core logic
6. **Version Control**: Changes to different components can be tracked separately