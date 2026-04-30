#!/usr/bin/env python3
"""
Presentation Timer - Python SaaS
Real-time timer control for speakers and presentations
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio

# ===== CONFIGURATION =====
app = FastAPI(title="Presentation Timer")

# Templates
templates = Jinja2Templates(directory="templates")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Socket.IO
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=False,
    engineio_logger=False
)
socket_app = socketio.ASGIApp(sio, app)


# ===== TIMER MANAGER =====
class TimerManager:
    """
    Manages multiple presentation timers.
    
    ⚙️ DEFAULT SETTINGS - CHANGE HERE (IN MINUTES):
    """
    
    # ==========================================
    # ⏱️ DEFAULT TIMES (in minutes)
    # ==========================================
    DEFAULT_TOTAL_MINUTES = 5          # Total time: 5 minutes
    DEFAULT_WARNING_MINUTES = 2        # Yellow warning: 2 minutes remaining
    DEFAULT_DANGER_MINUTES = 1         # Red danger: 1 minute remaining
    
    # ==========================================
    # 🎨 DEFAULT COLORS
    # ==========================================
    DEFAULT_COLORS = {
        'normal': '#00ff00',           # Green - plenty of time
        'warning': '#ffaa00',          # Yellow/orange - attention
        'danger': '#ff4444',           # Light red - danger zone
        'expired': '#ff0000',          # Strong red - time's up
    }
    
    # ==========================================
    # 💬 STATUS MESSAGES
    # ==========================================
    STATUS_MESSAGES = {
        'idle': 'Ready to start',
        'running': 'Running',
        'paused': 'Paused',
        'expired': '⏰ TIME IS UP!',
    }
    
    # ==========================================
    # 🔔 AUTO ALERTS (seconds remaining)
    # ==========================================
    ALERT_TIMES = {
        60: '⚠️ 1 minute remaining!',
        30: '⚡ 30 seconds!',
        10: '🔴 10 seconds!',
    }
    
    # ==========================================
    # 🎯 TIME PRESETS (in minutes)
    # ==========================================
    TIME_PRESETS = [3, 5, 10, 15, 20, 30, 45, 60]
    DEFAULT_PRESET_INDEX = 1  # 5 minutes (index 1)
    
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.connections: Dict[str, Dict[str, str]] = {}
        self.tasks: Dict[str, asyncio.Task] = {}
    
    # ==========================================
    # INTERNAL CONVERSION (minutes ↔ seconds)
    # ==========================================
    
    def _min_to_sec(self, minutes: int) -> int:
        """Convert minutes to seconds (internal use)"""
        return minutes * 60
    
    def _sec_to_min(self, seconds: int) -> int:
        """Convert seconds to minutes (internal use)"""
        return seconds // 60
    
    # ==========================================
    # SESSION MANAGEMENT
    # ==========================================
    
    def create_session(self) -> dict:
        """Create a new timer session"""
        session_id = str(uuid.uuid4())[:8].upper()
        
        # Convert minutes to seconds internally
        total_seconds = self._min_to_sec(self.DEFAULT_TOTAL_MINUTES)
        warning_seconds = self._min_to_sec(self.DEFAULT_WARNING_MINUTES)
        danger_seconds = self._min_to_sec(self.DEFAULT_DANGER_MINUTES)
        
        self.sessions[session_id] = {
            'session_id': session_id,
            
            # Internal storage in seconds
            'total_time': total_seconds,
            'remaining': total_seconds,
            'is_running': False,
            'message': '',
            'color': self.DEFAULT_COLORS['normal'],
            'warning_time': warning_seconds,
            'danger_time': danger_seconds,
            'color_config': dict(self.DEFAULT_COLORS),  # Copy
            
            # Metadata
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
        }
        
        self.connections[session_id] = {}
        print(f"✅ Session created: {session_id} | "
              f"Time: {self.DEFAULT_TOTAL_MINUTES}min | "
              f"Warning: {self.DEFAULT_WARNING_MINUTES}min | "
              f"Danger: {self.DEFAULT_DANGER_MINUTES}min")
        
        return self.sessions[session_id]
    
    # ==========================================
    # DISPLAY DATA FORMATTING
    # ==========================================
    
    def get_timer_display_data(self, session_id: str) -> dict:
        """Returns formatted data for frontend display"""
        timer = self.sessions.get(session_id)
        if not timer:
            return None
        
        remaining = timer['remaining']
        total = timer['total_time']
        
        # Formatted time
        minutes = remaining // 60
        seconds = remaining % 60
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Current color
        color = self._get_current_color(timer)
        
        # Progress bar percentage
        percent = int((remaining / total) * 100) if total > 0 else 0
        
        # Status
        if remaining <= 0:
            status_text = self.STATUS_MESSAGES['expired']
            status_icon = "🔴"
            is_pulsing = True
            is_shaking = True
        elif timer['is_running']:
            status_text = self.STATUS_MESSAGES['running']
            status_icon = "▶️"
            is_pulsing = remaining <= 10
            is_shaking = False
        else:
            status_text = self.STATUS_MESSAGES['paused']
            status_icon = "⏸️"
            is_pulsing = False
            is_shaking = False
        
        # Message inherits timer color
        message = timer.get('message', '')
        message_color = color
        
        # Threshold times in minutes (for display)
        warning_minutes = self._sec_to_min(timer['warning_time'])
        danger_minutes = self._sec_to_min(timer['danger_time'])
        total_minutes = self._sec_to_min(timer['total_time'])
        
        return {
            # Timer
            'time_str': time_str,
            'minutes': minutes,
            'seconds': seconds,
            'remaining': remaining,
            'total_time': total,
            'percent': percent,
            
            # Colors
            'color': color,
            'message_color': message_color,
            
            # Status
            'status_text': status_text,
            'status_icon': status_icon,
            'is_running': timer['is_running'],
            'is_pulsing': is_pulsing,
            'is_shaking': is_shaking,
            
            # Message
            'message': message,
            
            # Settings (in minutes for display)
            'total_minutes': total_minutes,
            'warning_minutes': warning_minutes,
            'danger_minutes': danger_minutes,
            'color_config': timer.get('color_config', self.DEFAULT_COLORS),
        }
    
    def _get_current_color(self, timer: dict) -> str:
        """Determine current color based on remaining time"""
        remaining = timer['remaining']
        colors = timer.get('color_config', self.DEFAULT_COLORS)
        
        if remaining <= 0:
            return colors.get('expired', self.DEFAULT_COLORS['expired'])
        elif remaining <= timer.get('danger_time', self._min_to_sec(self.DEFAULT_DANGER_MINUTES)):
            return colors.get('danger', self.DEFAULT_COLORS['danger'])
        elif remaining <= timer.get('warning_time', self._min_to_sec(self.DEFAULT_WARNING_MINUTES)):
            return colors.get('warning', self.DEFAULT_COLORS['warning'])
        else:
            return colors.get('normal', self.DEFAULT_COLORS['normal'])


# Global instance
manager = TimerManager()


# ===== HTTP ROUTES =====

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page"""
    return templates.TemplateResponse("home.html", {
        "request": request
    })


