# Contributing to AI Cache Proxy

Thank you for your interest in contributing to AI Cache Proxy! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the issue template** and provide detailed information
3. **Include steps to reproduce** the problem
4. **Add relevant logs** and error messages
5. **Specify your environment** (OS, Docker version, etc.)

### Feature Requests

When requesting features:

1. **Describe the use case** clearly
2. **Explain the expected behavior**
3. **Consider the impact** on existing functionality
4. **Provide examples** if possible

## 🛠️ Development Setup

### Prerequisites

- Docker & Docker Compose
- Go 1.21+ (for local development)
- Python 3.8+ (for local development)
- Git

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-cache-proxy.git
cd ai-cache-proxy

# Setup development environment
cd project
make setup

# Start services
make up-build

# Check status
make status
```

### Local Development

```bash
# Start services in development mode
make dev

# Run tests
make test

# Check logs
make logs

# Access services
# Dashboard: http://localhost:8080/dashboard
# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## 📝 Code Style Guidelines

### Go Code

- Follow [Effective Go](https://golang.org/doc/effective_go.html)
- Use `gofmt` for formatting
- Run `golint` and `gosec` for code quality
- Write tests for new functionality

### Python Code

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints where appropriate
- Write docstrings for functions and classes
- Use `black` for code formatting

### General Guidelines

- **Write clear commit messages** using conventional commits
- **Add tests** for new features
- **Update documentation** when adding features
- **Keep functions small** and focused
- **Use meaningful variable names**

## 🔧 Development Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/ai-cache-proxy.git
cd ai-cache-proxy

# Add upstream remote
git remote add upstream https://github.com/original-owner/ai-cache-proxy.git
```

### 2. Create a Feature Branch

```bash
# Create and switch to a new branch
git checkout -b feature/amazing-feature

# Or for bug fixes
git checkout -b fix/bug-description
```

### 3. Make Changes

- Write your code following the style guidelines
- Add tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Run all tests
make test

# Test specific components
make test-proxy

# Run security scans
make security-scan

# Check performance
make benchmark
```

### 5. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new analytics endpoint

- Add /analytics/export endpoint
- Implement data export functionality
- Add tests for new endpoint
- Update documentation"
```

### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/amazing-feature

# Create a Pull Request on GitHub
```

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] **Tests pass** locally
- [ ] **Code is formatted** correctly
- [ ] **Documentation is updated**
- [ ] **No sensitive data** is included
- [ ] **Commit messages** are clear and descriptive

### PR Description Template

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Screenshots (if applicable)
Add screenshots for UI changes
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
make test

# Run Go tests only
cd go-proxy && go test ./...

# Run Python tests only
cd llama-service && python -m pytest tests/ -v

# Run with coverage
cd go-proxy && go test -cover ./...
cd llama-service && python -m pytest --cov=. tests/
```

### Writing Tests

- **Test new functionality** thoroughly
- **Use descriptive test names**
- **Test edge cases** and error conditions
- **Mock external dependencies**
- **Keep tests fast** and reliable

## 📚 Documentation

### Updating Documentation

- **Update README.md** for new features
- **Add API documentation** for new endpoints
- **Include examples** and usage patterns
- **Update configuration** documentation

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add diagrams for complex concepts
- Keep documentation up-to-date

## 🔒 Security

### Security Guidelines

- **Never commit secrets** or sensitive data
- **Use environment variables** for configuration
- **Validate all inputs** thoroughly
- **Follow security best practices**
- **Report security issues** privately

### Reporting Security Issues

For security issues, please email security@yourdomain.com instead of creating a public issue.

## 🏷️ Release Process

### Versioning

We use [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for new functionality
- **PATCH** version for bug fixes

### Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] Version is bumped
- [ ] Release notes are written
- [ ] Docker images are built and tested

## 🤝 Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive
- **Help others** learn and grow
- **Provide constructive feedback**
- **Follow the project's code of conduct**

### Communication

- **Use clear language** in issues and PRs
- **Be patient** with maintainers
- **Ask questions** when needed
- **Share knowledge** with the community

## 📞 Getting Help

### Resources

- **Documentation**: Check the README and wiki
- **Issues**: Search existing issues for solutions
- **Discussions**: Use GitHub Discussions for questions
- **Chat**: Join our community chat (if available)

### Contact

- **Issues**: GitHub Issues
- **Security**: security@yourdomain.com
- **General**: discussions tab

## 🙏 Acknowledgments

Thank you for contributing to AI Cache Proxy! Your contributions help make this project better for everyone.

---

**Happy coding! 🚀**
