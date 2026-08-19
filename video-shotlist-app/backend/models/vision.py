from openai import OpenAI
import os
import base64
from typing import Optional, List, Dict, Any
from pathlib import Path


class VisionService:
    """Service for visual analysis using GPT-4o Vision"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or "https://api.openai.com/v1"
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    async def analyze_frame(
        self,
        image_path: str,
        transcription_segment: Optional[Dict] = None,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze a single video frame"""
        
        client = self.client
        if api_key:
            client = OpenAI(api_key=api_key, base_url=api_base or self.api_base)
        
        if not client:
            raise ValueError("No API key provided for Vision model")
        
        try:
            # Encode image
            base64_image = self._encode_image(image_path)
            
            # Build default prompts
            default_system = """You are a professional cinematographer and video analyst. 
Analyze this video frame in detail, focusing on:
- Shot type (wide, medium, close-up, extreme close-up, over-the-shoulder, etc.)
- Camera angle (eye-level, high angle, low angle, dutch angle, bird's eye, worm's eye)
- Camera movement (static, pan, tilt, dolly, zoom, handheld, steadicam)
- Composition (rule of thirds, leading lines, symmetry, framing)
- Lighting (natural, artificial, high-key, low-key, backlighting, side lighting)
- Color palette and mood
- Key visual elements and subjects
- Depth of field and focus"""

            default_user = """Provide a detailed analysis of this frame as if creating a professional shot list.
Include technical details about the cinematography and visual storytelling elements."""
            
            system_content = system_prompt if system_prompt else default_system
            user_content = user_prompt if user_prompt else default_user
            
            # Add transcription context if available
            if transcription_segment:
                user_content += f"\n\nContext from audio transcription at this moment: \"{transcription_segment.get('text', '')}\""
            
            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_content},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "frame_path": image_path,
                "analysis": analysis,
                "model_used": model,
            }
        
        except Exception as e:
            raise Exception(f"Vision analysis failed: {str(e)}")
    
    async def analyze_frames(
        self,
        frame_paths: List[str],
        transcription: Optional[Dict] = None,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
        batch_size: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple frames
        
        Args:
            frame_paths: List of paths to frame images
            transcription: Full transcription with segments
            model: Vision model to use
            batch_size: Number of frames to process in parallel
            
        Returns:
            List of frame analyses
        """
        results = []
        
        # Get transcription segment for each frame based on timing
        def get_segment_for_frame(frame_idx: int, total_frames: int, duration: float) -> Optional[Dict]:
            if not transcription or not transcription.get("segments"):
                return None
            
            frame_time = (frame_idx / total_frames) * duration if duration > 0 else 0
            
            for segment in transcription["segments"]:
                if segment["start"] <= frame_time <= segment["end"]:
                    return segment
            
            return None
        
        duration = transcription.get("duration", 0) if transcription else 0
        total_frames = len(frame_paths)
        
        # Process frames (in production, use async batching)
        for i, frame_path in enumerate(frame_paths):
            try:
                segment = get_segment_for_frame(i, total_frames, duration)
                
                analysis = await self.analyze_frame(
                    image_path=frame_path,
                    transcription_segment=segment,
                    model=model,
                    api_key=api_key,
                    api_base=api_base,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
                analysis["frame_index"] = i
                analysis["timestamp"] = (i / total_frames) * duration if duration > 0 else 0
                
                results.append(analysis)
            except Exception as e:
                print(f"Error analyzing frame {frame_path}: {e}")
                results.append({
                    "frame_path": frame_path,
                    "frame_index": i,
                    "error": str(e),
                })
        
        return results
    
    def set_api_key(self, api_key: str):
        """Update API key"""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url=self.api_base)
    
    def set_api_base(self, api_base: str):
        """Update API base URL for custom endpoints"""
        self.api_base = api_base
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=api_base)
