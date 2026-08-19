import React from 'react'
import { useAppStore } from '../store/appStore'
import { Download, FileJson, FileSpreadsheet, FileType, FileText } from 'lucide-react'

export default function ExportButtons({ sessionId }) {
  const { exportShotlist } = useAppStore()
  
  const exportOptions = [
    { format: 'html', label: 'HTML', icon: FileType },
    { format: 'csv', label: 'CSV', icon: FileSpreadsheet },
    { format: 'json', label: 'JSON', icon: FileJson },
    { format: 'markdown', label: 'Markdown', icon: FileText },
  ]
  
  const handleExport = async (format) => {
    try {
      await exportShotlist(sessionId, format)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }
  
  return (
    <div className="flex gap-2 flex-wrap">
      {exportOptions.map((option) => {
        const Icon = option.icon
        return (
          <button
            key={option.format}
            onClick={() => handleExport(option.format)}
            className="btn-secondary flex items-center gap-2"
          >
            <Icon className="w-4 h-4" />
            {option.label}
          </button>
        )
      })}
    </div>
  )
}
