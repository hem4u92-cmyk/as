import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAppStore } from '../store/appStore'
import ShotListTable from '../components/ShotListTable'
import ExportButtons from '../components/ExportButtons'
import ModelPanel from '../components/ModelPanel'
import { Play, MessageSquare, FileText, Loader2, Wand2, ChevronLeft } from 'lucide-react'

export default function Workspace() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const { currentSession, setCurrentSession, fetchSessions, processVideo, refineShotlist, modelConfig, promptConfig } = useAppStore()
  const [activeTab, setActiveTab] = useState('shotlist')
  const [feedback, setFeedback] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  
  useEffect(() => {
    if (sessionId) {
      // Load session details
      const loadSession = async () => {
        try {
          const response = await fetch(`/api/session/${sessionId}`).then(r => r.json())
          setCurrentSession(response)
        } catch (error) {
          console.error('Failed to load session:', error)
        }
      }
      loadSession()
    } else if (!currentSession) {
      // Fetch sessions and get the most recent one
      fetchSessions()
    }
  }, [sessionId])
  
  const handleProcess = async () => {
    const sessionToProcess = sessionId ? { session_id: sessionId } : currentSession
    if (!sessionToProcess?.session_id) return
    
    setIsProcessing(true)
    try {
      await processVideo(sessionToProcess.session_id, modelConfig, promptConfig)
    } catch (error) {
      console.error('Processing failed:', error)
    } finally {
      setIsProcessing(false)
    }
  }
  
  const handleRefine = async () => {
    if (!feedback.trim() || !currentSession?.session_id) return
    
    setIsProcessing(true)
    try {
      await refineShotlist(currentSession.session_id, feedback, modelConfig)
      setFeedback('')
    } catch (error) {
      console.error('Refinement failed:', error)
    } finally {
      setIsProcessing(false)
    }
  }
  
  const session = sessionId && !currentSession ? null : currentSession
  
  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Main Content */}
      <div className="lg:col-span-3 space-y-6">
        {/* Back button if no sessionId in URL */}
        {!sessionId && (
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-4"
          >
            <ChevronLeft className="w-4 h-4" />
            Back to Dashboard
          </button>
        )}
        
        {/* Session Info */}
        {session && (
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">
                {session.video_path?.split('/').pop() || 'Untitled Project'}
              </h2>
              <span className={`px-3 py-1 rounded-full text-sm ${
                session.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                session.status === 'failed' ? 'bg-secondary/20 text-secondary' :
                'bg-yellow-500/20 text-yellow-400'
              }`}>
                {session.status}
              </span>
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-3 flex-wrap">
              <button
                onClick={handleProcess}
                disabled={isProcessing || !session?.video_path}
                className="btn-primary flex items-center gap-2"
              >
                {isProcessing ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Wand2 className="w-5 h-5" />
                )}
                {isProcessing ? 'Processing...' : 'Generate Shotlist'}
              </button>
              
              {session?.shotlist && (
                <ExportButtons sessionId={session.session_id} />
              )}
            </div>
          </div>
        )}
        
        {/* Tabs */}
        {session?.shotlist && (
          <>
            <div className="flex gap-2 border-b border-dark-300">
              <button
                onClick={() => setActiveTab('shotlist')}
                className={`px-4 py-2 flex items-center gap-2 ${
                  activeTab === 'shotlist'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <FileText className="w-4 h-4" />
                Shotlist
              </button>
              <button
                onClick={() => setActiveTab('transcription')}
                className={`px-4 py-2 flex items-center gap-2 ${
                  activeTab === 'transcription'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                Transcription
              </button>
              <button
                onClick={() => setActiveTab('refine')}
                className={`px-4 py-2 flex items-center gap-2 ${
                  activeTab === 'refine'
                    ? 'border-b-2 border-primary text-primary'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <Wand2 className="w-4 h-4" />
                Refine
              </button>
            </div>
            
            {/* Tab Content */}
            <div className="card min-h-[500px]">
              {activeTab === 'shotlist' && (
                <ShotListTable shotlist={session.shotlist} />
              )}
              
              {activeTab === 'transcription' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Audio Transcription</h3>
                  {session.transcription?.segments?.map((segment, i) => (
                    <div key={i} className="p-3 bg-dark-300 rounded-lg">
                      <span className="text-primary font-mono text-sm">
                        {new Date(segment.start * 1000).toISOString().substr(14, 5)} - 
                        {new Date(segment.end * 1000).toISOString().substr(14, 5)}
                      </span>
                      <p className="mt-1">{segment.text}</p>
                    </div>
                  ))}
                </div>
              )}
              
              {activeTab === 'refine' && (
                <div className="space-y-4">
                  <h3 className="font-semibold text-lg">Refine Shotlist</h3>
                  <p className="text-gray-400">
                    Provide feedback to improve the generated shotlist. Be specific about what you'd like to change.
                  </p>
                  <textarea
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    placeholder="E.g., 'Add more detail about camera movements', 'Focus on lighting descriptions', 'Include AI generation prompts for each shot'..."
                    className="input-base h-32 resize-none"
                  />
                  <button onClick={handleRefine} disabled={isProcessing || !feedback.trim()} className="btn-primary">
                    {isProcessing ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Apply Refinements'}
                  </button>
                </div>
              )}
            </div>
          </>
        )}
        
        {/* No session state */}
        {!session && (
          <div className="card text-center py-12 text-gray-400">
            <Play className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>Select or upload a video to start working.</p>
          </div>
        )}
      </div>
      
      {/* Sidebar */}
      <div className="lg:col-span-1">
        <ModelPanel />
      </div>
    </div>
  )
}
