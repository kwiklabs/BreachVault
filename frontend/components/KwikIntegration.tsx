'use client'

import { useEffect, useState } from 'react'
import { sha256 } from '@/lib/crypto'
import { checkPassword } from '@/lib/api'
import { AlertTriangle } from 'lucide-react'

interface KwikIntegrationProps {
  passphrase: string
  onBreached?: () => void
  debounceMs?: number
}

/**
 * Drop-in component for kwik.gg passphrase inputs
 *
 * Usage:
 * ```tsx
 * import { KwikIntegration } from '@/components/KwikIntegration'
 *
 * function PassphraseModal() {
 *   const [passphrase, setPassphrase] = useState('')
 *   const [showWarning, setShowWarning] = useState(false)
 *
 *   return (
 *     <div>
 *       <input
 *         value={passphrase}
 *         onChange={(e) => setPassphrase(e.target.value)}
 *       />
 *
 *       <KwikIntegration
 *         passphrase={passphrase}
 *         onBreached={() => setShowWarning(true)}
 *       />
 *
 *       {showWarning && (
 *         <div className="text-red-500">
 *           ⚠️ This password has been breached!
 *         </div>
 *       )}
 *     </div>
 *   )
 * }
 * ```
 */
export function KwikIntegration({
  passphrase,
  onBreached,
  debounceMs = 500,
}: KwikIntegrationProps) {
  const [checking, setChecking] = useState(false)
  const [breached, setBreached] = useState(false)
  const [source, setSource] = useState<string>()

  useEffect(() => {
    // Reset state when passphrase changes
    setBreached(false)
    setSource(undefined)

    // Don't check empty passphrases
    if (!passphrase || passphrase.length < 3) {
      return
    }

    // Debounce the check
    const timeoutId = setTimeout(async () => {
      setChecking(true)

      try {
        // Hash passphrase client-side
        const hash = await sha256(passphrase)

        // Check against BreachVault API
        const result = await checkPassword(hash)

        setBreached(result.breached)
        setSource(result.source)

        // Call callback if breached
        if (result.breached && onBreached) {
          onBreached()
        }
      } catch (error) {
        console.error('BreachVault check failed:', error)
        // Fail silently - don't block user if API is down
      } finally {
        setChecking(false)
      }
    }, debounceMs)

    return () => clearTimeout(timeoutId)
  }, [passphrase, debounceMs, onBreached])

  // Don't show anything if not checking and not breached
  if (!checking && !breached) {
    return null
  }

  return (
    <div className="mt-2">
      {checking && (
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Checking breach database...
        </div>
      )}

      {!checking && breached && (
        <div className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-xs font-medium text-red-900 dark:text-red-100">
              This passphrase has been found in a data breach
            </p>
            {source && (
              <p className="text-xs text-red-700 dark:text-red-300 mt-1">
                Source: {source}
              </p>
            )}
            <p className="text-xs text-red-700 dark:text-red-300 mt-1">
              Consider using a different, unique passphrase for better security.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
