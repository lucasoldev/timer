Aqui está o README em inglês para o seu projeto:

```markdown
# ⏱️ Presentation Timer

A real-time presentation timer built with **Python**, inspired by [Stagetimer.io](https://stagetimer.io). Control countdowns, send messages to speakers, and customize colors — all through a clean web interface.

> **Why Python?** Stagetimer.io is a fantastic tool, but I wanted to build my own version using Python to have full control over the backend, understand real-time communication patterns, and create a self-hosted solution.


## ✨ Features

- **Real-time countdown** — Start, pause, reset timers with instant updates via WebSocket
- **Dual interface** — Separate Control Panel and Speaker Display views
- **Color-coded alerts** — Timer automatically changes color based on remaining time:
  - 🟢 Green — Plenty of time
  - 🟡 Yellow — Warning threshold
  - 🔴 Red — Danger zone  
  - ⬛ Expired — Time's up
- **Customizable thresholds** — Set when colors change (in minutes)
- **Custom colors** — Pick any color for each time zone via color pickers
- **Speaker messages** — Send real-time messages that appear on the display, inheriting the timer's current color
- **Time presets** — Quick-select buttons for common durations (3, 5, 10, 15, 20, 30, 45, 60 minutes)
- **Add extra time** — Quickly add +1 or +5 minutes during a presentation
- **Progress bar** — Visual indicator of elapsed vs remaining time
- **Auto alerts** — Audio/visual warnings at 60s, 30s, and 10s remaining
- **Session-based** — Multiple concurrent timers via unique session IDs
- **Dark theme** — Clean, modern dark UI for both controller and display
- **Responsive** — Works on desktop, tablet, and mobile browsers


## 🎥 How It Works

```
┌─────────────────────┐         WebSocket         ┌─────────────────────┐
│   CONTROL PANEL     │ ◄──────────────────────►  │   SPEAKER DISPLAY   │
│   (Controller)      │     Real-time updates     │   (Fullscreen)      │
│                     │                           │                     │
│  • Start/Pause      │                           │  • Large timer      │
│  • Set time         │                           │  • Color changes    │
│  • Send messages    │                           │  • Messages         │
│  • Configure colors │                           │  • Progress bar     │
└─────────────────────┘                           └─────────────────────┘
          │                                                 │
          │              Python Backend                      │
          └──────────────┬──────────────────────────────────┘
                         │
               ┌─────────▼─────────┐
               │   FastAPI Server   │
               │   + Socket.IO      │
               │   + Jinja2         │
               │                    │
               │  TimerManager      │
               │  • Countdown logic │
               │  • Color logic     │
               │  • Session mgmt    │
               └────────────────────┘
```


## 🚀 Quick Start

### Prerequisites

- Python 3.9+

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/presentation-timer.git
cd presentation-timer

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

### Usage

1. Open the **Control Panel**: [http://localhost:8000/controller](http://localhost:8000/controller)
2. Click **"New"** to generate a session ID
3. Open the **Speaker Display**: [http://localhost:8000/display?session=YOUR_SESSION_ID](http://localhost:8000/display?session=YOUR_SESSION_ID)
4. Control the timer from the panel — changes appear instantly on the display


## 🛠️ Configuration

All default settings are in `server.py`, inside the `TimerManager` class. Everything is configured in **minutes**:

```python
class TimerManager:
    # ⏱️ DEFAULT TIMES (in minutes)
    DEFAULT_TOTAL_MINUTES = 5          # Total timer duration
    DEFAULT_WARNING_MINUTES = 2        # When timer turns yellow
    DEFAULT_DANGER_MINUTES = 1         # When timer turns red
    
    # 🎨 DEFAULT COLORS
    DEFAULT_COLORS = {
        'normal': '#00ff00',           # Green
        'warning': '#ffaa00',          # Yellow/Orange
        'danger': '#ff4444',           # Light Red
        'expired': '#ff0000',          # Strong Red
    }
    
    # 🎯 TIME PRESETS (available quick-select buttons)
    TIME_PRESETS = [3, 5, 10, 15, 20, 30, 45, 60]
```

**Examples:**

```python
# 10-minute timer, yellow at 3min, red at 1min
DEFAULT_TOTAL_MINUTES = 10
DEFAULT_WARNING_MINUTES = 3
DEFAULT_DANGER_MINUTES = 1

# 15-minute timer, yellow at 5min, red at 2min
DEFAULT_TOTAL_MINUTES = 15
DEFAULT_WARNING_MINUTES = 5
DEFAULT_DANGER_MINUTES = 2
```


## 🏗️ Architecture

```
presentation-timer/
├── server.py                 # Main server application
├── requirements.txt          # Python dependencies
├── templates/
│   ├── base.html             # Base HTML template
│   ├── home.html             # Landing page
│   ├── controller.html       # Control panel (minimal JS)
│   └── display.html          # Speaker display (minimal JS)
└── static/
    └── style.css             # All styles (dark theme)
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | Python 3.9+ | Core logic |
| **Web Framework** | FastAPI | HTTP routes, static files |
| **Templates** | Jinja2 | Server-side HTML rendering |
| **Real-time** | Socket.IO (python-socketio) | WebSocket communication |
| **Frontend JS** | Minimal vanilla JS | Only Socket.IO client + DOM updates |
| **Styling** | CSS3 | Dark theme, responsive |

### Design Decisions

