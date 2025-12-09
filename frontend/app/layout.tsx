import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'BreachVault - Password Breach Checker',
  description: 'Check if your password has been compromised in a data breach',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        {children}
      </body>
    </html>
  )
}
