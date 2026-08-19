import json
from typing import List, Dict, Any


class ExportService:
    """Service for exporting shotlists in various formats"""
    
    def to_json(self, shotlist: List[Dict[str, Any]], pretty: bool = True) -> str:
        """Export shotlist as JSON"""
        if pretty:
            return json.dumps(shotlist, indent=2, ensure_ascii=False)
        return json.dumps(shotlist, ensure_ascii=False)
    
    def to_csv(self, shotlist: List[Dict[str, Any]]) -> str:
        """Export shotlist as CSV"""
        if not shotlist:
            return ""
        
        # Define columns
        columns = [
            "shot_number",
            "time_start",
            "time_end",
            "duration",
            "shot_type",
            "camera_angle",
            "camera_movement",
            "composition",
            "lighting",
            "description",
            "dialogue",
            "visual_elements",
            "mood_tone",
            "ai_prompt",
        ]
        
        # Build CSV
        lines = []
        
        # Header
        lines.append(",".join(columns))
        
        # Rows
        for shot in shotlist:
            row = []
            for col in columns:
                value = shot.get(col, "")
                
                # Handle lists (convert to string)
                if isinstance(value, list):
                    value = "; ".join(str(v) for v in value)
                
                # Escape quotes and wrap in quotes if contains comma
                value = str(value).replace('"', '""')
                if "," in value or "\n" in value:
                    value = f'"{value}"'
                
                row.append(value)
            
            lines.append(",".join(row))
        
        return "\n".join(lines)
    
    def to_html(self, shotlist: List[Dict[str, Any]]) -> str:
        """Export shotlist as HTML table"""
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shotlist Export</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
        }
        h1 {
            color: #00d9ff;
            border-bottom: 2px solid #00d9ff;
            padding-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: #16213e;
        }
        th, td {
            border: 1px solid #0f3460;
            padding: 12px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background: #0f3460;
            color: #00d9ff;
            font-weight: 600;
            position: sticky;
            top: 0;
        }
        tr:nth-child(even) {
            background: #1a1a2e;
        }
        tr:hover {
            background: #0f3460;
        }
        .time-code {
            font-family: 'Courier New', monospace;
            color: #e94560;
        }
        .shot-number {
            font-weight: bold;
            color: #00d9ff;
        }
    </style>
</head>
<body>
    <h1>🎬 Video Shotlist</h1>
    <table>
        <thead>
            <tr>
                <th>#</th>
                <th>Time</th>
                <th>Type</th>
                <th>Angle</th>
                <th>Movement</th>
                <th>Description</th>
                <th>Dialogue</th>
                <th>Lighting</th>
                <th>Mood</th>
            </tr>
        </thead>
        <tbody>
"""
        
        for shot in shotlist:
            duration = shot.get("time_end", 0) - shot.get("time_start", 0)
            time_range = f"{self._format_time(shot.get('time_start', 0))} - {self._format_time(shot.get('time_end', 0))} ({duration:.1f}s)"
            
            visual_elements = shot.get("visual_elements", [])
            if isinstance(visual_elements, list):
                visual_elements = ", ".join(str(v) for v in visual_elements)
            
            html += f"""            <tr>
                <td class="shot-number">{shot.get('shot_number', '')}</td>
                <td class="time-code">{time_range}</td>
                <td>{shot.get('shot_type', '')}</td>
                <td>{shot.get('camera_angle', '')}</td>
                <td>{shot.get('camera_movement', '')}</td>
                <td>{shot.get('description', '')}<br><small>{visual_elements}</small></td>
                <td>{shot.get('dialogue', '')}</td>
                <td>{shot.get('lighting', '')}</td>
                <td>{shot.get('mood_tone', '')}</td>
            </tr>
"""
        
        html += """        </tbody>
    </table>
</body>
</html>"""
        
        return html
    
    def to_markdown(self, shotlist: List[Dict[str, Any]]) -> str:
        """Export shotlist as Markdown"""
        md = "# 🎬 Video Shotlist\n\n"
        
        for shot in shotlist:
            duration = shot.get("time_end", 0) - shot.get("time_start", 0)
            time_range = f"{self._format_time(shot.get('time_start', 0))} - {self._format_time(shot.get('time_end', 0))} ({duration:.1f}s)"
            
            md += f"## Shot {shot.get('shot_number', '')}: {time_range}\n\n"
            md += f"**Type:** {shot.get('shot_type', 'N/A')}\n\n"
            md += f"**Camera Angle:** {shot.get('camera_angle', 'N/A')}\n\n"
            md += f"**Movement:** {shot.get('camera_movement', 'N/A')}\n\n"
            md += f"**Composition:** {shot.get('composition', 'N/A')}\n\n"
            md += f"**Lighting:** {shot.get('lighting', 'N/A')}\n\n"
            md += f"**Description:** {shot.get('description', 'N/A')}\n\n"
            
            if shot.get('dialogue'):
                md += f"**Dialogue:** \"{shot.get('dialogue')}\"\n\n"
            
            visual_elements = shot.get("visual_elements", [])
            if visual_elements:
                if isinstance(visual_elements, list):
                    visual_elements = ", ".join(str(v) for v in visual_elements)
                md += f"**Visual Elements:** {visual_elements}\n\n"
            
            if shot.get('mood_tone'):
                md += f"**Mood/Tone:** {shot.get('mood_tone')}\n\n"
            
            if shot.get('ai_prompt'):
                md += f"**AI Prompt:** `{shot.get('ai_prompt')}`\n\n"
            
            md += "---\n\n"
        
        return md
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def to_pdf_template(self, shotlist: List[Dict[str, Any]]) -> str:
        """Export shotlist in a format suitable for PDF generation"""
        # This could be extended to use reportlab or similar
        # For now, return HTML which can be converted to PDF
        return self.to_html(shotlist)
