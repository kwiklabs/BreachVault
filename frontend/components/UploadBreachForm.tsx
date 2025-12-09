'use client'

import { useState } from 'react'
import { importBreachFile, type ImportResponse } from '@/lib/api'
import { Upload, CheckCircle, XCircle } from 'lucide-react'

interface UploadBreachFormProps {
  token: string
}

export function UploadBreachForm({ token }: UploadBreachFormProps) {
  const [file, setFile] = useState<File | null>(null)
  const [source, setSource] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<ImportResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file || !source) return

    setLoading(true)
    setResult(null)
    setError(null)

    try {
      const response = await importBreachFile(file, source, token)
      setResult(response)
      setFile(null)
      setSource('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to import file')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Upload Breach File
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Source Name
          </label>
          <input
            type="text"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="e.g., rockyou.txt"
            className="w-full px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-900 dark:text-white"
            disabled={loading}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Breach File
          </label>
          <div className="flex items-center gap-4">
            <label className="flex-1 flex items-center gap-2 px-4 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-600">
              <Upload className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              <span className="text-gray-700 dark:text-gray-300">
                {file ? file.name : 'Choose file...'}
              </span>
              <input
                type="file"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="hidden"
                disabled={loading}
                accept=".txt,.csv"
              />
            </label>
          </div>
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            Supports .txt or .csv files with one password/hash per line
          </p>
        </div>

        <button
          type="submit"
          disabled={!file || !source || loading}
          className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors duration-200"
        >
          {loading ? 'Uploading...' : 'Upload and Import'}
        </button>
      </form>

      {result && (
        <div className="mt-6 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-green-900 dark:text-green-100 mb-2">
                Import Complete
              </h3>
              <dl className="space-y-1 text-sm text-green-800 dark:text-green-200">
                <div className="flex justify-between">
                  <dt>Total lines:</dt>
                  <dd className="font-medium">{result.total.toLocaleString()}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Imported:</dt>
                  <dd className="font-medium">{result.imported.toLocaleString()}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Skipped (duplicates):</dt>
                  <dd className="font-medium">{result.skipped.toLocaleString()}</dd>
                </div>
                <div className="flex justify-between">
                  <dt>Source:</dt>
                  <dd className="font-medium">{result.source}</dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      )}

      {error && (
        <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <div className="flex items-start gap-3">
            <XCircle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-red-900 dark:text-red-100 mb-1">
                Import Failed
              </h3>
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
