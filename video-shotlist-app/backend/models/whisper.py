from openai import OpenAI
import os
from typing import Optional, Dict, Any


class WhisperService:
    """Service for audio transcription using Whisper"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or "https://api.openai.com/v1"
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
    
    async def transcribe(
        self,
        audio_path: str,
        model: str = "whisper-1",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper
        
        Returns:
            Dictionary with segments containing text and timestamps
        """
        # Use provided credentials or fall back to instance credentials
        client = self.client
        if api_key:
            client = OpenAI(api_key=api_key, base_url=api_base or self.api_base)
        
        if not client:
            raise ValueError("No API key provided for Whisper")
        
        try:
            # Build prompt for better transcription
            prompt = None
            if system_prompt or user_prompt:
                prompt_parts = []
                if system_prompt:
                    prompt_parts.append(system_prompt)
                if user_prompt:
                    prompt_parts.append(user_prompt)
                prompt = " ".join(prompt_parts) if prompt_parts else None
            
            # Transcribe with timestamps
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model=model,
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"],
                    language=language if language != "auto" else None,
                    prompt=prompt,
                )
            
            # Parse segments with timestamps
            segments = []
            for segment in getattr(transcription, 'segments', []):
                segments.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                })
            
            return {
                "full_text": transcription.text,
                "language": getattr(transcription, 'language', language),
                "segments": segments,
                "duration": getattr(transcription, 'duration', 0),
            }
        
        except Exception as e:
            raise Exception(f"Whisper transcription failed: {str(e)}")
    
    def set_api_key(self, api_key: str):
        """Update API key"""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url=self.api_base)
    
    def set_api_base(self, api_base: str):
        """Update API base URL for custom endpoints"""
        self.api_base = api_base
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=api_base)
