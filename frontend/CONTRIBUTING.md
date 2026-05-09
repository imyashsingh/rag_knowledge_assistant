# Contributing to RAG Knowledge Assistant Frontend

Thank you for your interest in contributing to the RAG Knowledge Assistant frontend! This guide will help you get started with development, testing, and contributing to the project.

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Node.js**: Version 18 or higher
- **npm**: Latest stable version
- **Git**: Configured with your name and email
- **Code Editor**: VS Code (recommended) with extensions:
  - TypeScript and JavaScript language features
  - ESLint for code quality
  - Prettier for code formatting
  - Tailwind CSS IntelliSense

### Development Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub
   git clone https://github.com/your-username/rag-knowledge-assistant.git
   cd rag-knowledge-assistant/frontend
   ```

2. **Install Dependencies**
   ```bash
   npm install
   ```

3. **Environment Configuration**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Configure your local backend
   echo "VITE_API_URL=http://localhost:8000" >> .env
   ```

4. **Start Development**
   ```bash
   npm run dev
   ```

5. **Verify Setup**
   - Open `http://localhost:3000`
   - Check browser console for errors
   - Test backend connectivity

## 🏗️ Project Structure

Understanding the project structure is crucial for effective contributions:

```
src/
├── components/          # Reusable UI components
│   ├── ui/           # Base UI components (Button, Input, Card)
│   ├── auth/          # Authentication-specific components
│   └── layout/        # Layout components
├── pages/              # Route components
│   └── auth/          # Authentication pages
├── services/           # API service layer
├── stores/              # State management (Zustand)
├── utils/               # Utility functions
├── types/               # TypeScript type definitions
├── constants/           # Application constants
├── hooks/               # Custom React hooks
└── assets/              # Static assets
```

## 🎨 Development Guidelines

### Code Style

We use **ESLint** and **Prettier** to maintain consistent code style:

```typescript
// ✅ Good Example
const getUserData = async (userId: string): Promise<User> => {
  try {
    const response = await userService.get(userId)
    return response.data
  } catch (error) {
    throw new Error(`Failed to fetch user: ${error.message}`)
  }
}

// ❌ Bad Example
const getUserData = async (userId) => {
  const response = await userService.get(userId)
  return response.data
}
```

### TypeScript Guidelines

- **Strict Mode**: All code must be properly typed
- **Interfaces**: Use interfaces for all data structures
- **Generics**: Use generics for reusable functions
- **No `any`**: Avoid `any` type except when absolutely necessary

```typescript
// ✅ Proper Typing
interface User {
  id: number
  email: string
  name: string
  workspace_id: number
}

const fetchUser = async (id: number): Promise<User> => {
  const response = await api.get<User>(`/users/${id}`)
  return response.data
}

// ❌ Avoid This
const fetchUser = async (id: any): Promise<any> => {
  const response = await api.get(`/users/${id}`)
  return response.data
}
```

### Component Guidelines

- **Functional Components**: Use function components with hooks
- **Props Interface**: Define clear prop interfaces
- **Default Exports**: Use default exports for components
- **Composition**: Favor composition over inheritance

```typescript
// ✅ Component Pattern
interface ButtonProps {
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  children: React.ReactNode
  onClick?: () => void
}

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  children,
  onClick,
  ...props
}) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size }))}
      onClick={onClick}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button
```

## 🧪 Testing Guidelines

### Testing Philosophy

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test component interactions
- **E2E Tests**: Test user workflows
- **Coverage**: Maintain >80% test coverage

### Writing Tests

```typescript
// Component Test Example
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from '../Button'

describe('Button Component', () => {
  it('renders with primary variant', () => {
    render(<Button variant="primary">Click me</Button>)
    expect(screen.getByRole('button')).toHaveClass('bg-primary')
  })

  it('handles click events', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('applies size variants correctly', () => {
    render(<Button size="lg">Large Button</Button>)
    expect(screen.getByRole('button')).toHaveClass('h-11 px-8 text-lg')
  })
})
```

### Running Tests

```bash
# Run all tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run E2E tests
npm run test:e2e
```

## 📋 Development Workflow

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Commit Changes**
   ```bash
   # Stage all changes
   git add .
   
   # Commit with conventional message
   git commit -m "feat: add user authentication"
   ```

4. **Push and Create PR**
   ```bash
   # Push to your fork
   git push origin feature/your-feature-name
   
   # Create Pull Request on GitHub
   ```

