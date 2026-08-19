import React, { useState } from 'react'
import { useAppStore } from '../store/appStore'
import { Settings, Sliders, Wand2, Save } from 'lucide-react'

export default function ModelPanel() {
  const { modelConfig, setModelConfig, promptConfig, setPromptConfig, loadPromptPresets, promptPresets, applyPreset } = useAppStore()
  const [activeTab, setActiveTab] = useState('models')
  
  return (
    <div className="card h-full overflow-y-auto">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <Settings className="w-5 h-5" />
        Configuration
      </h2>
      
      {/* Tabs */}
      <div className="flex gap-2 mb-4 border-b border-dark-300 pb-2">
        <button
          onClick={() => setActiveTab('models')}
          className={`px-3 py-1 rounded ${activeTab === 'models' ? 'bg-primary text-dark-100' : 'text-gray-400 hover:text-white'}`}
        >
          Models
        </button>
        <button
          onClick={() => setActiveTab('prompts')}
          className={`px-3 py-1 rounded ${activeTab === 'prompts' ? 'bg-primary text-dark-100' : 'text-gray-400 hover:text-white'}`}
        >
          Prompts
        </button>
      </div>
      
      {/* Models Tab */}
      {activeTab === 'models' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Transcription Model</label>
            <select
              value={modelConfig.transcription_model}
              onChange={(e) => setModelConfig({ transcription_model: e.target.value })}
              className="input-base"
            >
              <option value="whisper-1">Whisper (OpenAI)</option>
              <option value="faster-whisper">Faster Whisper (Local)</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Vision Model</label>
            <select
              value={modelConfig.vision_model}
              onChange={(e) => setModelConfig({ vision_model: e.target.value })}
              className="input-base"
            >
              <option value="gpt-4o-mini">GPT-4o Mini (Fast & Cheap)</option>
              <option value="gpt-4o">GPT-4o (Best Quality)</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Shotlist Model</label>
            <select
              value={modelConfig.shotlist_model}
              onChange={(e) => setModelConfig({ shotlist_model: e.target.value })}
              className="input-base"
            >
              <option value="gpt-4o">GPT-4o (Recommended)</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
              <option value="gpt-4-turbo">GPT-4 Turbo</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Temperature: {modelConfig.temperature}</label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={modelConfig.temperature}
              onChange={(e) => setModelConfig({ temperature: parseFloat(e.target.value) })}
              className="w-full"
            />
            <p className="text-xs text-gray-400 mt-1">Lower = more focused, Higher = more creative</p>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Custom API Key (Optional)</label>
            <input
              type="password"
              value={modelConfig.custom_api_key}
              onChange={(e) => setModelConfig({ custom_api_key: e.target.value })}
              placeholder="sk-..."
              className="input-base"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Custom API Base URL (Optional)</label>
            <input
              type="url"
              value={modelConfig.custom_api_base}
              onChange={(e) => setModelConfig({ custom_api_base: e.target.value })}
              placeholder="https://api.example.com/v1"
              className="input-base"
            />
            <p className="text-xs text-gray-400 mt-1">For local models or alternative providers</p>
          </div>
        </div>
      )}
      
      {/* Prompts Tab */}
      {activeTab === 'prompts' && (
        <div className="space-y-4">
          {/* Preset selector */}
          <div>
            <label className="block text-sm font-medium mb-1">Load Preset</label>
            <select
              onChange={(e) => {
                if (e.target.value) {
                  // Apply preset logic here
                }
              }}
              className="input-base"
              defaultValue=""
            >
              <option value="">Select a preset...</option>
              <option value="cinematic">Cinematic Shotlist</option>
              <option value="commercial">Commercial/Advertisement</option>
              <option value="documentary">Documentary Style</option>
              <option value="social_media">Social Media Content</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Vision System Prompt</label>
            <textarea
              value={promptConfig.vision_system}
              onChange={(e) => setPromptConfig({ vision_system: e.target.value })}
              className="input-base h-24 resize-none"
              placeholder="Describe the role for frame analysis..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Vision User Prompt</label>
            <textarea
              value={promptConfig.vision_user}
              onChange={(e) => setPromptConfig({ vision_user: e.target.value })}
              className="input-base h-24 resize-none"
              placeholder="Instructions for analyzing frames..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Shotlist System Prompt</label>
            <textarea
              value={promptConfig.shotlist_system}
              onChange={(e) => setPromptConfig({ shotlist_system: e.target.value })}
              className="input-base h-24 resize-none"
              placeholder="Describe the role for shotlist generation..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1">Shotlist User Prompt</label>
            <textarea
              value={promptConfig.shotlist_user}
              onChange={(e) => setPromptConfig({ shotlist_user: e.target.value })}
              className="input-base h-24 resize-none"
              placeholder="Instructions for generating the shotlist..."
            />
          </div>
          
          <button className="btn-secondary w-full flex items-center justify-center gap-2">
            <Save className="w-4 h-4" />
            Save Custom Prompt
          </button>
        </div>
      )}
    </div>
  )
}
