'use client'

import { PasswordChecker } from '@/components/PasswordChecker'
import Link from 'next/link'
import { BarChart3, Shield, Lock, Zap, Github } from 'lucide-react'
import { motion } from 'framer-motion'

const fadeIn = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 }
}

const stagger = {
  animate: {
    transition: {
      staggerChildren: 0.1
    }
  }
}

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-indigo-950">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 90, 0],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-blue-400/10 to-purple-400/10 rounded-full blur-3xl"
          />
          <motion.div
            animate={{
              scale: [1.2, 1, 1.2],
              rotate: [90, 0, 90],
            }}
            transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
            className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-indigo-400/10 to-cyan-400/10 rounded-full blur-3xl"
          />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 py-16 sm:px-6 lg:px-8">
          {/* Header with GitHub link */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-between items-center mb-12"
          >
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400 bg-clip-text text-transparent">
                BreachVault
              </span>
            </div>
            <motion.a
              href="https://github.com/kwiklabs/BreachVault"
              target="_blank"
              rel="noopener noreferrer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="flex items-center gap-2 px-4 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-lg hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
            >
              <Github className="w-5 h-5" />
              <span className="font-medium">Star on GitHub</span>
            </motion.a>
          </motion.div>

          {/* Hero Content */}
          <motion.div
            variants={stagger}
            initial="initial"
            animate="animate"
            className="text-center mb-16"
          >
            <motion.h1
              variants={fadeIn}
              className="text-5xl sm:text-6xl lg:text-7xl font-bold text-gray-900 dark:text-white mb-6"
            >
              <span className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 dark:from-blue-400 dark:via-indigo-400 dark:to-purple-400 bg-clip-text text-transparent">
                Secure Passwords.
              </span>
              <br />
              <span className="text-gray-900 dark:text-white">
                Instant Verification.
              </span>
            </motion.h1>
            <motion.p
              variants={fadeIn}
              className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto mb-8"
            >
              Check if your password has been compromised in over{' '}
              <span className="font-semibold text-blue-600 dark:text-blue-400">
                1.5 billion
              </span>{' '}
              known data breaches
            </motion.p>

            {/* Feature Pills */}
            <motion.div
              variants={fadeIn}
              className="flex flex-wrap justify-center gap-3 mb-12"
            >
              {[
                { icon: Lock, text: 'Client-side Hashing' },
                { icon: Zap, text: 'Ultra-fast Lookup' },
                { icon: Shield, text: 'Privacy First' }
              ].map((feature, i) => (
                <motion.div
                  key={i}
                  whileHover={{ scale: 1.05, y: -2 }}
                  className="flex items-center gap-2 px-4 py-2 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-full shadow-lg"
                >
                  <feature.icon className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {feature.text}
                  </span>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>

          {/* Password Checker Component */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <PasswordChecker />
          </motion.div>

          {/* Stats and Links */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="mt-16 text-center space-y-6"
          >
            <Link
              href="/stats"
              className="inline-flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:underline text-lg font-medium"
            >
              <BarChart3 className="w-5 h-5" />
              View Database Statistics
            </Link>

            <div className="text-sm text-gray-500 dark:text-gray-400">
              <Link
                href="/admin"
                className="hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
              >
                Admin Panel
              </Link>
            </div>
          </motion.div>

          {/* Footer */}
          <motion.footer
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-24 text-center text-sm text-gray-500 dark:text-gray-400"
          >
            <p>
              Built by{' '}
              <a
                href="https://github.com/kwiklabs"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
              >
                kwiklabs
              </a>
              {' '}for{' '}
              <a
                href="https://kwik.gg"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
              >
                kwik.gg
              </a>
            </p>
            <p className="mt-2">
              Securing the web, one password at a time
            </p>
          </motion.footer>
        </div>
      </div>
    </main>
  )
}
