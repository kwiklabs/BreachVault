# Contributing to BreachVault

Thank you for your interest in contributing to BreachVault! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include:
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Docker version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Open an issue with the `enhancement` label
2. Describe the feature and its use case
3. Explain why it would benefit BreachVault users
4. Consider implementation complexity

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/kwiklabs/BreachVault.git
   cd BreachVault
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed
   - Keep commits focused and atomic

3. **Test your changes**
   ```bash
   # Start the development environment
   docker compose up --build
   
   # Run backend tests
   cd backend
   pytest
   
   # Run frontend tests
   cd frontend
   pnpm test
   ```

4. **Commit with clear messages**
   ```bash
   git commit -m "feat: add support for custom bloom filter size"
   git commit -m "fix: resolve memory leak in import worker"
   git commit -m "docs: update deployment guide for AWS"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a pull request on GitHub with:
   - Clear title and description
   - Reference related issues
   - Screenshots/videos for UI changes

## Development Setup

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for frontend development)
- Python 3.12+ (for backend development)
- pnpm 8+ (package manager)

### Local Development

```bash
# Install dependencies
cd frontend && pnpm install
cd ../backend && pip install -r requirements.txt

# Start services
docker compose up postgres redis

# Run frontend (hot reload)
cd frontend && pnpm dev

# Run backend (hot reload)
cd backend && uvicorn app.main:app --reload
```

### Code Style

**Frontend (TypeScript/React):**
- Use functional components with hooks
- Follow ESLint configuration
- Use TypeScript strict mode
- Prefer const over let

**Backend (Python):**
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for public functions
- Use async/await for I/O operations

### Testing

- Write unit tests for new features
- Ensure existing tests pass
- Aim for >80% code coverage
- Test edge cases and error handling

## Project Structure

```
BreachVault/
├── frontend/           # Next.js React application
│   ├── app/           # Next.js app router pages
│   └── components/    # Reusable React components
├── backend/           # FastAPI Python application
│   ├── app/          # Application code
│   └── scripts/      # Utility scripts
├── scripts/          # Deployment and setup scripts
└── docs/             # Documentation
```

## Release Process

1. Version bump in package.json and __version__.py
2. Update CHANGELOG.md
3. Create git tag: `git tag v1.x.x`
4. Push tag: `git push origin v1.x.x`
5. GitHub Actions will build and publish

## Questions?

- Open a [GitHub Discussion](https://github.com/kwiklabs/BreachVault/discussions)
- Join our [Discord](https://discord.gg/kwiklabs) (if available)
- Email: support@kwik.gg

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