- **95% Python** — All timer logic, color calculations, data formatting, and countdown happens server-side
- **Server-rendered HTML** — Jinja2 templates with template inheritance
- **Minimal JavaScript** — Browser only handles Socket.IO connection and DOM updates
- **Minutes-based config** — All settings use minutes (converted to seconds internally)
- **Session isolation** — Each session ID creates an independent timer


## 🔌 API / Socket.IO Events

### Client → Server (Controller emits)

| Event | Payload | Description |
|-------|---------|-------------|
| `create_session` | — | Creates a new timer session |
| `join_session` | `{session_id, role}` | Join as `controller` or `display` |
| `start_timer` | `{session_id}` | Starts the countdown |
| `pause_timer` | `{session_id}` | Pauses the countdown |
| `reset_timer` | `{session_id}` | Resets to total time |
| `set_timer` | `{session_id, minutes}` | Sets timer duration |
| `add_time` | `{session_id, minutes}` | Adds extra time |
| `send_message` | `{session_id, message}` | Sends message to display |
| `update_color_config` | `{session_id, colors}` | Updates color scheme |
| `update_time_thresholds` | `{session_id, warning_time, danger_time}` | Updates alert times |

### Server → Client (Broadcast)

| Event | Payload | Description |
|-------|---------|-------------|
| `timer_update` | `{time_str, color, percent, status_text, message, ...}` | Full timer state |
| `session_created` | `{session_id}` | New session ID |
| `time_alert` | `{message}` | Alert notification |


## 🎨 Customization

### Changing Colors (via UI)
1. Connect to a session
2. Go to **Color & Alert Settings** → **Colors** tab
3. Use color pickers for each zone
4. Click **Apply Colors**

### Changing Alert Times (via UI)
1. Go to **Color & Alert Settings** → **Alert Times** tab
2. Set Warning and Danger thresholds
3. Click **Apply Alert Times**

### Changing Defaults (in code)
Edit the class variables in `TimerManager` (see [Configuration](#-configuration) section above).


## 📱 Screenshots

### Control Panel
```
┌─────────────────────────────────────────┐
│  ⏱️ Timer Control          🟢 Connected │
├─────────────────────────────────────────┤
│  📡 Session                             │
│  [Session ID...] [Connect] [+ New]     │
├─────────────────────────────────────────┤
│  ⏱️ Time                                │
│  [3min] [5min] [10min] [15min] ...     │
├─────────────────────────────────────────┤
│  🎨 Color & Alert Settings              │
│  [Colors] [Alert Times]                 │
│  🟢 Normal  🟡 Warning                  │
│  🔴 Danger  ⏰ Expired                  │
├─────────────────────────────────────────┤
│  🎮 Controls                            │
│  [▶ Start] [⏸ Pause] [↺ Reset]        │
│  [+1 min] [+5 min]                      │
├─────────────────────────────────────────┤
│  💬 Message to Speaker                  │
│  [Type message...] [Send]              │
├─────────────────────────────────────────┤
│  👁️ Speaker Preview                     │
│  ┌─────────────────────────────────┐    │
│  │  ● ● ●  DISPLAY                 │    │
│  │                                 │    │
│  │          05:00                   │    │
│  │     ════════════════            │    │
│  │                                 │    │
│  │        ⏸ Paused                 │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

### Speaker Display
```
┌─────────────────────────────────────────┐
│                                         │
│                                         │
│              05:00                      │
│          ════════════════               │
│                                         │
│       "5 minutes remaining"             │
│                                         │
│           ⏸ Paused                      │
│                                         │
│                          ID: ABC123     │
└─────────────────────────────────────────┘
```


## 🔧 Dependencies

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-socketio==5.10.0
websockets==12.0
```


## 🤔 Why This Project?

[Stagetimer.io](https://stagetimer.io) is an excellent tool for managing presentation timers — it has a polished UI, great features, and real-time sync. I wanted to:

1. **Understand the architecture** behind real-time timer applications
2. **Build it in Python** to leverage FastAPI + Socket.IO instead of Node.js
3. **Have full control** over the backend logic and deployment
4. **Self-host** for events where internet access might be unreliable
5. **Learn** real-time communication patterns with WebSockets

This is **not** a clone or competitor — it's a learning project that solves the same problem with a different tech stack.


## 📝 Future Improvements

- [ ] User authentication (admin vs viewer roles)
- [ ] Multiple timers in a single session (e.g., talk + Q&A)
- [ ] Session persistence (Redis/PostgreSQL)
- [ ] Export timer logs/history
- [ ] OBS Studio integration (browser source)
- [ ] QR code for easy display access
- [ ] Custom audio alerts
- [ ] Docker image for easy deployment
- [ ] PWA support for mobile control
- [ ] Keyboard shortcuts for common actions


## 📄 License

MIT License — feel free to use, modify, and distribute.


## 🙏 Acknowledgments

- [Stagetimer.io](https://stagetimer.io) — inspiration for this project
- [FastAPI](https://fastapi.tiangolo.com/) — the amazing Python web framework
- [Socket.IO](https://socket.io/) — real-time communication made easy
- [Jinja2](https://jinja.palletsprojects.com/) — powerful templating engine


---

**Built with 🐍 Python and ❤️**
```

Esse README cobre:
- ✅ Explicação do propósito (inspirado no Stagetimer.io)
- ✅ Por que Python
- ✅ Features completas
- ✅ Quick start
- ✅ Configuração clara
- ✅ Arquitetura do projeto
- ✅ Documentação da API/Socket.IO
- ✅ Screenshots ASCII
- ✅ Dependências
- ✅ Melhorias futuras
- ✅ Agradecimentos ao Stagetimer.io