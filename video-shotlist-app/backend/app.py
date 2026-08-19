from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import uuid
import json
from datetime import datetime

from models.whisper import WhisperService
from models.vision import VisionService
from models.shotlist import ShotlistGenerator
from models.memory import MemoryService
from utils.video_processor import VideoProcessor
from utils.export import ExportService

app = FastAPI(title="Video Shotlist AI", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
os.makedirs("frames", exist_ok=True)

# Initialize services
whisper_service = WhisperService()
vision_service = VisionService()
shotlist_generator = ShotlistGenerator()
memory_service = MemoryService()
video_processor = VideoProcessor()
export_service = ExportService()


class ModelConfig(BaseModel):
    transcription_model: str = "whisper-1"
    vision_model: str = "gpt-4o-mini"
    shotlist_model: str = "gpt-4o"
    temperature: float = 0.7
    custom_api_key: Optional[str] = None
    custom_api_base: Optional[str] = None


class PromptConfig(BaseModel):
    transcription_system: Optional[str] = None
    transcription_user: Optional[str] = None
    vision_system: Optional[str] = None
    vision_user: Optional[str] = None
    shotlist_system: Optional[str] = None
    shotlist_user: Optional[str] = None


class RefinementRequest(BaseModel):
    session_id: str
    feedback: str
    model_config: Optional[ModelConfig] = None


class SessionResponse(BaseModel):
    session_id: str
    status: str
    video_path: Optional[str] = None
    transcription: Optional[Dict] = None
    shotlist: Optional[List[Dict]] = None
    created_at: str
    updated_at: str


@app.get("/")
async def root():
    return {"message": "Video Shotlist AI API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/upload", response_model=SessionResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    youtube_url: Optional[str] = Form(None),
):
    """Upload video file or YouTube URL"""
    session_id = str(uuid.uuid4())
    
    try:
        if file:
            # Save uploaded file
            file_path = f"uploads/{session_id}_{file.filename}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        elif youtube_url:
            # Download from YouTube
            file_path = await video_processor.download_youtube(youtube_url, session_id)
        else:
            raise HTTPException(status_code=400, detail="No file or YouTube URL provided")
        
        # Initialize session in memory
        session_data = {
            "session_id": session_id,
            "video_path": file_path,
            "status": "uploaded",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        memory_service.save_session(session_data)
        
        return SessionResponse(
            session_id=session_id,
            status="uploaded",
            video_path=file_path,
            created_at=session_data["created_at"],
            updated_at=session_data["updated_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/process/{session_id}")
async def process_video(
    session_id: str,
    model_config: ModelConfig,
    prompt_config: Optional[PromptConfig] = None,
):
    """Process video: extract audio, transcribe, analyze frames, generate shotlist"""
    session = memory_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Update status
        memory_service.update_session(session_id, {"status": "processing"})
        
        video_path = session["video_path"]
        
        # Step 1: Extract audio
        audio_path = await video_processor.extract_audio(video_path, session_id)
        
        # Step 2: Transcribe audio
        transcription = await whisper_service.transcribe(
            audio_path,
            model=model_config.transcription_model,
            api_key=model_config.custom_api_key,
            api_base=model_config.custom_api_base,
            system_prompt=prompt_config.transcription_system if prompt_config else None,
            user_prompt=prompt_config.transcription_user if prompt_config else None,
        )
        
        # Step 3: Extract key frames
        frames = await video_processor.extract_frames(video_path, session_id, fps=1)
        
        # Step 4: Analyze frames with vision model
        frame_analyses = await vision_service.analyze_frames(
            frames,
            transcription=transcription,
            model=model_config.vision_model,
            api_key=model_config.custom_api_key,
            api_base=model_config.custom_api_base,
            system_prompt=prompt_config.vision_system if prompt_config else None,
            user_prompt=prompt_config.vision_user if prompt_config else None,
        )
        
        # Step 5: Generate shotlist
        shotlist = await shotlist_generator.generate(
            transcription=transcription,
            frame_analyses=frame_analyses,
            model=model_config.shotlist_model,
            api_key=model_config.custom_api_key,
            api_base=model_config.custom_api_base,
            system_prompt=prompt_config.shotlist_system if prompt_config else None,
            user_prompt=prompt_config.shotlist_user if prompt_config else None,
        )
        
        # Save results
        session_data = {
            "status": "completed",
            "transcription": transcription,
            "frame_analyses": frame_analyses,
            "shotlist": shotlist,
            "model_config": model_config.dict(),
            "updated_at": datetime.now().isoformat(),
        }
        memory_service.update_session(session_id, session_data)
        
        # Store in vector memory for semantic search
        memory_service.store_shotlist_embeddings(session_id, shotlist)
        
        return {"session_id": session_id, "status": "completed", "shotlist": shotlist}
    
    except Exception as e:
        memory_service.update_session(session_id, {"status": "failed", "error": str(e)})
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/refine/{session_id}")
async def refine_shotlist(
    session_id: str,
    request: RefinementRequest,
    prompt_config: Optional[PromptConfig] = None,
):
    """Refine shotlist based on user feedback"""
    session = memory_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        current_shotlist = session.get("shotlist", [])
        transcription = session.get("transcription", {})
        
        # Regenerate with feedback
        refined_shotlist = await shotlist_generator.refine(
            current_shotlist=current_shotlist,
            transcription=transcription,
            feedback=request.feedback,
            model=request.model_config.shotlist_model if request.model_config else "gpt-4o",
            api_key=request.model_config.custom_api_key if request.model_config else None,
        )
        
        # Update session
        memory_service.update_session(session_id, {
            "shotlist": refined_shotlist,
            "updated_at": datetime.now().isoformat(),
        })
        
        return {"session_id": session_id, "shotlist": refined_shotlist}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
async def list_sessions():
    """List all sessions"""
    sessions = memory_service.list_sessions()
    return {"sessions": sessions}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    session = memory_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    memory_service.delete_session(session_id)
    return {"message": "Session deleted"}


@app.get("/api/export/{session_id}/{format}")
async def export_shotlist(session_id: str, format: str):
    """Export shotlist in various formats (html, csv, json, markdown)"""
    session = memory_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    shotlist = session.get("shotlist", [])
    
    try:
        if format == "json":
            content = export_service.to_json(shotlist)
            media_type = "application/json"
            ext = "json"
        elif format == "csv":
            content = export_service.to_csv(shotlist)
            media_type = "text/csv"
            ext = "csv"
        elif format == "html":
            content = export_service.to_html(shotlist)
            media_type = "text/html"
            ext = "html"
        elif format == "markdown":
            content = export_service.to_markdown(shotlist)
            media_type = "text/markdown"
            ext = "md"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")
        
        filename = f"shotlist_{session_id}.{ext}"
        filepath = f"processed/{filename}"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return FileResponse(filepath, media_type=media_type, filename=filename)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prompts/presets")
async def get_prompt_presets():
    """Get preset prompts"""
    presets = {
        "cinematic": {
            "name": "Cinematic Shotlist",
            "shotlist_system": "You are a professional cinematographer and director of photography. Analyze the video and create a detailed shotlist.",
            "shotlist_user": "Create a shotlist with detailed descriptions of camera angles, movements, lighting, and composition for each shot.",
        },
        "commercial": {
            "name": "Commercial/Advertisement",
            "shotlist_system": "You are a commercial director specializing in advertising. Focus on product placement and visual appeal.",
            "shotlist_user": "Create a shotlist optimized for commercial use, highlighting products, branding elements, and key messaging moments.",
        },
        "documentary": {
            "name": "Documentary Style",
            "shotlist_system": "You are a documentary filmmaker. Focus on storytelling, interviews, and B-roll footage.",
            "shotlist_user": "Create a shotlist that captures the narrative flow, identifying interview segments, B-roll, and key documentary moments.",
        },
        "social_media": {
            "name": "Social Media Content",
            "shotlist_system": "You are a social media content creator. Focus on engaging, short-form content.",
            "shotlist_user": "Create a shotlist optimized for social media, identifying hook moments, transitions, and viral-worthy segments.",
        },
    }
    return presets


@app.post("/api/prompts/custom")
async def save_custom_prompt(name: str = Form(...), prompt_type: str = Form(...), content: str = Form(...)):
    """Save a custom prompt"""
    prompt_data = {
        "name": name,
        "type": prompt_type,
        "content": content,
        "created_at": datetime.now().isoformat(),
    }
    memory_service.save_prompt(prompt_data)
    return {"message": "Prompt saved", "prompt": prompt_data}


@app.get("/api/prompts/custom")
async def get_custom_prompts():
    """Get all custom prompts"""
    prompts = memory_service.list_prompts()
    return {"prompts": prompts}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
