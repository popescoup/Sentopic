# Sentopic

Reddit analytics software for finding and validating business opportunities. Sentopic collects Reddit posts and comments, runs keyword-based sentiment analysis, maps co-occurrences and mention/sentiment trends, and surfaces insights through an AI-powered chat interface.

Built as an Electron desktop app with a Python (FastAPI) backend and React frontend.

---

## What It Does

- **Collect** — Pull posts and comments from any subreddit via the Reddit API
- **Analyze** — Track keywords, measure sentiment (VADER), and map co-occurrence relationships
- **Visualize** — Explore trends, keyword networks, and discussion timelines
- **Ask** — Chat with your data using an LLM-powered assistant (Anthropic or OpenAI)

---

## Getting the App

Pre-built installers for macOS are available on the [releases page](../../releases). For installation and usage instructions, see the [documentation](https://sentopic.io/pages/documentation).

The rest of this README is for contributors and developers who want to run or build Sentopic from source.

---

## Running from Source

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Reddit API app ([create one here](https://www.reddit.com/prefs/apps) — select "script" type)
- An Anthropic or OpenAI API key (optional, required for AI features)

> **Note on PyTorch**: `requirements.txt` includes `torch`, which is a large dependency (~2GB). Installation may take several minutes. If you only need the core sentiment analysis features and not local embeddings, you can skip torch — but AI-powered features will be limited.

### 1. Clone and configure

```bash
git clone https://github.com/popescoup/Sentopic.git
cd sentopic
```

Copy the example config and fill in your credentials:

```bash
cp config.example.json config.json
```

Open `config.json` and add your Reddit API credentials and optionally your LLM API key. See [Configuration](#configuration) below for details.

### 2. Set up the Python backend

```bash
python -m venv sentopic-env
source sentopic-env/bin/activate        # macOS/Linux
# sentopic-env\Scripts\activate.bat     # Windows

pip install -r requirements.txt
```

> The first run will also download the `all-MiniLM-L6-v2` sentence transformer model (~90MB) from HuggingFace when embeddings are first used.

### 3. Set up the frontend

```bash
cd frontend
npm install
```

### 4. Run in development mode

You'll need two terminals:

**Terminal 1 — Backend:**
```bash
source sentopic-env/bin/activate
python run_api.py
# API runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
# Open the URL shown in the terminal (typically http://localhost:5173)
```

---

## Building the Packaged App

The full build chains PyInstaller (Python → binary) → Vite (React → static assets) → electron-builder (→ `.dmg` / `.exe`).

### Prerequisites

Complete the [Running from Source](#running-from-source) setup first, then:

```bash
cd electron
npm install
```

### macOS

```bash
cd electron
npm run build
```

Output: `electron/dist/Sentopic-1.0.0-arm64.dmg` and `Sentopic-1.0.0.dmg` (Intel)

> **Code signing**: By default the build is unsigned. macOS users will see an "unidentified developer" warning on first launch, which can be bypassed by right-clicking → Open. See the [macOS installation guide](docs/installation/macos-installation.md) for details. If you have an Apple Developer certificate, set `"identity"` in `electron/package.json` to your identity string.

### Windows

```bash
cd electron
npm run dist:win
```

Output: `electron/dist/Sentopic-1.0.0.exe`

> Windows builds can also be produced on macOS using Wine, but native Windows is recommended.

### What the build does

1. `scripts/build-python.sh` (or `.bat`) — packages the Python backend into a standalone binary via PyInstaller
2. `cd frontend && npm run build` — compiles the React app and copies it to `electron/frontend-dist/`
3. `electron-builder` — wraps everything into a platform installer

---

## Configuration

Copy `config.example.json` to `config.json` and fill in your values:

```json
{
    "reddit": {
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "user_agent": "Sentopic:v1.0 (by u/yourusername)"
    },
    "llm": {
        "enabled": true,
        "default_provider": "anthropic",
        "providers": {
            "anthropic": {
                "api_key": "YOUR_ANTHROPIC_API_KEY"
            },
            "openai": {
                "api_key": "YOUR_OPENAI_API_KEY"
            }
        }
    }
}
```

**Reddit credentials** — Required for all data collection. Create a "script" type app at [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps).

**LLM API key** — Optional. Required for keyword suggestions, AI summaries, and the chat assistant. Configure either Anthropic or OpenAI, not both. LLM features are disabled gracefully if no key is provided.

`config.json` is gitignored and never committed.

---

## Architecture

```
sentopic/
├── api.py                  # FastAPI app entry point
├── run_api.py              # Dev server runner
├── src/
│   ├── analytics/          # Sentiment, keyword, trend, co-occurrence analysis
│   ├── llm/                # LLM providers, embeddings, RAG, chat agent
│   ├── api/                # API models and services
│   ├── collector.py        # Reddit data collection via PRAW
│   ├── database.py         # SQLAlchemy models and SQLite interface
│   └── reddit_client.py    # Reddit API client wrapper
├── frontend/               # React + TypeScript + Vite + Tailwind
├── electron/               # Electron shell (main.js, preload.js)
└── scripts/                # Build scripts for Python and macOS signing
```

The packaged app embeds the Python backend as a PyInstaller binary that Electron spawns as a child process on startup. In development, you run them separately.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Desktop shell | Electron |
| Frontend | React, TypeScript, Vite, Tailwind CSS, D3.js |
| Backend | Python, FastAPI, SQLAlchemy |
| Database | SQLite |
| Sentiment analysis | VADER |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`) |
| Reddit API | PRAW |
| LLM providers | Anthropic (Claude), OpenAI (GPT) |
| Packaging | PyInstaller + electron-builder |

---

## Contributing

Contributions are welcome. Please open an issue before starting significant work so we can discuss the approach.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Open a pull request

Please make sure the app runs from source before submitting. There are no automated tests yet — validating manually against the dev setup is the current expectation.

---

## Documentation

Full usage documentation is available at [sentopic.io/docs](https://sentopic.io/pages/documentation), including:

- [Quick Start Guide](docs/getting-started/quick-start-guide.md)
- [macOS Installation](docs/installation/macos-installation.md)
- [Windows Installation](docs/installation/windows-installation.md)

---

## License

MIT — see [LICENSE](LICENSE) for details.