'use client'

import { useState } from 'react'
import { sha256 } from '@/lib/crypto'
import { checkPassword } from '@/lib/api'
import { BreachResult } from './BreachResult'
import { Shield, Lock, Eye, EyeOff } from 'lucide-react'

export function PasswordChecker() {
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{
    breached: boolean
    source?: string
    checked: boolean
  }>({ breached: false, checked: false })

  const handleCheck = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!password) return

    setLoading(true)
    setResult({ breached: false, checked: false })

    try {
      // Hash password client-side
      const hash = await sha256(password)

      // Check against API
      const response = await checkPassword(hash)

      setResult({
        breached: response.breached,
        source: response.source,
        checked: true,
      })
    } catch (error) {
      console.error('Error checking password:', error)
      alert('Failed to check password. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <Shield className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Check Password Security
          </h1>
        </div>

        <p className="text-gray-600 dark:text-gray-300 mb-6">
          Check if your password has been compromised in a data breach. Your password is
          hashed locally and never sent in plaintext.
        </p>

        <form onSubmit={handleCheck} className="space-y-4">
          <div className="relative">
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
              <Lock className="w-5 h-5" />
            </div>
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password to check..."
              className="w-full pl-12 pr-12 py-4 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-gray-900 dark:text-white"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>

          <button
            type="submit"
            disabled={!password || loading}
            className="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors duration-200"
          >
            {loading ? 'Checking...' : 'Check Password'}
          </button>
        </form>

        {result.checked && <BreachResult result={result} />}

        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong>Privacy:</strong> Your password is hashed using SHA-256 in your browser
            before being sent. We never see or store your plaintext password.
          </p>
        </div>
      </div>
    </div>
  )
}
