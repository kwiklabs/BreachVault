'use client'

import { useEffect, useState } from 'react'
import { getStats, type StatsResponse } from '@/lib/api'
import Link from 'next/link'
import { ArrowLeft, Database, Filter, Server } from 'lucide-react'

export default function StatsPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats()
        setStats(data)
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-2xl text-gray-600 dark:text-gray-300">Loading...</div>
      </div>
    )
  }

  return (
    <main className="min-h-screen py-12 px-4">
      <div className="max-w-4xl mx-auto">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline mb-8"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Checker
        </Link>

        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
          Database Statistics
        </h1>

        {stats && (
          <div className="grid gap-6 md:grid-cols-2">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <Database className="w-6 h-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Total Hashes
                </h2>
              </div>
              <p className="text-4xl font-bold text-blue-600">
                {stats.total_hashes.toLocaleString()}
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <Filter className="w-6 h-6 text-green-600" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Bloom Filter Size
                </h2>
              </div>
              <p className="text-4xl font-bold text-green-600">
                {stats.bloom_filter_size.toLocaleString()}
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <Server className="w-6 h-6 text-purple-600" />
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Redis Keys
                </h2>
              </div>
              <p className="text-4xl font-bold text-purple-600">
                {stats.redis_keys.toLocaleString()}
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                Breach Sources
              </h2>
              {stats.sources.length > 0 ? (
                <ul className="space-y-2">
                  {stats.sources.map((source) => (
                    <li
                      key={source}
                      className="text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 px-3 py-2 rounded"
                    >
                      {source}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 dark:text-gray-400">No sources yet</p>
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
