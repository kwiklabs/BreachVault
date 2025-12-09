'use client'

import { useState } from 'react'
import { useBreachChunkUpload } from '@/hooks/useBreachChunkUpload'
import { Upload, File, X, CheckCircle, AlertCircle, Pause, Play } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface ChunkedBreachUploaderProps {
  token: string
  onComplete?: () => void
}

export function ChunkedBreachUploader({ token, onComplete }: ChunkedBreachUploaderProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const { state, startUpload, pauseUpload, cancelUpload, resetUpload } = useBreachChunkUpload()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // Validate file type
      const validExtensions = ['.txt', '.lst', '.dic', '.wordlist']
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase()
      
      if (!validExtensions.includes(fileExt)) {
        alert(`Invalid file type. Allowed: ${validExtensions.join(', ')}`)
        return
      }

      setSelectedFile(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    await startUpload(selectedFile, token, (progress, hashesProcessed) => {
      // Optional progress callback
      console.log(`Progress: ${progress}%, Hashes: ${hashesProcessed}`)
    })

    if (onComplete) {
      onComplete()
    }
  }

  const handleCancel = async () => {
    await cancelUpload(token)
    setSelectedFile(null)
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  }

  const formatSpeed = (bytesPerSecond: number) => {
    return `${formatBytes(bytesPerSecond)}/s`
  }

  const formatTime = (seconds: number) => {
    if (!isFinite(seconds)) return '∞'
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = Math.floor(seconds % 60)
    
    if (h > 0) return `${h}h ${m}m`
    if (m > 0) return `${m}m ${s}s`
    return `${s}s`
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-gray-200/50 dark:border-gray-700/50">
        <div className="flex items-center gap-3 mb-6">
          <Upload className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Upload Breach Data
          </h2>
        </div>

        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Upload large breach files (up to 100GB). Files are processed in chunks and passwords are hashed directly to the database without storing the full file.
        </p>

        {/* File Selection */}
        {!selectedFile && state.stage === 'idle' && (
          <motion.div
            initial={{ scale: 0.95 }}
            animate={{ scale: 1 }}
            className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl p-12 text-center hover:border-blue-500 dark:hover:border-blue-400 transition-colors cursor-pointer"
          >
            <input
              type="file"
              onChange={handleFileSelect}
              accept=".txt,.lst,.dic,.wordlist"
              className="hidden"
              id="breach-file-input"
            />
            <label htmlFor="breach-file-input" className="cursor-pointer">
              <File className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
                Click to select a breach file
              </p>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                Supported: .txt, .lst, .dic, .wordlist (up to 100GB)
              </p>
            </label>
          </motion.div>
        )}

        {/* Selected File Info */}
        {selectedFile && state.stage === 'idle' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-blue-50/50 dark:bg-blue-900/10 rounded-xl p-6 mb-6 border border-blue-200/50 dark:border-blue-800/50"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <File className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                <div>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {selectedFile.name}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {formatBytes(selectedFile.size)}
                  </p>
                </div>
              </div>
              <button
                aria-label='select file'
                onClick={() => setSelectedFile(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <button
              onClick={handleUpload}
              className="w-full py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Start Upload
            </button>
          </motion.div>
        )}

        {/* Upload Progress */}
        {(state.stage === 'uploading' || state.stage === 'processing') && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {/* Progress Bar */}
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-700 dark:text-gray-300 font-medium">
                  {state.stage === 'uploading' ? 'Uploading & Processing' : 'Processing'}
                </span>
                <span className="text-gray-600 dark:text-gray-400">
                  {state.progress.toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${state.progress}%` }}
                  transition={{ duration: 0.3 }}
                  className="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full"
                />
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50/50 dark:bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Progress
                </p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {formatBytes(state.bytesUploaded)} / {formatBytes(state.totalBytes)}
                </p>
              </div>

              <div className="bg-gray-50/50 dark:bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Chunks
                </p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {state.chunksCompleted} / {state.totalChunks}
                </p>
              </div>

              <div className="bg-gray-50/50 dark:bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Upload Speed
                </p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {formatSpeed(state.uploadSpeed)}
                </p>
              </div>

              <div className="bg-gray-50/50 dark:bg-gray-700/50 rounded-lg p-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">
                  Time Remaining
                </p>
                <p className="text-lg font-semibold text-gray-900 dark:text-white">
                  {formatTime(state.timeRemaining)}
                </p>
              </div>

              <div className="bg-blue-50/50 dark:bg-blue-900/10 rounded-lg p-4 col-span-2">
                <p className="text-xs text-blue-600 dark:text-blue-400 mb-1">
                  Passwords Processed
                </p>
                <p className="text-2xl font-bold text-blue-700 dark:text-blue-300">
                  {state.hashesProcessed.toLocaleString()}
                </p>
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex gap-3">
              <button
                onClick={pauseUpload}
                className="flex-1 py-3 bg-yellow-600 hover:bg-yellow-700 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                <Pause className="w-5 h-5" />
                Pause
              </button>
              <button
                onClick={handleCancel}
                className="flex-1 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                <X className="w-5 h-5" />
                Cancel
              </button>
            </div>
          </motion.div>
        )}

        {/* Complete State */}
        {state.stage === 'complete' && (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-center py-8"
          >
            <CheckCircle className="w-16 h-16 text-green-600 dark:text-green-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Upload Complete!
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Processed {state.hashesProcessed.toLocaleString()} passwords
            </p>
            <button
              onClick={() => {
                resetUpload()
                setSelectedFile(null)
              }}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
            >
              Upload Another File
            </button>
          </motion.div>
        )}

        {/* Error State */}
        {state.stage === 'error' && (
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-center py-8"
          >
            <AlertCircle className="w-16 h-16 text-red-600 dark:text-red-400 mx-auto mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Upload Failed
            </h3>
            <p className="text-red-600 dark:text-red-400 mb-4">
              {state.error}
            </p>
            <button
              onClick={() => {
                resetUpload()
                setSelectedFile(null)
              }}
              className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-semibold rounded-xl transition-colors"
            >
              Try Again
            </button>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
