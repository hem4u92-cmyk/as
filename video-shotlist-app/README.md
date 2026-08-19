# Video Shotlist AI Application

Professional video processing application using AI for shotlist generation.

## Features

- **Video Upload**: Support for file upload and YouTube links
- **AI Transcription**: Whisper API integration for audio transcription
- **Visual Analysis**: GPT-4o Vision for frame analysis
- **Shotlist Generation**: Structured shotlist with timestamps, camera angles, movements
- **Model Management**: Switch between different AI models
- **Prompt Customization**: Edit system and user prompts for each stage
- **Memory System**: Session history and context retention
- **Export**: HTML, CSV, JSON, Markdown formats

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + TailwindCSS
- **AI Integration**: OpenAI API (Whisper, GPT-4o, GPT-4o-mini)
- **Video Processing**: FFmpeg, MoviePy
- **Database**: SQLite + ChromaDB for vector memory
- **Async Tasks**: Celery + Redis
- **Deployment**: Docker

## Project Structure

```
video-shotlist-app/
├── backend/
│   ├── app.py                 # FastAPI server
│   ├── models/
│   │   ├── whisper.py         # Whisper integration
│   │   ├── vision.py          # GPT-4o Vision integration
│   │   ├── shotlist.py        # Shotlist generation
│   │   └── memory.py          # Database & vector memory
│   ├── prompts/
│   │   ├── system/            # System prompts
│   │   ├── user/              # User prompts
│   │   └── presets/           # Preset prompts
│   ├── utils/
│   │   ├── video_processor.py # FFmpeg / MoviePy
│   │   └── export.py          # Export utilities
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── hooks/
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- FFmpeg
- Docker (optional)

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Setup

```bash
docker-compose up --build
```

## Configuration

Set your API keys in the UI settings panel:
- OpenAI API Key (for Whisper and GPT-4o)
- Custom API endpoints for local models

## Usage

1. Upload a video file or paste YouTube URL
2. Select AI models for transcription and analysis
3. Customize prompts if needed
4. Start processing
5. Review and edit the generated shotlist
6. Export in your preferred format

## License

MIT
