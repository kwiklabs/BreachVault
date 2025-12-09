import { PasswordChecker } from '@/components/PasswordChecker'
import Link from 'next/link'
import { BarChart3 } from 'lucide-react'

export default function Home() {
  return (
    <main className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            🔐 BreachVault
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Check if your password has been compromised in a data breach
          </p>
        </div>

        <PasswordChecker />

        <div className="mt-12 text-center space-y-4">
          <Link
            href="/stats"
            className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline"
          >
            <BarChart3 className="w-5 h-5" />
            View Database Statistics
          </Link>

          <div className="text-sm text-gray-500 dark:text-gray-400">
            <Link href="/admin" className="hover:text-gray-700 dark:hover:text-gray-200">
              Admin Panel
            </Link>
          </div>
        </div>

        <footer className="mt-16 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>
            Built for{' '}
            <a
              href="https://kwik.gg"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              kwik.gg
            </a>
          </p>
          <p className="mt-2">
            Securing the web, one password at a time
          </p>
        </footer>
      </div>
    </main>
  )
}
