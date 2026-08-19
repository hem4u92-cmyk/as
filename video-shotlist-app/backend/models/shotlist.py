from openai import OpenAI
import os
import json
from typing import Optional, List, Dict, Any


class ShotlistGenerator:
    """Service for generating structured shotlists from video analysis"""
    
    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_base = api_base or "https://api.openai.com/v1"
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
    
    async def generate(
        self,
        transcription: Dict[str, Any],
        frame_analyses: List[Dict[str, Any]],
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        system_prompt: Optional[str] = None,
        user_prompt: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Generate a structured shotlist from transcription and frame analyses
        
        Returns:
            List of shots with detailed information
        """
        client = self.client
        if api_key:
            client = OpenAI(api_key=api_key, base_url=api_base or self.api_base)
        
        if not client:
            raise ValueError("No API key provided for Shotlist generation")
        
        try:
            # Build default prompts
            default_system = """You are a professional film director and script supervisor. 
Your task is to create a detailed, production-ready shotlist from video analysis data.

For each shot, include:
- Shot number (sequential)
- Time range (start - end in seconds)
- Shot type (wide shot, medium shot, close-up, extreme close-up, over-the-shoulder, two-shot, etc.)
- Camera angle (eye-level, high angle, low angle, dutch angle, bird's eye view, worm's eye view)
- Camera movement (static, pan left/right, tilt up/down, dolly in/out, zoom in/out, handheld, steadicam, tracking)
- Composition notes (rule of thirds, centered, leading lines, symmetry, depth layers)
- Lighting description (natural, artificial, high-key, low-key, backlighting, side lighting, color temperature)
- Subject/action description
- Dialogue/audio (from transcription)
- Visual elements and props
- Mood and tone
- Suggested AI video generation prompt (if this shot were to be recreated)

Format your response as a JSON array of shot objects."""

            default_user = """Create a comprehensive shotlist from the provided video analysis.
Combine the visual frame analyses with the audio transcription to create accurate, detailed shot descriptions.
Group consecutive similar frames into single shots where appropriate.
Ensure all timecodes are accurate and sequential."""

            system_content = system_prompt if system_prompt else default_system
            user_content = user_prompt if user_prompt else default_user
            
            # Prepare context data
            transcription_text = transcription.get("full_text", "")
            transcription_segments = transcription.get("segments", [])
            
            # Summarize frame analyses
            frame_summaries = []
            for fa in frame_analyses[:50]:  # Limit to prevent token overflow
                if "analysis" in fa:
                    frame_summaries.append({
                        "timestamp": fa.get("timestamp", 0),
                        "analysis": fa["analysis"][:500] if len(fa["analysis"]) > 500 else fa["analysis"]
                    })
            
            # Build comprehensive prompt
            context = f"""
TRANSCRIPTION DATA:
Duration: {transcription.get("duration", 0):.2f} seconds
Language: {transcription.get("language", "unknown")}
Full Text: {transcription_text[:2000]}...

TRANSCRIPTION SEGMENTS (with timestamps):
{json.dumps(transcription_segments[:20], indent=2)}

VISUAL FRAME ANALYSES ({len(frame_summaries)} frames analyzed):
{json.dumps(frame_summaries, indent=2)}

INSTRUCTION:
{user_content}

Respond ONLY with a valid JSON array. Do not include any explanatory text outside the JSON."""

            # Make API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0.7,
            )
            
            # Parse response
            result_text = response.choices[0].message.content
            
            # Handle both array and object with shots key
            try:
                result_data = json.loads(result_text)
                if isinstance(result_data, dict) and "shots" in result_data:
                    shots = result_data["shots"]
                elif isinstance(result_data, list):
                    shots = result_data
                else:
                    shots = result_data.get("shots", []) if isinstance(result_data, dict) else []
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from text
                import re
                json_match = re.search(r'\[[\s\S]*\]', result_text)
                if json_match:
                    shots = json.loads(json_match.group())
                else:
                    shots = []
            
            # Ensure each shot has required fields
            processed_shots = []
            for i, shot in enumerate(shots):
                processed_shot = {
                    "shot_number": shot.get("shot_number", i + 1),
                    "time_start": shot.get("time_start", shot.get("start_time", 0)),
                    "time_end": shot.get("time_end", shot.get("end_time", 0)),
                    "shot_type": shot.get("shot_type", "unknown"),
                    "camera_angle": shot.get("camera_angle", "eye-level"),
                    "camera_movement": shot.get("camera_movement", "static"),
                    "composition": shot.get("composition", ""),
                    "lighting": shot.get("lighting", ""),
                    "description": shot.get("description", shot.get("action", "")),
                    "dialogue": shot.get("dialogue", shot.get("audio", "")),
                    "visual_elements": shot.get("visual_elements", shot.get("subjects", [])),
                    "mood_tone": shot.get("mood_tone", shot.get("mood", "")),
                    "ai_prompt": shot.get("ai_prompt", shot.get("generation_prompt", "")),
                }
                processed_shots.append(processed_shot)
            
            return processed_shots
        
        except Exception as e:
            raise Exception(f"Shotlist generation failed: {str(e)}")
    
    async def refine(
        self,
        current_shotlist: List[Dict[str, Any]],
        transcription: Dict[str, Any],
        feedback: str,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Refine existing shotlist based on user feedback
        """
        client = self.client
        if api_key:
            client = OpenAI(api_key=api_key, base_url=self.api_base)
        
        if not client:
            raise ValueError("No API key provided")
        
        try:
            system_prompt = """You are a film editing assistant. Revise the shotlist based on user feedback.
Maintain the same JSON structure but update shots according to the feedback.
Keep timecodes accurate and ensure continuity between shots."""

            user_prompt = f"""USER FEEDBACK: {feedback}

CURRENT SHOTLIST:
{json.dumps(current_shotlist, indent=2)}

Revise the shotlist addressing the feedback above. Return only the updated JSON array."""

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=4000,
                temperature=0.7,
            )
            
            result_text = response.choices[0].message.content
            result_data = json.loads(result_text)
            
            if isinstance(result_data, list):
                return result_data
            elif isinstance(result_data, dict) and "shots" in result_data:
                return result_data["shots"]
            else:
                return current_shotlist  # Return original if parsing fails
        
        except Exception as e:
            raise Exception(f"Shotlist refinement failed: {str(e)}")
    
    def set_api_key(self, api_key: str):
        """Update API key"""
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key, base_url=self.api_base)
    
    def set_api_base(self, api_base: str):
        """Update API base URL"""
        self.api_base = api_base
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=api_base)
