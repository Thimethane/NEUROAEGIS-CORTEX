# 🤝 Contributing to AegisAI

Thank you for your interest in contributing to AegisAI! This document provides guidelines and instructions for contributing.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Community](#community)

---

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Background
- Identity
- Personal characteristics

### Expected Behavior

- ✅ Be respectful and constructive
- ✅ Welcome newcomers warmly
- ✅ Accept constructive criticism gracefully
- ✅ Focus on what's best for the project
- ✅ Show empathy towards others

### Unacceptable Behavior

- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Personal or political attacks
- ❌ Publishing others' private information
- ❌ Unprofessional conduct

---

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Git** installed and configured
- **Node.js 18+** for frontend development
- **Python 3.9+** for backend development
- **Docker** (optional, for testing deployments)
- **Code editor** (VS Code recommended)

### Fork and Clone

```bash
# 1. Fork the repository on GitHub
# Click "Fork" button at https://github.com/Thimethane/NEUROAEGIS-CORTEX

# 2. Clone your fork
git clone https://github.com/Thimethane/NEUROAEGIS-CORTEX
cd aegisai

# 3. Add upstream remote
git remote add upstream https://github.com/Thimethane/NEUROAEGIS-CORTEX

# 4. Verify remotes
git remote -v
```

### Initial Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools

# Install pre-commit hooks
pip install pre-commit
pre-commit install
```

---

## 🔄 Development Workflow

### Branch Strategy

We use **feature branches** for development:

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# OR for bug fixes
git checkout -b fix/bug-description

# OR for documentation
git checkout -b docs/what-you-are-documenting
```

### Branch Naming Convention

- `feature/` - New features (e.g., `feature/multi-camera-support`)
- `fix/` - Bug fixes (e.g., `fix/camera-permission-error`)
- `docs/` - Documentation (e.g., `docs/api-guide`)
- `refactor/` - Code refactoring (e.g., `refactor/agent-architecture`)
- `test/` - Test additions (e.g., `test/integration-tests`)

### Making Changes

```bash
# Make your changes
# Edit files, add features, fix bugs

# Check status
git status

# Stage changes
git add .

# Commit with meaningful message
git commit -m "feat: add multi-camera support"

# Push to your fork
git push origin feature/your-feature-name
```

### Commit Message Format

We follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, no logic change)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

**Examples:**

```bash
# Good commits
git commit -m "feat(frontend): add dark mode toggle"
git commit -m "fix(backend): resolve camera disconnection crash"
git commit -m "docs: update installation guide for Windows"

# Bad commits (avoid)
git commit -m "fixed stuff"
git commit -m "updates"
git commit -m "WIP"
```

---

## 🎨 Coding Standards

### Frontend (TypeScript/React)

#### File Structure

```typescript
// components/MyComponent/MyComponent.tsx
import React from 'react';
import { ComponentProps } from '@/types';

interface MyComponentProps {
  title: string;
  onAction?: () => void;
}

export const MyComponent: React.FC<MyComponentProps> = ({ 
  title, 
  onAction 
}) => {
  // Component logic
  return (
    <div className="my-component">
      {title}
    </div>
  );
};
```

#### TypeScript Rules

- ✅ Use explicit types, avoid `any`
- ✅ Use interfaces for props
- ✅ Use enums for constants
- ✅ Enable strict mode
- ✅ Document complex types

```typescript
// Good
interface User {
  id: string;
  name: string;
  role: 'admin' | 'user';
}

// Avoid
const user: any = { ... };
```

#### React Best Practices

```typescript
// ✅ Use functional components
const MyComponent: React.FC<Props> = (props) => { ... };

// ✅ Use hooks properly
const [state, setState] = useState<Type>(initialValue);

// ✅ Memoize expensive computations
const result = useMemo(() => expensiveCalc(data), [data]);

// ✅ Clean up effects
useEffect(() => {
  const timer = setInterval(...);
  return () => clearInterval(timer);
}, []);
```

#### CSS/Styling

- Use **TailwindCSS** utility classes
- Follow mobile-first approach
- Use consistent spacing scale
- Prefer composition over duplication

```tsx
// Good
<div className="flex items-center gap-4 p-4 bg-gray-900 rounded-lg">

// Avoid inline styles
<div style={{ display: 'flex', padding: '16px' }}>
```

### Backend (Python)

#### Code Style

We follow **PEP 8** with some modifications:

```python
# Good
class VisionAgent(BaseAgent):
    """Vision analysis agent using Gemini API.
    
    Attributes:
        model_name: Gemini model identifier
        frame_history: List of recent frames for context
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        super().__init__()
        self.model_name = model_name
        self.frame_history: List[Dict] = []
    
    async def process(
        self, 
        frame: np.ndarray, 
        frame_number: int
    ) -> Dict[str, Any]:
        """Process a video frame for threat detection."""
        # Implementation
        pass
```

#### Type Hints

Always use type hints:

```python
# Good
def analyze_frame(
    frame: np.ndarray, 
    timestamp: datetime
) -> Dict[str, Any]:
    pass

# Avoid
def analyze_frame(frame, timestamp):
    pass
```

#### Error Handling

```python
# Good - Specific exceptions
try:
    result = await api_call()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except APIError as e:
    logger.warning(f"API error: {e}")
    return fallback_result()

# Avoid - Bare except
try:
    result = risky_operation()
except:
    pass
```

#### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed diagnostic info")
logger.info("General informational messages")
logger.warning("Warning messages")
logger.error("Error messages")
logger.critical("Critical issues")

# Include context
logger.error(
    "Failed to process frame",
    extra={
        "frame_number": frame_num,
        "error": str(e)
    }
)
```

---

## 🧪 Testing Guidelines

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- VideoFeed.test.tsx

# Watch mode
npm test -- --watch
```

