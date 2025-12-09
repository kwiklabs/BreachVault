# Quick Start: Claim BreachVault on GitHub

## 1. Create GitHub Repository

Go to GitHub and create a new repository:
- **Name:** `BreachVault`
- **Visibility:** Public (or Private)
- **Do NOT initialize** with README, .gitignore, or license (we already have these)

## 2. Push to GitHub

```bash
cd /home/mmi/kwiklabs/BreachVault

# Add remote (replace 'kwiklabs' with your GitHub username if different)
git remote add origin https://github.com/kwiklabs/BreachVault.git

# Push to GitHub
git push -u origin canary

# Or if you want to use 'main' branch:
git branch -M main
git push -u origin main
```

## 3. Configure Repository Settings

### Add Topics (for discoverability)
- password-security
- breach-detection
- fastapi
- nextjs
- postgresql
- redis
- docker
- cybersecurity
- privacy
- bloom-filter

### Add Description
```
🔐 Production-ready password breach checker. Upload 100GB+ breach files with chunked streaming. Bloom Filter → Redis → PostgreSQL cascade for ultra-fast lookups.
```

### Enable Features
- ✅ Issues
- ✅ Discussions
- ✅ Projects (optional)
- ✅ Wiki (optional)

### Add Repository Homepage
```
https://breachvault.yourdomain.com
```
(or leave blank until deployed)

## 4. Add GitHub Actions (Optional)

Create `.github/workflows/docker-build.yml`:

```yaml
name: Docker Build

on:
  push:
    branches: [ main, canary ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build backend
      run: docker build -t breachvault-backend ./backend
    
    - name: Build frontend
      run: docker build -t breachvault-frontend ./frontend
```

## 5. Add Badges to README

Add these at the top of `README.md`:

```markdown
# BreachVault 🔐

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/kwiklabs/BreachVault?style=social)
![GitHub forks](https://img.shields.io/github/forks/kwiklabs/BreachVault?style=social)
![GitHub license](https://img.shields.io/github/license/kwiklabs/BreachVault)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)

</div>
```

## 6. Share on Social Media

**Twitter/X:**
```
🔐 Just open-sourced BreachVault - a production-ready password breach checker!

✨ Features:
• Upload 100GB+ files without crashing
• Chunked streaming (no temp files!)
• Bloom Filter → Redis → PostgreSQL
• Modern UI with @framer Motion

Built with @nextjs + @fastapi

https://github.com/kwiklabs/BreachVault

#cybersecurity #opensource #privacy
```

**Reddit (r/programming, r/privacy):**
```
Title: [Open Source] BreachVault - Handle 100GB+ password breach files without crashing

I built a production-ready password breach checker that can handle massive 
files (tested with 40GB+) using chunked streaming. No temporary file storage 
needed - passwords are hashed and inserted directly to the database.

Tech stack: Next.js 16, FastAPI, PostgreSQL, Redis, Bloom Filters

Key features:
- Memory efficient: ~100MB regardless of file size
- Real-time progress with framer-motion UI
- Docker deployment ready
- Comprehensive docs (deployment, contributing, etc.)

GitHub: https://github.com/kwiklabs/BreachVault
```

## 7. Set Up GitHub Pages (Optional)

Create `docs/index.html` for a landing page:

```html
<!DOCTYPE html>
<html>
<head>
  <title>BreachVault - Password Breach Checker</title>
  <meta name="description" content="Production-ready password breach checker">
</head>
<body>
  <h1>🔐 BreachVault</h1>
  <p>Check if your password has been compromised in a data breach.</p>
  <a href="https://github.com/kwiklabs/BreachVault">View on GitHub</a>
</body>
</html>
```

Enable in Settings → Pages → Source: `main` branch, `/docs` folder

## 8. Add Sponsors (Optional)

Create `.github/FUNDING.yml`:

```yaml
github: kwiklabs
custom: ['https://kwik.gg/sponsor']
```

## You're Done! 🎉

Your repository is now:
- ✅ Fully branded under kwiklabs
- ✅ Production deployment ready
- ✅ Documented (README, CONTRIBUTING, DEPLOYMENT_GUIDE)
- ✅ Handles 100GB+ files with chunked streaming
- ✅ Modern animated UI
- ✅ Configurable for any environment

Next steps:
1. Deploy to production (see DEPLOYMENT_GUIDE.md)
2. Upload your first breach dataset
3. Share with the community
4. Accept contributions!
