import { create } from 'zustand'
import axios from 'axios'

const API_BASE = '/api'

export const useAppStore = create((set, get) => ({
  // Session state
  sessions: [],
  currentSession: null,
  isLoading: false,
  error: null,
  
  // Model configuration
  modelConfig: {
    transcription_model: 'whisper-1',
    vision_model: 'gpt-4o-mini',
    shotlist_model: 'gpt-4o',
    temperature: 0.7,
    custom_api_key: '',
    custom_api_base: '',
  },
  
  // Prompts
  promptConfig: {
    transcription_system: '',
    transcription_user: '',
    vision_system: '',
    vision_user: '',
    shotlist_system: '',
    shotlist_user: '',
  },
  
  // Preset prompts
  promptPresets: {},
  customPrompts: [],
  
  // Actions
  setModelConfig: (config) => set({ modelConfig: { ...get().modelConfig, ...config } }),
  
  setPromptConfig: (config) => set({ promptConfig: { ...get().promptConfig, ...config } }),
  
  loadPromptPresets: async () => {
    try {
      const response = await axios.get(`${API_BASE}/prompts/presets`)
      set({ promptPresets: response.data })
    } catch (error) {
      console.error('Failed to load prompt presets:', error)
    }
  },
  
  loadCustomPrompts: async () => {
    try {
      const response = await axios.get(`${API_BASE}/prompts/custom`)
      set({ customPrompts: response.data.prompts || [] })
    } catch (error) {
      console.error('Failed to load custom prompts:', error)
    }
  },
  
  saveCustomPrompt: async (name, type, content) => {
    try {
      const formData = new FormData()
      formData.append('name', name)
      formData.append('prompt_type', type)
      formData.append('content', content)
      
      await axios.post(`${API_BASE}/prompts/custom`, formData)
      await get().loadCustomPrompts()
    } catch (error) {
      console.error('Failed to save custom prompt:', error)
      throw error
    }
  },
  
  // Session management
  fetchSessions: async () => {
    try {
      set({ isLoading: true })
      const response = await axios.get(`${API_BASE}/sessions`)
      set({ sessions: response.data.sessions || [], isLoading: false })
    } catch (error) {
      set({ error: error.message, isLoading: false })
      throw error
    }
  },
  
  uploadVideo: async (file, youtubeUrl = null) => {
    try {
      set({ isLoading: true, error: null })
      
      const formData = new FormData()
      if (file) {
        formData.append('file', file)
      }
      if (youtubeUrl) {
        formData.append('youtube_url', youtubeUrl)
      }
      
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      
      const session = response.data
      set({ currentSession: session, isLoading: false })
      
      // Refresh sessions list
      await get().fetchSessions()
      
      return session
    } catch (error) {
      set({ error: error.response?.data?.detail || error.message, isLoading: false })
      throw error
    }
  },
  
  processVideo: async (sessionId, modelConfig, promptConfig) => {
    try {
      set({ isLoading: true, error: null })
      
      const response = await axios.post(
        `${API_BASE}/process/${sessionId}`,
        { model_config: modelConfig, prompt_config: promptConfig },
        { headers: { 'Content-Type': 'application/json' } }
      )
      
      // Update current session with results
      const updatedSession = { ...get().currentSession, ...response.data }
      set({ currentSession: updatedSession, isLoading: false })
      
      // Refresh sessions list
      await get().fetchSessions()
      
      return response.data
    } catch (error) {
      set({ error: error.response?.data?.detail || error.message, isLoading: false })
      throw error
    }
  },
  
  refineShotlist: async (sessionId, feedback, modelConfig) => {
    try {
      set({ isLoading: true, error: null })
      
      const response = await axios.post(
        `${API_BASE}/refine/${sessionId}`,
        { session_id: sessionId, feedback, model_config: modelConfig },
        { headers: { 'Content-Type': 'application/json' } }
      )
      
      // Update current session
      const updatedSession = { ...get().currentSession, shotlist: response.data.shotlist }
      set({ currentSession: updatedSession, isLoading: false })
      
      return response.data
    } catch (error) {
      set({ error: error.response?.data?.detail || error.message, isLoading: false })
      throw error
    }
  },
  
  setCurrentSession: (session) => set({ currentSession: session }),
  
  deleteSession: async (sessionId) => {
    try {
      await axios.delete(`${API_BASE}/session/${sessionId}`)
      await get().fetchSessions()
      
      if (get().currentSession?.session_id === sessionId) {
        set({ currentSession: null })
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
      throw error
    }
  },
  
  exportShotlist: async (sessionId, format) => {
    try {
      const response = await axios.get(`${API_BASE}/export/${sessionId}/${format}`, {
        responseType: 'blob',
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `shotlist_${sessionId}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export shotlist:', error)
      throw error
    }
  },
  
  clearError: () => set({ error: null }),
}))
