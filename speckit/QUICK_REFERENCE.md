# Speckit Quick Reference Guide
## Developer Checklist & Best Practices

### ✅ Before You Start Coding

- [ ] Branch name follows convention: `feature/`, `bugfix/`, `hotfix/`
- [ ] Issue created and linked
- [ ] Feature discussed with team if architecture impact
- [ ] You've read relevant CONSTITUTION sections

### ✅ During Development

#### Code Quality
- [ ] No warnings from linter
- [ ] Meaningful variable/function names
- [ ] Functions < 50 lines
- [ ] Following SOLID principles
- [ ] DRY - no code duplication

#### Testing
- [ ] Unit tests written for new code
- [ ] Tests passing locally
- [ ] Test names describe what they test
- [ ] Coverage > 80% for modules

#### Documentation
- [ ] Docstrings on public methods
- [ ] Complex logic has explanatory comments
- [ ] Code is self-documenting where possible
- [ ] README updated if needed

### ✅ Before Committing

```bash
# Run these checks locally
npm run lint          # or 'black . && flake8 .'
npm run test          # or 'pytest'
npm run test:coverage # or 'pytest --cov'
npm run build         # Ensure builds successfully
```

- [ ] All checks passing
- [ ] No debug code or console.logs
- [ ] No commented-out code
- [ ] Commit message is clear and descriptive
- [ ] References issue: "Fixes #123"

### ✅ Pull Request Checklist

**Before Opening PR:**
- [ ] Code is complete and tested
- [ ] conflicts resolved
- [ ] Rebased on main/develop
- [ ] Force push if needed (interactive rebase)

**PR Description Should Include:**
- [ ] Clear description of changes
- [ ] Why this change was needed
- [ ] How to test the changes
- [ ] Linked issue(s)
- [ ] Screenshots (if UI changes)
- [ ] Performance impact (if applicable)
- [ ] Breaking changes (if any)

### ✅ Code Review Guidelines

**When Reviewing:**
- [ ] Code is readable and maintainable
- [ ] Tests are adequate (coverage > 80%)
- [ ] No security vulnerabilities
- [ ] Performance acceptable
- [ ] Follows Speckit standards
- [ ] Documentation complete

**Review Comments:**
- ✓ Be constructive and respectful
- ✓ Explain why, not just "wrong"
- ✓ Approve with confidence or request changes
- ✓ Approve within 24 hours

### ✅ Performance Checklist

**Frontend:**
- [ ] Bundle size added < 50KB
- [ ] Images optimized
- [ ] No render-blocking resources
- [ ] Code splitting applied to large features
- [ ] Lighthouse score > 80

**Backend:**
- [ ] API responds in < 500ms (p95)
- [ ] Database queries optimized (< 100ms)
- [ ] Caching strategy implemented
- [ ] Load tested with 2x peak load
- [ ] Monitoring in place

### ✅ Security Checklist

- [ ] Input validation on all user inputs
- [ ] No secrets in code
- [ ] No SQL injection vulnerabilities
- [ ] CORS configured correctly
- [ ] Authentication required for protected endpoints
- [ ] Rate limiting implemented
- [ ] Error messages don't leak information

### ✅ Testing Pyramid

```
        /\
       /  \  E2E Tests (10%)
      /----\
     /      \  Integration Tests (30%)
    /--------\
   /          \ Unit Tests (60%)
  /____________\
```

**Unit Test Example:**
```python
def test_calculate_total_with_discount():
    # Arrange
    items = [10, 20, 30]
    discount = 0.1
    
    # Act
    result = calculate_total(items, discount)
    
    # Assert
    assert result == 54.0  # (10+20+30) * 0.9
```

### ✅ Common Mistakes to Avoid

❌ **Don't:**
- Commit without tests
- Write functions > 100 lines
- Skip code reviews
- Ignore linting warnings
- Commit debug code
- Store secrets in code
- Skip documentation
- Make massive PRs (> 400 lines)

✓ **Do:**
- Test first (TDD where possible)
- Write self-documenting code
- Participate in reviews
- Fix linting issues
- Clean up before commit
- Use environment variables
- Update documentation
- Make focused, reviewable PRs

### ✅ Performance Optimization Process

1. **Measure** - Establish baseline metrics
2. **Profile** - Identify bottlenecks
3. **Optimize** - Focus on top 20% of issues
4. **Verify** - Confirm improvement
5. **Monitor** - Track regression

### ✅ Troubleshooting Common Issues

**Slow Build?**
- Check for unnecessary dependencies
- Use code splitting
- Enable parallel test execution

**High Memory Usage?**
- Check for memory leaks
- Implement proper cleanup
- Review collection sizes

**Unreliable Tests?**
- Remove timing dependencies
- Use proper test isolation
- Mock external services

**Security Vulnerabilities?**
- Update dependencies: `npm audit fix`
- Scan code: `snyk test`
- Review: OWASP Top 10

### ✅ Daily Developer Habits

**Morning:**
- [ ] Update branch from main
- [ ] Check failed tests/builds
- [ ] Review feedback on PRs

**Throughout Day:**
- [ ] Run tests after significant changes
- [ ] Ask questions if unsure
- [ ] Review peer code
- [ ] Update documentation

**End of Day:**
- [ ] Commit working code
- [ ] Push to branch
- [ ] Update task status
- [ ] Note blockers

---

## Quick Reference: Response Times

| Operation | Target | Acceptable |
|-----------|--------|-----------|
| Page Load (FCP) | < 2.5s | < 4s |
| API Call | < 500ms | < 1s |
| Database Query | < 100ms | < 500ms |
| UI Interaction | < 100ms | < 300ms |

---

## Quick Reference: Coverage Requirements

| Code Type | Minimum Coverage | Target Coverage |
|-----------|------------------|-----------------|
| Utility Functions | 80% | 95% |
| Business Logic | 80% | 90% |
| Controllers/Views | 60% | 80% |
| Security Code | 100% | 100% |

---

## Terminal Commands Cheatsheet

### Code Quality
```bash
# Python
black .                    # Format code
flake8 .                   # Lint
isort .                    # Organize imports

# JavaScript/TypeScript
npm run lint               # ESLint
npm run format             # Prettier
npm run type-check         # TypeScript
```

### Testing
```bash
# Python
pytest                     # Run tests
pytest --cov              # With coverage
pytest -v -s              # Verbose with prints

# JavaScript
npm test                   # Run tests
npm run test:watch        # Watch mode
npm run test:coverage     # With coverage
```

### Performance
```bash
# Build analysis
npm run build:analyze      # Bundle size

# Load testing
k6 run load-test.js       # k6 load test
```

### Git Workflow
```bash
# Feature branch
git checkout -b feature/my-feature
git push -u origin feature/my-feature

# Before PR
git fetch origin
git rebase origin/main
git push -f origin feature/my-feature

# After merge
git checkout main
git pull
git branch -d feature/my-feature
```

---

**Last Updated**: 2026-05-06  
**Version**: 1.0  
*Bookmark this page for quick reference!*

