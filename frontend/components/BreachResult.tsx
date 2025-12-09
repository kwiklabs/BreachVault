'use client'

import { AlertTriangle, CheckCircle } from 'lucide-react'

interface BreachResultProps {
  result: {
    breached: boolean
    source?: string
    checked: boolean
  }
}

export function BreachResult({ result }: BreachResultProps) {
  if (!result.checked) return null

  if (result.breached) {
    return (
      <div className="mt-6 p-6 bg-red-50 dark:bg-red-900/20 border-2 border-red-200 dark:border-red-800 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-6 h-6 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
              Password Compromised!
            </h3>
            <p className="text-red-800 dark:text-red-200 mb-3">
              This password has been found in a data breach and should not be used.
            </p>
            {result.source && (
              <p className="text-sm text-red-700 dark:text-red-300">
                <strong>Source:</strong> {result.source}
              </p>
            )}
            <div className="mt-4 p-3 bg-white dark:bg-gray-800 rounded">
              <p className="text-sm text-gray-700 dark:text-gray-300">
                <strong>Recommendation:</strong> Choose a different, stronger password. Use a
                password manager to generate and store unique passwords.
              </p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="mt-6 p-6 bg-green-50 dark:bg-green-900/20 border-2 border-green-200 dark:border-green-800 rounded-lg">
      <div className="flex items-start gap-3">
        <CheckCircle className="w-6 h-6 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
        <div>
          <h3 className="text-lg font-semibold text-green-900 dark:text-green-100 mb-2">
            Password Safe
          </h3>
          <p className="text-green-800 dark:text-green-200">
            This password has not been found in any known data breaches. However, always use
            strong, unique passwords for each account.
          </p>
        </div>
      </div>
    </div>
  )
}