@app.get("/controller", response_class=HTMLResponse)
async def controller_page(request: Request):
    """Controller panel"""
    return templates.TemplateResponse("controller.html", {
        "request": request,
        "presets": TimerManager.TIME_PRESETS,
        "default_preset": TimerManager.TIME_PRESETS[TimerManager.DEFAULT_PRESET_INDEX],
        "colors": TimerManager.DEFAULT_COLORS,
        "warning_minutes": TimerManager.DEFAULT_WARNING_MINUTES,
        "danger_minutes": TimerManager.DEFAULT_DANGER_MINUTES,
        "default_minutes": TimerManager.DEFAULT_TOTAL_MINUTES,
    })


@app.get("/display", response_class=HTMLResponse)
async def display_page(request: Request, session: str = Query(None)):
    """Speaker display screen"""
    if not session:
        return templates.TemplateResponse("display.html", {
            "request": request,
            "session_id": None,
            "error": "Session not specified. Use ?session=SESSION_ID"
        })
    
    # Create session if it doesn't exist
    if session not in manager.sessions:
        manager.sessions[session] = {
            'session_id': session,
            'total_time': manager._min_to_sec(TimerManager.DEFAULT_TOTAL_MINUTES),
            'remaining': manager._min_to_sec(TimerManager.DEFAULT_TOTAL_MINUTES),
            'is_running': False,
            'message': '',
            'color': TimerManager.DEFAULT_COLORS['normal'],
            'warning_time': manager._min_to_sec(TimerManager.DEFAULT_WARNING_MINUTES),
            'danger_time': manager._min_to_sec(TimerManager.DEFAULT_DANGER_MINUTES),
            'color_config': dict(TimerManager.DEFAULT_COLORS),
            'created_at': datetime.now().isoformat(),
        }
        manager.connections[session] = {}
    
    display_data = manager.get_timer_display_data(session)
    
    return templates.TemplateResponse("display.html", {
        "request": request,
        "session_id": session,
        "display_data": display_data,
        "error": None
    })


