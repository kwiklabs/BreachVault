'use client'

import { useState } from 'react'
import { sha256 } from '@/lib/crypto'
import { checkPassword } from '@/lib/api'
import { BreachResult } from './BreachResult'
import { Shield, Lock, Eye, EyeOff, Sparkles } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-3xl shadow-2xl p-8 border border-gray-200/50 dark:border-gray-700/50">
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="flex items-center gap-3 mb-6"
        >
          <motion.div
            animate={{
              rotate: [0, 5, -5, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              repeatDelay: 3
            }}
          >
            <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </motion.div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent">
            Check Password Security
          </h2>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-gray-600 dark:text-gray-300 mb-6"
        >
          Check if your password has been compromised in a data breach. Your password is
          hashed locally and never sent in plaintext.
        </motion.p>

        <form onSubmit={handleCheck} className="space-y-4">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="relative"
          >
            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500">
              <Lock className="w-5 h-5" />
            </div>
            <input
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password to check..."
              className="w-full pl-12 pr-12 py-4 bg-gray-50/50 dark:bg-gray-700/50 border-2 border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none text-gray-900 dark:text-white transition-all duration-200 placeholder:text-gray-400"
              disabled={loading}
            />
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </motion.button>
          </motion.div>

          <motion.button
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            type="submit"
            disabled={!password || loading}
            className="w-full py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-2 relative overflow-hidden group"
          >
            <AnimatePresence mode="wait">
              {loading ? (
                <motion.div
                  key="loading"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2"
                >
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                  />
                  <span>Checking...</span>
                </motion.div>
              ) : (
                <motion.div
                  key="check"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="flex items-center gap-2"
                >
                  <Sparkles className="w-5 h-5" />
                  <span>Check Password</span>
                </motion.div>
              )}
            </AnimatePresence>
            
            {/* Shimmer effect */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
              initial={{ x: '-100%' }}
              animate={{ x: '100%' }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 1 }}
            />
          </motion.button>
        </form>

        <AnimatePresence>
          {result.checked && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
            >
              <BreachResult result={result} />
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-6 p-4 bg-blue-50/50 dark:bg-blue-900/10 rounded-xl border border-blue-200/50 dark:border-blue-800/50"
        >
          <p className="text-sm text-blue-800 dark:text-blue-200">
            <strong className="font-semibold">🔒 Privacy:</strong> Your password is hashed using SHA-256 in your browser
            before being sent. We never see or store your plaintext password.
          </p>
        </motion.div>
      </div>
    </div>
  )
}