#### Writing Tests

```typescript
// MyComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { MyComponent } from './MyComponent';

describe('MyComponent', () => {
  it('renders title correctly', () => {
    render(<MyComponent title="Test" />);
    expect(screen.getByText('Test')).toBeInTheDocument();
  });

  it('calls onAction when button clicked', () => {
    const onAction = jest.fn();
    render(<MyComponent title="Test" onAction={onAction} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(onAction).toHaveBeenCalledTimes(1);
  });
});
```

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Run by marker
pytest -m unit
pytest -m integration
```

#### Writing Tests

```python
# test_vision_agent.py
import pytest
from agents.vision_agent import VisionAgent

@pytest.fixture
def vision_agent():
    return VisionAgent()

@pytest.mark.asyncio
async def test_analyze_frame(vision_agent):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = await vision_agent.process(frame, frame_number=1)
    
    assert result is not None
    assert 'incident' in result
    assert 'confidence' in result
    assert 0 <= result['confidence'] <= 100

@pytest.mark.integration
async def test_full_analysis_pipeline(vision_agent):
    # Integration test
    pass
```

### Test Coverage Requirements

- **Minimum 70% overall coverage**
- **80%+ for critical components**:
  - AI agents
  - API endpoints
  - Database operations
- **100% for utility functions**

---

## 📝 Documentation

### Code Documentation

#### TypeScript/React

```typescript
/**
 * Custom hook for managing video monitoring state
 * 
 * @param initialInterval - Frame capture interval in ms
 * @returns Monitoring state and control functions
 * 
 * @example
 * ```tsx
 * const { isActive, toggleMonitoring } = useMonitoring(4000);
 * ```
 */
export const useMonitoring = (initialInterval: number = 4000) => {
  // Implementation
};
```

#### Python

```python
def process_frame(
    frame: np.ndarray,
    context: Dict[str, Any]
) -> AnalysisResult:
    """Process a single video frame for threat detection.
    
    Args:
        frame: BGR image array from OpenCV
        context: Additional context including timestamp, location
        
    Returns:
        Analysis result containing threat type, confidence, and actions
        
    Raises:
        ValueError: If frame dimensions are invalid
        APIError: If Gemini API call fails
        
    Example:
        >>> frame = cv2.imread('test.jpg')
        >>> result = process_frame(frame, {'timestamp': datetime.now()})
        >>> print(result.confidence)
        85.5
    """
    pass
```

### README Updates

When adding features, update relevant documentation:

- `README.md` - Main project overview
- `QUICKSTART.md` - Quick start instructions
- `INTEGRATION.md` - Integration details
- `DEPLOYMENT.md` - Deployment procedures

---

## 🔍 Code Review Process

### Before Submitting PR

**Self-Review Checklist:**

- [ ] Code follows style guidelines
- [ ] All tests pass locally
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] No console.log or debug statements
- [ ] Commits follow conventional format
- [ ] No merge conflicts with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots here]

## Related Issues
Closes #123
```

### Review Guidelines

Reviewers will check:

1. **Functionality**: Does it work as intended?
2. **Code Quality**: Is it maintainable?
3. **Tests**: Are there adequate tests?
4. **Documentation**: Is it documented?
5. **Performance**: Any performance implications?
6. **Security**: Any security concerns?

---

## 🚀 Submitting Changes

### Create Pull Request

```bash
# 1. Push your branch
git push origin feature/your-feature-name

# 2. Go to GitHub and create PR
# - Base: main
# - Compare: feature/your-feature-name

# 3. Fill out PR template
# 4. Request review
# 5. Address feedback
```

### After PR is Merged

```bash
# 1. Switch to main
git checkout main

# 2. Pull latest changes
git pull upstream main

# 3. Delete feature branch
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## 🏷️ Issue Guidelines

### Creating Issues

Use these templates:

**Bug Report:**
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Expected vs actual

## Environment
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- Version: [e.g., 2.5.0]

## Screenshots
[If applicable]
```

**Feature Request:**
```markdown
## Feature Description
What feature do you want?

## Use Case
Why is this useful?

## Proposed Solution
How might this work?

## Alternatives Considered
Other approaches?
```

---

## 🌟 Recognition

### Contributors Hall of Fame

All contributors are recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes

### Types of Contributions

We value all contributions:

- 💻 **Code** - New features, bug fixes
- 📝 **Documentation** - Guides, tutorials, translations
- 🎨 **Design** - UI/UX improvements
- 🧪 **Testing** - Writing tests, reporting bugs
- 💡 **Ideas** - Feature suggestions, architectural input
- 🤝 **Community** - Helping others, answering questions

---

## ❓ Questions?

- **Technical Questions**: [GitHub Discussions](https://github.com/Thimethane/NEUROAEGIS-CORTEX/discussions)
- **Bug Reports**: [GitHub Issues](https://github.com/Thimethane/NEUROAEGIS-CORTEX/issues)
- **Security Issues**: security@aegisai.dev (private)

---

## 📚 Resources

### Learning Resources

- **React**: https://react.dev/learn
- **TypeScript**: https://www.typescriptlang.org/docs/
- **FastAPI**: https://fastapi.tiangolo.com/tutorial/
- **Gemini API**: https://ai.google.dev/docs

### Development Tools

- **VS Code Extensions**:
  - ESLint
  - Prettier
  - Python
  - TypeScript and JavaScript Language Features
  - Tailwind CSS IntelliSense

---

**Thank you for contributing to AegisAI! Together, we're building the future of autonomous security.** 🛡️

---

*Last Updated: February 2026*