# ===== SOCKET.IO EVENTS =====

@sio.event
async def connect(sid, environ):
    print(f"🔌 Connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"🔌 Disconnected: {sid}")
    for session_id, connections in manager.connections.items():
        for role, conn_sid in list(connections.items()):
            if conn_sid == sid:
                del manager.connections[session_id][role]

@sio.event
async def create_session(sid):
    """Create a new session"""
    session = manager.create_session()
    await sio.emit('session_created', {
        'session_id': session['session_id']
    }, to=sid)

@sio.event
async def join_session(sid, data):
    """Join an existing session"""
    session_id = data.get('session_id')
    role = data.get('role', 'display')
    
    if session_id not in manager.sessions:
        # Create session if it doesn't exist
        manager.sessions[session_id] = {
            'session_id': session_id,
            'total_time': manager._min_to_sec(TimerManager.DEFAULT_TOTAL_MINUTES),
            'remaining': manager._min_to_sec(TimerManager.DEFAULT_TOTAL_MINUTES),
            'is_running': False,
            'message': '',
            'color': TimerManager.DEFAULT_COLORS['normal'],
            'warning_time': manager._min_to_sec(TimerManager.DEFAULT_WARNING_MINUTES),
            'danger_time': manager._min_to_sec(TimerManager.DEFAULT_DANGER_MINUTES),
            'color_config': dict(TimerManager.DEFAULT_COLORS),
            'created_at': datetime.now().isoformat(),
        }
        manager.connections[session_id] = {}
    
    manager.connections[session_id][role] = sid
    
    # Send current formatted state
    display_data = manager.get_timer_display_data(session_id)
    await sio.emit('timer_update', display_data, to=sid)
    print(f"👤 {role} joined session {session_id}")

@sio.event
async def start_timer(sid, data):
    """Start the timer"""
    session_id = data.get('session_id')
    if session_id not in manager.sessions:
        return
    
    manager.sessions[session_id]['is_running'] = True
    
    # Cancel previous countdown task if exists
    if session_id in manager.tasks:
        manager.tasks[session_id].cancel()
    
    # Start countdown
    manager.tasks[session_id] = asyncio.create_task(countdown(session_id))
    await broadcast(session_id)
    print(f"▶️ Timer started: {session_id}")

@sio.event
async def pause_timer(sid, data):
    """Pause the timer"""
    session_id = data.get('session_id')
    if session_id not in manager.sessions:
        return
    
    manager.sessions[session_id]['is_running'] = False
    if session_id in manager.tasks:
        manager.tasks[session_id].cancel()
    
    await broadcast(session_id)
    print(f"⏸️ Timer paused: {session_id}")

@sio.event
async def reset_timer(sid, data):
    """Reset the timer"""
    session_id = data.get('session_id')
    if session_id not in manager.sessions:
        return
    
    session = manager.sessions[session_id]
    session['remaining'] = session['total_time']
    session['is_running'] = False
    session['message'] = ''
    
    if session_id in manager.tasks:
        manager.tasks[session_id].cancel()
    
    await broadcast(session_id)
    print(f"🔄 Timer reset: {session_id}")

@sio.event
async def set_timer(sid, data):
    """
    Set timer duration.
    Receives minutes (int), converts to seconds internally.
    """
    session_id = data.get('session_id')
    minutes = data.get('minutes', TimerManager.DEFAULT_TOTAL_MINUTES)
    
    if session_id not in manager.sessions:
        return
    
    # Convert minutes to seconds
    total_seconds = manager._min_to_sec(minutes)
    
    session = manager.sessions[session_id]
    session['total_time'] = total_seconds
    session['remaining'] = total_seconds
    session['is_running'] = False
    
    if session_id in manager.tasks:
        manager.tasks[session_id].cancel()
    
    await broadcast(session_id)
    print(f"⏱️ Timer set: {session_id} → {minutes} minutes")

@sio.event
async def add_time(sid, data):
    """
    Add time to the timer.
    Receives minutes (int), converts to seconds internally.
    """
    session_id = data.get('session_id')
    minutes = data.get('minutes', 1)
    
    if session_id not in manager.sessions:
        return
    
    # Convert to seconds
    seconds_to_add = manager._min_to_sec(minutes)
    manager.sessions[session_id]['remaining'] += seconds_to_add
    
    await broadcast(session_id)
    print(f"⏰ +{minutes}min added: {session_id}")

@sio.event
async def send_message(sid, data):
    """Send a message to the display"""
    session_id = data.get('session_id')
    message = data.get('message', '')
    
    if session_id not in manager.sessions:
        return
    
    manager.sessions[session_id]['message'] = message
    await broadcast(session_id)
    print(f"💬 Message to {session_id}: '{message}'")

@sio.event
async def update_color_config(sid, data):
    """Update color configuration"""
    session_id = data.get('session_id')
    colors = data.get('colors', {})
    
    if session_id not in manager.sessions:
        return
    
    manager.sessions[session_id]['color_config'] = colors
    await broadcast(session_id)
    print(f"🎨 Colors updated: {session_id}")

@sio.event
async def update_time_thresholds(sid, data):
    """
    Update warning and danger time thresholds.
    Receives minutes (int), converts to seconds internally.
    """
    session_id = data.get('session_id')
    warning_minutes = data.get('warning_time', TimerManager.DEFAULT_WARNING_MINUTES)
    danger_minutes = data.get('danger_time', TimerManager.DEFAULT_DANGER_MINUTES)
    
    if session_id not in manager.sessions:
        return
    
    # Convert minutes to seconds
    manager.sessions[session_id]['warning_time'] = manager._min_to_sec(warning_minutes)
    manager.sessions[session_id]['danger_time'] = manager._min_to_sec(danger_minutes)
    
    await broadcast(session_id)
    print(f"⏰ Thresholds updated: {session_id} → warning: {warning_minutes}min, danger: {danger_minutes}min")


# ===== COUNTDOWN LOGIC =====

async def countdown(session_id: str):
    """Countdown loop"""
    try:
        while (session_id in manager.sessions and
               manager.sessions[session_id]['is_running'] and
               manager.sessions[session_id]['remaining'] > 0):
            
            await asyncio.sleep(1)
            
            if session_id not in manager.sessions:
                break
            
            session = manager.sessions[session_id]
            if not session['is_running']:
                break
            
            session['remaining'] -= 1
            await broadcast(session_id)
            
            # Auto alerts
            remaining = session['remaining']
            if remaining in TimerManager.ALERT_TIMES:
                await broadcast_alert(session_id, TimerManager.ALERT_TIMES[remaining])
        
        # Timer reached zero
        if session_id in manager.sessions:
            manager.sessions[session_id]['is_running'] = False
            await broadcast_alert(session_id, "⏰ TIME IS UP!")
            await broadcast(session_id)
            
    except asyncio.CancelledError:
        pass


async def broadcast(session_id: str):
    """Broadcast timer data to all clients in the session"""
    if session_id not in manager.connections:
        return
    
    display_data = manager.get_timer_display_data(session_id)
    connections = manager.connections[session_id]
    
    for role, sid in connections.items():
        try:
            await sio.emit('timer_update', display_data, to=sid)
        except:
            pass


async def broadcast_alert(session_id: str, message: str):
    """Send alert to display clients"""
    if session_id not in manager.connections:
        return
    
    connections = manager.connections[session_id]
    if 'display' in connections:
        try:
            await sio.emit('time_alert', {'message': message}, 
                          to=connections['display'])
        except:
            pass


# ===== STARTUP =====

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("🐍 Presentation Timer - Python SaaS")
    print("=" * 60)
    print(f"\n⚙️  Default Settings:")
    print(f"   ⏱️  Total time: {TimerManager.DEFAULT_TOTAL_MINUTES} minutes")
    print(f"   ⚠️  Warning alert: {TimerManager.DEFAULT_WARNING_MINUTES} minutes")
    print(f"   🔴  Danger alert: {TimerManager.DEFAULT_DANGER_MINUTES} minutes")
    print(f"   🎨  Colors: Green → Yellow → Red")
    print(f"\n📡 URLs:")
    print(f"   Home:       http://localhost:8000")
    print(f"   Controller: http://localhost:8000/controller")
    print(f"   Display:    http://localhost:8000/display?session=ID")
    print(f"\n✨ Python server running...\n")
    
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, log_level="info")