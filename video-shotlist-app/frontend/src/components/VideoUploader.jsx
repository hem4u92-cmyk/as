import React, { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { useAppStore } from '../store/appStore'
import { Upload, Link, Film, Loader2 } from 'lucide-react'

export default function VideoUploader() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const { uploadVideo, isLoading, error } = useAppStore()
  
  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      try {
        await uploadVideo(acceptedFiles[0])
      } catch (err) {
        console.error('Upload failed:', err)
      }
    }
  }
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm'],
    },
    multiple: false,
    disabled: isLoading,
  })
  
  const handleYoutubeSubmit = async (e) => {
    e.preventDefault()
    if (!youtubeUrl.trim()) return
    
    try {
      await uploadVideo(null, youtubeUrl)
      setYoutubeUrl('')
    } catch (err) {
      console.error('YouTube upload failed:', err)
    }
  }
  
  return (
    <div className="max-w-3xl mx-auto">
      <h2 className="text-3xl font-bold text-primary mb-6">Upload Video</h2>
      
      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`card mb-6 cursor-pointer transition-all ${
          isDragActive
            ? 'border-primary bg-dark-300'
            : 'border-dark-300 hover:border-primary'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-center py-12">
          <Upload className="w-16 h-16 mx-auto mb-4 text-primary" />
          {isDragActive ? (
            <p className="text-lg text-primary">Drop the video here...</p>
          ) : (
            <>
              <p className="text-lg mb-2">
                Drag & drop a video file here, or click to select
              </p>
              <p className="text-sm text-gray-400">
                Supports MP4, MOV, AVI, MKV, WebM
              </p>
            </>
          )}
        </div>
      </div>
      
      {/* YouTube URL */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Link className="w-5 h-5" />
          Or upload from YouTube
        </h3>
        <form onSubmit={handleYoutubeSubmit} className="flex gap-3">
          <input
            type="url"
            value={youtubeUrl}
            onChange={(e) => setYoutubeUrl(e.target.value)}
            placeholder="Paste YouTube URL here..."
            className="input-base flex-1"
            disabled={isLoading}
          />
          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Process'}
          </button>
        </form>
      </div>
      
      {/* Error message */}
      {error && (
        <div className="mt-4 p-4 bg-secondary/20 border border-secondary rounded-lg">
          <p className="text-secondary">{error}</p>
        </div>
      )}
      
      {/* Loading state */}
      {isLoading && (
        <div className="mt-4 p-4 bg-dark-300 rounded-lg flex items-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-primary" />
          <span>Processing video...</span>
        </div>
      )}
    </div>
  )
}
