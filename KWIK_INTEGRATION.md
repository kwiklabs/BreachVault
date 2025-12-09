# Integrating BreachVault into kwik.gg

This guide shows you how to integrate BreachVault's password breach checking into your kwik.gg passphrase inputs.

## Quick Integration

### 1. Copy the Component

Copy the `KwikIntegration.tsx` component from `frontend/components/KwikIntegration.tsx` into your kwik.gg project.

Also copy the required utilities:
- `lib/crypto.ts` - Client-side SHA-256 hashing
- `lib/api.ts` - API communication functions

### 2. Install Dependencies

```bash
npm install lucide-react
```

### 3. Use in Your Passphrase Modal

```tsx
import { useState } from 'react'
import { KwikIntegration } from '@/components/KwikIntegration'

export function PassphraseModal() {
  const [passphrase, setPassphrase] = useState('')
  const [showWarning, setShowWarning] = useState(false)

  return (
    <div className="modal">
      <h2>Enter Passphrase</h2>

      <input
        type="password"
        value={passphrase}
        onChange={(e) => setPassphrase(e.target.value)}
        placeholder="Enter your passphrase..."
      />

      {/* Drop-in BreachVault integration */}
      <KwikIntegration
        passphrase={passphrase}
        onBreached={() => setShowWarning(true)}
        debounceMs={500}
      />

      {showWarning && (
        <div className="warning">
          ⚠️ Warning: This passphrase has been found in a data breach!
          Consider using a different one.
        </div>
      )}

      <button onClick={handleSubmit}>
        Continue
      </button>
    </div>
  )
}
```

## API Configuration

Set the BreachVault API URL in your environment variables:

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://breachvault.yourdomain.com
```

For local development:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Component Props

### `KwikIntegration`

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `passphrase` | `string` | required | The passphrase to check |
| `onBreached` | `() => void` | optional | Callback when breach is detected |
| `debounceMs` | `number` | `500` | Debounce delay in milliseconds |

## Features

✅ **Client-side hashing** - Password never leaves the browser in plaintext
✅ **Automatic debouncing** - Reduces API calls while user types
✅ **Silent failure** - Won't block user if API is down
✅ **Minimal UI** - Shows warning only when needed
✅ **Zero-config** - Works out of the box with sensible defaults

## Security Notes

1. **Never send plaintext passwords** - The component automatically hashes passwords using SHA-256 before sending to the API
2. **Client-side validation** - All hashing happens in the browser
3. **Privacy-first** - No passwords are ever logged or stored by BreachVault
4. **HTTPS required** - Always use HTTPS in production

## Customization

### Custom Styling

The component uses Tailwind CSS classes. Customize the appearance:

```tsx
// Modify the className in KwikIntegration.tsx
<div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
  {/* Your custom warning UI */}
</div>
```

### Different Debounce Timing

```tsx
<KwikIntegration
  passphrase={passphrase}
  debounceMs={1000}  // Wait 1 second before checking
/>
```

### Manual Control

For more control, you can use the API functions directly:

```tsx
import { sha256 } from '@/lib/crypto'
import { checkPassword } from '@/lib/api'

async function checkPassphrase(passphrase: string) {
  const hash = await sha256(passphrase)
  const result = await checkPassword(hash)

  if (result.breached) {
    console.log('Breach detected!', result.source)
  }
}
```

## Deployment

Deploy BreachVault to your infrastructure:

```bash
# Build and start all services
docker compose up -d

# Access the API at http://localhost:8000
# Access the frontend at http://localhost:3000
```

For production deployment, see the main README.md for Kubernetes, AWS, GCP, and Azure guides.

## Support

If you encounter any issues integrating BreachVault:

1. Check the [main README](./README.md)
2. Open an issue on GitHub
3. Contact support@breachvault.dev

---

**Built with ❤️ for kwik.gg**
