import React, { useState } from 'react'
import { Clock, Film, MessageSquare, Camera, Lightbulb, Sparkles } from 'lucide-react'

export default function ShotListTable({ shotlist }) {
  const [editingShot, setEditingShot] = useState(null)
  
  if (!shotlist || shotlist.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <Film className="w-16 h-16 mx-auto mb-4 opacity-50" />
        <p>No shots generated yet. Process a video to create a shotlist.</p>
      </div>
    )
  }
  
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left">
        <thead>
          <tr className="border-b border-dark-300">
            <th className="p-3 font-semibold text-primary">#</th>
            <th className="p-3 font-semibold text-primary">Time</th>
            <th className="p-3 font-semibold text-primary">Type</th>
            <th className="p-3 font-semibold text-primary">Angle</th>
            <th className="p-3 font-semibold text-primary">Movement</th>
            <th className="p-3 font-semibold text-primary w-64">Description</th>
            <th className="p-3 font-semibold text-primary">Dialogue</th>
            <th className="p-3 font-semibold text-primary">Lighting</th>
            <th className="p-3 font-semibold text-primary">Mood</th>
          </tr>
        </thead>
        <tbody>
          {shotlist.map((shot, index) => (
            <tr
              key={index}
              className="border-b border-dark-300 hover:bg-dark-300/50 transition-colors"
            >
              <td className="p-3 font-bold text-primary">{shot.shot_number || index + 1}</td>
              <td className="p-3 font-mono text-sm text-secondary">
                {formatTime(shot.time_start)} - {formatTime(shot.time_end)}
              </td>
              <td className="p-3">{shot.shot_type}</td>
              <td className="p-3">{shot.camera_angle}</td>
              <td className="p-3">{shot.camera_movement}</td>
              <td className="p-3 max-w-xs truncate" title={shot.description}>
                {shot.description}
              </td>
              <td className="p-3 max-w-xs truncate text-gray-400" title={shot.dialogue}>
                {shot.dialogue || '—'}
              </td>
              <td className="p-3">{shot.lighting}</td>
              <td className="p-3">{shot.mood_tone}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
