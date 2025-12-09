'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { UploadBreachForm } from '@/components/UploadBreachForm'
import { getStats, type StatsResponse } from '@/lib/api'
import Link from 'next/link'
import { LogOut, Home, BarChart3 } from 'lucide-react'

export default function AdminPage() {
  const router = useRouter()
  const [token, setToken] = useState<string | null>(null)
  const [stats, setStats] = useState<StatsResponse | null>(null)

  useEffect(() => {
    // Check if user is logged in
    const storedToken = localStorage.getItem('admin_token')
    if (!storedToken) {
      router.push('/admin/login')
      return
    }
    setToken(storedToken)

    // Fetch stats
    const fetchStats = async () => {
      try {
        const data = await getStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }
    fetchStats()
  }, [router])

  const handleLogout = () => {
    localStorage.removeItem('admin_token')
    router.push('/admin/login')
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl text-gray-600 dark:text-gray-300">Loading...</div>
      </div>
    )
  }

  return (
    <main className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
            Admin Dashboard
          </h1>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>

        <div className="grid gap-6 mb-8">
          <div className="flex gap-4">
            <Link
              href="/"
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              <Home className="w-4 h-4" />
              Home
            </Link>
            <Link
              href="/stats"
              className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              <BarChart3 className="w-4 h-4" />
              Statistics
            </Link>
          </div>
        </div>

        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">Total Hashes</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.total_hashes.toLocaleString()}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">Sources</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.sources.length}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">Bloom Filter</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.bloom_filter_size.toLocaleString()}
              </div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm text-gray-600 dark:text-gray-400">Redis Keys</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.redis_keys.toLocaleString()}
              </div>
            </div>
          </div>
        )}

        <UploadBreachForm token={token} />
      </div>
    </main>
  )
}
