```markdown
# ⏱️ Presentation Timer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Socket.IO-Real--time-010101?style=for-the-badge&logo=socket.io&logoColor=white" alt="Socket.IO">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <strong>A real-time presentation timer built with Python, inspired by Stagetimer.io</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-architecture">Architecture</a>
</p>

---

## 📖 About

This project is a **self-hosted presentation timer** that lets you control countdowns, send messages to speakers, and customize alert colors — all through a clean web interface.

> **Why Python?** [Stagetimer.io](https://stagetimer.io) is a fantastic tool, but I wanted to build my own version using Python to have full control over the backend, understand real-time communication patterns, and create a self-hosted solution.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔄 **Real-time sync** | Start, pause, reset timers with instant WebSocket updates |
| 🖥️ **Dual interface** | Separate Control Panel and Speaker Display views |
| 🎨 **Color-coded alerts** | Timer changes color automatically: Green → Yellow → Red → Expired |
| ⚙️ **Customizable thresholds** | Set exactly when colors change (in minutes) |
| 🎯 **Custom colors** | Pick any color for each time zone via color pickers |
| 💬 **Speaker messages** | Send real-time messages that inherit the timer's current color |
| ⏱️ **Time presets** | Quick-select buttons: 3, 5, 10, 15, 20, 30, 45, 60 min |
| ➕ **Add extra time** | Quickly add +1 or +5 minutes during a presentation |
| 📊 **Progress bar** | Visual indicator of elapsed vs remaining time |
| 🔔 **Auto alerts** | Audio/visual warnings at 60s, 30s, and 10s remaining |
| 🔗 **Session-based** | Multiple concurrent timers via unique session IDs |
| 🌙 **Dark theme** | Clean, modern dark UI for both controller and display |
| 📱 **Responsive** | Works on desktop, tablet, and mobile browsers |

---

## 🎥 How It Works

```
┌─────────────────────┐         WebSocket         ┌─────────────────────┐
│   CONTROL PANEL     │◄─────────────────────────►│   SPEAKER DISPLAY   │
│                     │     Real-time updates     │                     │
│  • Start/Pause      │                           │  • Large timer      │
│  • Set time         │                           │  • Color changes    │
│  • Send messages    │                           │  • Messages         │
│  • Configure colors │                           │  • Progress bar     │
└─────────┬───────────┘                           └──────────┬──────────┘
          │                                                  │
          │              Python Backend                      │
          └──────────────────┬───────────────────────────────┘
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

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9** or higher
- **pip** (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/presentation-timer.git
cd presentation-timer

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

### Usage

**1. Open the Control Panel**
```
http://localhost:8000/controller
```
Click **"New"** to generate a session ID.

**2. Open the Speaker Display**
```
http://localhost:8000/display?session=YOUR_SESSION_ID
```
Replace `YOUR_SESSION_ID` with the ID from step 1.

**3. Control the timer from the panel** — all changes appear instantly on the display.

---

## 🛠️ Configuration

All default settings are in `server.py`, inside the `TimerManager` class. **Everything is configured in minutes:**

```python
class TimerManager:
    # ⏱️ DEFAULT TIMES (in minutes)
    DEFAULT_TOTAL_MINUTES = 5          # Total timer duration
    DEFAULT_WARNING_MINUTES = 2        # When timer turns yellow
    DEFAULT_DANGER_MINUTES = 1         # When timer turns red

    # 🎨 DEFAULT COLORS
    DEFAULT_COLORS = {
        'normal': '#00ff00',           # Green - plenty of time
        'warning': '#ffaa00',          # Yellow/orange - attention
        'danger': '#ff4444',           # Light red - danger zone
        'expired': '#ff0000',          # Strong red - time's up
    }

    # 🎯 TIME PRESETS (quick-select buttons)
    TIME_PRESETS = [3, 5, 10, 15, 20, 30, 45, 60]
```

### Quick Examples

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

---

## 🏗️ Architecture

```
presentation-timer/
├── server.py                 # Main server (FastAPI + Socket.IO)
├── requirements.txt          # Python dependencies
├── templates/
│   ├── base.html             # Base HTML template
│   ├── home.html             # Landing page
│   ├── controller.html       # Control panel (minimal JS)
│   └── display.html          # Speaker display (fullscreen)
└── static/
    └── style.css             # All styles (dark theme)
```

### Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | Python 3.9+ | Core timer logic, session management |
| **Web Framework** | FastAPI | Fast, modern, async support |
| **Templates** | Jinja2 | Server-side HTML rendering |
| **Real-time** | python-socketio | WebSocket communication |
| **Frontend JS** | Minimal vanilla JS | Only Socket.IO client + DOM updates |
| **Styling** | CSS3 | Dark theme, responsive, animations |

### Design Philosophy

- **95% Python** — All timer logic, color calculations, and countdown run server-side
- **Server-rendered HTML** — Jinja2 with template inheritance
- **Minimal JavaScript** — Only for WebSocket connection and DOM manipulation
- **Minutes-based config** — All settings use minutes (converted to seconds internally)
- **Session isolation** — Each session ID creates an independent timer

---

## 🔌 API Reference (Socket.IO Events)

### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `create_session` | — | Creates a new timer session |
| `join_session` | `{session_id, role}` | Join as `controller` or `display` |
| `start_timer` | `{session_id}` | Starts the countdown |
| `pause_timer` | `{session_id}` | Pauses the countdown |
| `reset_timer` | `{session_id}` | Resets to total time |
| `set_timer` | `{session_id, minutes}` | Sets timer duration (in minutes) |
| `add_time` | `{session_id, minutes}` | Adds extra time (in minutes) |
| `send_message` | `{session_id, message}` | Sends message to display |
| `update_color_config` | `{session_id, colors}` | Updates color scheme |
| `update_time_thresholds` | `{session_id, warning_time, danger_time}` | Updates alert thresholds (in minutes) |

### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `timer_update` | `{time_str, color, percent, status_text, message, ...}` | Full timer state |
| `session_created` | `{session_id}` | New session ID |
| `time_alert` | `{message}` | Alert notification |

---

## 🔧 Dependencies

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
jinja2==3.1.2
python-socketio==5.10.0
websockets==12.0
```

---

## 📝 Roadmap

- [ ] User authentication (admin vs viewer roles)
- [ ] Multiple timers in a single session (talk + Q&A)
- [ ] Session persistence with Redis/PostgreSQL
- [ ] Export timer history and logs
- [ ] OBS Studio integration (browser source)
- [ ] QR code generation for easy display access
- [ ] Custom audio alerts (upload MP3)
- [ ] Docker image for one-click deployment
- [ ] PWA support for mobile control
- [ ] Keyboard shortcuts (Space to play/pause, R to reset)

---

## 🤔 Inspiration

[**Stagetimer.io**](https://stagetimer.io) is an excellent tool for managing presentation timers — polished UI, great features, real-time sync. This project was built to:

- Understand the architecture behind real-time timer applications
- Build it in Python using FastAPI + Socket.IO (instead of Node.js)
- Have full control over the backend logic and self-hosting
- Learn WebSocket communication patterns

> This is a **learning project** — not a clone or competitor. Same problem, different tech stack.

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use, modify, and distribute.

---

## 🙏 Acknowledgments

- [Stagetimer.io](https://stagetimer.io) — the inspiration
- [FastAPI](https://fastapi.tiangolo.com/) — the Python web framework
- [Socket.IO](https://socket.io/) — real-time made simple
- [Jinja2](https://jinja.palletsprojects.com/) — powerful templating

---

<p align="center">
  <strong>Built with 🐍 Python and ❤️</strong><br>
  ⭐ Star this repo if you found it useful!
</p>
```

## O que estava errado:

| Problema | Correção |
|----------|----------|
| Diagrama ASCII sem ``` | Adicionado ``` antes e depois |
| Código Python sem ```python | Adicionado ```python |
| Estrutura de pastas sem ``` | Adicionado ``` |
| Dependências sem ```txt | Adicionado ```txt |
| Faltavam `##` nos títulos | Adicionados `##` e `###` |
| Roadmap sem `- [ ]` | Adicionado formato de checklist |
| Lista de acknowledgments sem `-` | Adicionado bullets |