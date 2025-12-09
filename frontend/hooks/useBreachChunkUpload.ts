'use client'

import { useState, useCallback, useRef } from 'react'

export interface ChunkUploadState {
  stage: 'idle' | 'uploading' | 'processing' | 'complete' | 'error' | 'paused'
  progress: number
  bytesUploaded: number
  totalBytes: number
  chunksCompleted: number
  totalChunks: number
  hashesProcessed: number
  uploadSpeed: number
  timeRemaining: number
  error: string | null
  uploadId: string | null
  isPaused: boolean
}

const initialState: ChunkUploadState = {
  stage: 'idle',
  progress: 0,
  bytesUploaded: 0,
  totalBytes: 0,
  chunksCompleted: 0,
  totalChunks: 0,
  hashesProcessed: 0,
  uploadSpeed: 0,
  timeRemaining: 0,
  error: null,
  uploadId: null,
  isPaused: false,
}

const CHUNK_SIZE = 10 * 1024 * 1024 // 10MB chunks
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function useBreachChunkUpload() {
  const [state, setState] = useState<ChunkUploadState>(initialState)
  const abortControllerRef = useRef<AbortController | null>(null)
  const uploadSpeedHistoryRef = useRef<number[]>([])
  const lastUpdateTimeRef = useRef<number>(0)
  const lastBytesUploadedRef = useRef<number>(0)

  const startUpload = useCallback(async (
    file: File,
    token: string,
    onProgress?: (progress: number, hashesProcessed: number) => void
  ) => {
    try {
      // Calculate total chunks
      const totalChunks = Math.ceil(file.size / CHUNK_SIZE)

      // Initialize upload session
      const formData = new FormData()
      formData.append('filename', file.name)
      formData.append('total_chunks', totalChunks.toString())
      formData.append('file_size', file.size.toString())

      const startResponse = await fetch(`${API_URL}/api/breach/chunk/start`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (!startResponse.ok) {
        throw new Error('Failed to start upload session')
      }

      const { upload_id } = await startResponse.json()

      // Update state
      setState({
        ...initialState,
        stage: 'uploading',
        totalBytes: file.size,
        totalChunks,
        uploadId: upload_id,
      })

      // Create abort controller for cancellation
      abortControllerRef.current = new AbortController()

      // Upload chunks
      let uploadedBytes = 0
      const startTime = Date.now()

      for (let chunkIndex = 0; chunkIndex < totalChunks; chunkIndex++) {
        // Check if upload was cancelled
        if (abortControllerRef.current?.signal.aborted) {
          setState((prev) => ({ ...prev, stage: 'paused' }))
          return
        }

        // Extract chunk from file
        const start = chunkIndex * CHUNK_SIZE
        const end = Math.min(start + CHUNK_SIZE, file.size)
        const chunkBlob = file.slice(start, end)

        // Prepare chunk upload
        const chunkFormData = new FormData()
        chunkFormData.append('upload_id', upload_id)
        chunkFormData.append('chunk_index', chunkIndex.toString())
        chunkFormData.append('total_chunks', totalChunks.toString())
        chunkFormData.append('chunk', chunkBlob, `chunk_${chunkIndex}`)

        // Upload chunk with retry logic
        let retries = 3
        let uploaded = false

        while (retries > 0 && !uploaded) {
          try {
            const chunkResponse = await fetch(
              `${API_URL}/api/breach/chunk/upload`,
              {
                method: 'POST',
                headers: {
                  Authorization: `Bearer ${token}`,
                },
                body: chunkFormData,
                signal: abortControllerRef.current?.signal,
              }
            )

            if (!chunkResponse.ok) {
              throw new Error(`Chunk upload failed: ${chunkResponse.statusText}`)
            }

            const result = await chunkResponse.json()
            uploaded = true

            // Update progress
            uploadedBytes += chunkBlob.size
            const currentTime = Date.now()
            const elapsedTime = (currentTime - startTime) / 1000 // seconds
            const uploadSpeed = uploadedBytes / elapsedTime // bytes per second

            // Calculate speed (smoothed)
            uploadSpeedHistoryRef.current.push(uploadSpeed)
            if (uploadSpeedHistoryRef.current.length > 10) {
              uploadSpeedHistoryRef.current.shift()
            }

            const avgSpeed =
              uploadSpeedHistoryRef.current.reduce((a, b) => a + b, 0) /
              uploadSpeedHistoryRef.current.length

            const remainingBytes = file.size - uploadedBytes
            const timeRemaining = remainingBytes / avgSpeed

            setState({
              stage: result.is_complete ? 'complete' : 'uploading',
              progress: result.progress,
              bytesUploaded: uploadedBytes,
              totalBytes: file.size,
              chunksCompleted: result.chunks_completed,
              totalChunks,
              hashesProcessed: result.total_hashes_processed,
              uploadSpeed: avgSpeed,
              timeRemaining,
              error: null,
              uploadId: upload_id,
              isPaused: false,
            })

            // Call progress callback
            if (onProgress) {
              onProgress(result.progress, result.total_hashes_processed)
            }

            // Break if upload is complete
            if (result.is_complete) {
              break
            }
          } catch (error: any) {
            retries--
            if (retries === 0) {
              throw error
            }
            // Wait before retry
            await new Promise((resolve) => setTimeout(resolve, 1000))
          }
        }
      }

      // Upload completed successfully
      setState((prev) => ({
        ...prev,
        stage: 'complete',
        progress: 100,
      }))
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        stage: 'error',
        error: error.message || 'Upload failed',
      }))
    }
  }, [])

  const pauseUpload = useCallback(() => {
    abortControllerRef.current?.abort()
    setState((prev) => ({ ...prev, stage: 'paused', isPaused: true }))
  }, [])

  const cancelUpload = useCallback(async (token: string) => {
    if (state.uploadId) {
      try {
        await fetch(`${API_URL}/api/breach/chunk/cancel/${state.uploadId}`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
      } catch (error) {
        console.error('Failed to cancel upload:', error)
      }
    }
    abortControllerRef.current?.abort()
    setState(initialState)
  }, [state.uploadId])

  const resetUpload = useCallback(() => {
    setState(initialState)
    uploadSpeedHistoryRef.current = []
  }, [])

  return {
    state,
    startUpload,
    pauseUpload,
    cancelUpload,
    resetUpload,
  }
}
