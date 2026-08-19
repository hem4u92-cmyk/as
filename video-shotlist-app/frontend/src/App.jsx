import React from 'react'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Workspace from './pages/Workspace'
import { Film } from 'lucide-react'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-dark-100 text-white">
        {/* Header */}
        <header className="bg-dark-200 border-b border-dark-300 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link to="/" className="flex items-center gap-3">
              <div className="bg-primary p-2 rounded-lg">
                <Film className="w-6 h-6 text-dark-100" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-primary">Video Shotlist AI</h1>
                <p className="text-xs text-gray-400">Professional Video Analysis</p>
              </div>
            </Link>
            
            <nav className="flex gap-4">
              <Link to="/" className="text-gray-400 hover:text-white transition-colors">
                Dashboard
              </Link>
              <Link to="/workspace" className="text-gray-400 hover:text-white transition-colors">
                Workspace
              </Link>
            </nav>
          </div>
        </header>
        
        {/* Main Content */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/workspace" element={<Workspace />} />
            <Route path="/workspace/:sessionId" element={<Workspace />} />
          </Routes>
        </main>
        
        {/* Footer */}
        <footer className="border-t border-dark-300 mt-12 py-6 text-center text-gray-500 text-sm">
          <p>Video Shotlist AI &copy; 2024. Built with FastAPI + React.</p>
        </footer>
      </div>
    </BrowserRouter>
  )
}

export default App
