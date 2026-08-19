import React, { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAppStore } from '../store/appStore'
import VideoUploader from '../components/VideoUploader'
import { Film, Clock, Trash2, ChevronRight, Loader2 } from 'lucide-react'

export default function Dashboard() {
  const { sessions, fetchSessions, deleteSession, isLoading } = useAppStore()
  
  useEffect(() => {
    fetchSessions()
  }, [])
  
  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }
  
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
          AI-Powered Video Shotlist Generator
        </h1>
        <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-8">
          Transform your videos into professional shotlists using advanced AI. 
          Analyze camera angles, movements, lighting, and dialogue automatically.
        </p>
        
        <Link to="/workspace" className="btn-primary text-lg px-8 py-3">
          Start New Project
        </Link>
      </div>
      
      {/* Upload Section */}
      <VideoUploader />
      
      {/* Sessions List */}
      <div>
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          <Film className="w-6 h-6 text-primary" />
          Recent Projects
        </h2>
        
        {isLoading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : sessions.length === 0 ? (
          <div className="card text-center py-12 text-gray-400">
            <Film className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No projects yet. Upload a video to get started!</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {sessions.map((session) => (
              <div
                key={session.session_id}
                className="card flex items-center justify-between hover:border-primary transition-colors"
              >
                <Link
                  to={`/workspace/${session.session_id}`}
                  className="flex items-center gap-4 flex-1"
                >
                  <div className="bg-dark-300 p-3 rounded-lg">
                    <Film className="w-6 h-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">
                      {session.video_path?.split('/').pop() || 'Untitled Project'}
                    </h3>
                    <div className="flex items-center gap-4 text-sm text-gray-400 mt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {formatDate(session.created_at)}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        session.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        session.status === 'failed' ? 'bg-secondary/20 text-secondary' :
                        'bg-yellow-500/20 text-yellow-400'
                      }`}>
                        {session.status}
                      </span>
                    </div>
                  </div>
                </Link>
                
                <div className="flex items-center gap-2">
                  <Link
                    to={`/workspace/${session.session_id}`}
                    className="p-2 hover:bg-dark-300 rounded-lg transition-colors"
                  >
                    <ChevronRight className="w-5 h-5" />
                  </Link>
                  <button
                    onClick={() => deleteSession(session.session_id)}
                    className="p-2 hover:bg-secondary/20 text-secondary rounded-lg transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