### Conventional Commits

We use [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

- `feat:` New feature or functionality
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, missing semi-colons, etc)
- `refactor:` Code refactoring without functional changes
- `test:` Adding or updating tests
- `chore:` Maintenance tasks (updating dependencies, etc.)

Examples:
```bash
git commit -m "feat: add document upload functionality"
git commit -m "fix: resolve authentication token refresh issue"
git commit -m "docs: update API integration guide"
```

## 🐛 Bug Reports

### Reporting Issues

When reporting bugs, please include:

1. **Environment Information**
   - OS and version
   - Browser and version
   - Node.js version
   - npm version

2. **Steps to Reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Code Context**
   - Relevant component names
   - Error messages from console
   - Network requests/responses

### Bug Report Template

```markdown
## Bug Description
**Brief description of the bug**

### Environment
- OS: [e.g., Ubuntu 22.04]
- Browser: [e.g., Chrome 120.0]
- Node.js: [e.g., 18.17.0]
- npm: [e.g., 9.6.7]

### Steps to Reproduce
1. Go to [page]
2. Click [button]
3. Fill [form]
4. Submit [form]
5. See [error]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happens]

### Screenshots
[If applicable, add screenshots]

### Additional Context
[Any relevant code snippets, console errors, etc.]
```

## 💡 Feature Requests

### Requesting Features

1. **Search Existing Issues**: Check if feature already requested
2. **Use Template**: Follow bug report format for consistency
3. **Provide Context**: Explain use case and benefits
4. **Consider Implementation**: Think about technical feasibility

### Feature Request Template

```markdown
## Feature Request
**Brief description of the feature**

### Problem Statement
[What problem does this solve?]

### Proposed Solution
[How should this work?]

### Use Cases
[Specific scenarios where this would be useful]

### Implementation Ideas
[Technical considerations or implementation approach]

### Alternatives Considered
[Other approaches and why they weren't chosen]
```

## 📝 Pull Request Guidelines

### Before Submitting

1. **Tests Pass**: All tests must pass
2. **Code Style**: Follow ESLint rules
3. **Documentation**: Update relevant docs
4. **Type Safety**: No TypeScript errors
5. **Performance**: No performance regressions

### PR Template

```markdown
## Description
[Brief description of changes]

### Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

### Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

### Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests
2. **Code Review**: At least one maintainer review
3. **Merge**: Squash and merge to main branch

## 🔧 Development Tools

### Recommended VS Code Extensions

```json
{
  "recommendations": [
    "ms-vscode.vscode-typescript-next",
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "bradlc.vscode-tailwindcss",
    "ms-vscode.vscode-json"
  ]
}
```

### Useful Commands

```bash
# Development
npm run dev              # Start development server
npm run build            # Build for production
npm run preview           # Preview production build

# Code Quality
npm run lint              # Run ESLint
npm run lint:fix          # Auto-fix linting issues
npm run type-check        # Run TypeScript check

# Testing
npm run test              # Run unit tests
npm run test:watch        # Run tests in watch mode
npm run test:coverage     # Run tests with coverage
npm run test:e2e           # Run E2E tests
```

## 🎯 Areas of Contribution

### High Priority Areas

1. **Authentication & Security**
   - JWT token management
   - Protected routes
   - Security best practices

2. **Core Features**
   - Document upload and management
   - RAG chat functionality
   - Workspace management

3. **User Experience**
   - Responsive design improvements
   - Accessibility enhancements
   - Performance optimizations

4. **Developer Experience**
   - Testing infrastructure
   - Documentation improvements
   - Development tooling

### Getting Help

- **Discord**: Join our community discussions
- **GitHub Issues**: Ask questions or report issues
- **Email**: Contact maintainers at dev@example.com
- **Documentation**: Check existing docs first

## 📄 Code of Conduct

### Our Pledge

- **Be Respectful**: Value different perspectives and experiences
- **Be Inclusive**: Welcome newcomers and diverse contributions
- **Be Collaborative**: Work together and help each other learn
- **Be Constructive**: Focus on what's best for the project
- **Be Professional**: Maintain a positive and productive environment

### Enforcement

- **Warning**: For first violations
- **Temporary Suspension**: For repeated violations
- **Permanent Ban**: For severe violations

---

Thank you for contributing to RAG Knowledge Assistant! Your contributions help make this project better for everyone. 🚀
