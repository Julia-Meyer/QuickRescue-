# Speckit Constitution
## Foundation Principles for Code Excellence

**Version:** 1.0  
**Last Updated:** 2026-05-06  
**Purpose:** Establish universal standards for code quality, testing, user experience, and performance

---

## 1. Code Quality Principles

### 1.1 Readability & Maintainability
- **Clean Code First**: Code is written for humans first, machines second
- **Meaningful Names**: Variables, functions, and classes must have clear, descriptive names
- **Single Responsibility**: Each function/class should have one reason to change
- **DRY Principle**: Don't Repeat Yourself - extract reusable components
- **Maximum Function Length**: Aim for functions under 50 lines
- **Documentation**: All public APIs must include docstrings with examples

### 1.2 Code Style & Consistency
- **Language-Specific Standards**:
  - Python: PEP 8 compliance with max line length of 100 characters
  - TypeScript/JavaScript: ESLint configuration with Prettier formatting
  - Java: Google Java Style Guide
- **Linting**: All projects must pass linting checks before merge
- **Formatting**: Automated formatting on save (Prettier, Black, etc.)
- **Import Organization**: Organize imports alphabetically and by category

### 1.3 Architecture & Design Patterns
- **SOLID Principles**:
  - Single Responsibility Principle
  - Open/Closed Principle
  - Liskov Substitution Principle
  - Interface Segregation Principle
  - Dependency Inversion Principle
- **Design Patterns**: Use established patterns (Factory, Observer, Strategy, etc.)
- **Modularity**: Code must be organized into logical, reusable modules
- **Dependency Management**: Minimize coupling, maximize cohesion

### 1.4 Code Review Standards
- **Peer Review Required**: All code changes require at least one approval
- **Review Checklist**:
  - ✓ Functionality correctness
  - ✓ Code readability and style compliance
  - ✓ Test coverage adequacy
  - ✓ No security vulnerabilities
  - ✓ Performance impact assessment
  - ✓ Documentation completeness
- **Comment Standards**: Only explain "why", not "what" (code shows what)
- **Review Turnaround**: 24-hour review SLA for critical changes

---

## 2. Testing Standards

### 2.1 Test Coverage Requirements
- **Minimum Coverage**: 80% code coverage for all modules
- **Critical Paths**: 100% coverage for security and business-critical code
- **Coverage Tools**: Use industry standard tools (pytest, Jest, JUnit, etc.)
- **Coverage Tracking**: Track coverage trends in CI/CD pipeline

### 2.2 Test Types & Responsibilities

#### Unit Tests
- **Target**: Individual functions/methods in isolation
- **Tools**: pytest (Python), Jest (JS), JUnit (Java)
- **Standard**: Write tests alongside code development
- **Requirement**: Each public method must have associated unit tests

#### Integration Tests
- **Target**: Component interactions and data flow
- **Scope**: Database interactions, API calls, service integrations
- **Frequency**: Run on every commit
- **Mock External Services**: Use mocks for unreliable external dependencies

#### End-to-End Tests
- **Target**: Complete user workflows
- **Frequency**: Daily or on-demand
- **Tools**: Selenium, Cypress, Playwright
- **Coverage**: Critical user paths and happy paths

#### Performance Tests
- **Target**: Response times, memory usage, scalability
- **Baseline**: Establish and maintain performance baselines
- **Regression Detection**: Fail on 10%+ performance degradation
- **Load Testing**: Test under expected peak loads

### 2.3 Test Quality Standards
- **Deterministic Tests**: No flaky tests - must pass/fail consistently
- **Isolation**: Tests must not depend on execution order
- **Clarity**: Test names must describe what is being tested
- **Assertion Density**: At least one meaningful assertion per test
- **Setup & Teardown**: Clear before/after states
- **Test Data**: Use realistic, representative data
- **Naming Convention**: `test_[functionality]_[scenario]_[expected_result]`

### 2.4 Test Execution
- **Pre-commit**: Run unit tests before each commit
- **CI/CD Pipeline**: Run full test suite on pull requests
- **Parallel Execution**: Run tests in parallel when possible
- **Fast Feedback**: Unit tests must complete within 5 minutes

---

## 3. User Experience Consistency Principles

### 3.1 Design System Compliance
- **Design Language**: All UI components must follow the established design system
- **Component Library**: Use centralized, well-documented component library
- **Style Consistency**: Unified color palette, typography, spacing, animations
- **Accessibility**: WCAG 2.1 AA compliance minimum
- **Responsive Design**: Mobile-first approach, support for all breakpoints

### 3.2 User Interface Standards
- **Navigation**: Intuitive, predictable navigation patterns
- **Feedback**: Always provide user feedback for actions (loading, success, error)
- **Error Handling**:
  - ✓ Clear, actionable error messages
  - ✓ No technical jargon in user-facing messages
  - ✓ Suggest corrective actions
  - ✓ Log technical details for debugging
- **Consistency**: Same actions produce same UI/UX across all screens
- **Loading States**: Never show blank screens; use loaders/skeletons

### 3.3 Interaction Patterns
- **Default Actions**: Clear primary action on each screen
- **Form Validation**: Real-time validation with immediate feedback
- **Confirmation**: Require confirmation for destructive actions
- **Undo/Redo**: Support undo where practical
- **Keyboard Navigation**: Full keyboard support for accessibility
- **Touch-Friendly**: Minimum 44x44px touch targets for mobile

### 3.4 Performance Perception
- **Perceived Performance**: Optimize perception (99ms response feels instant)
- **Loading Indicators**: Show progress for operations >1 second
- **Empty States**: Meaningful, not frustrating empty state messages
- **Animations**: Smooth, purposeful animations (not just eye candy)
- **Network Awareness**: Graceful degradation for slow connections

### 3.5 Localization & Internationalization
- **Multi-language Support**: Extract all strings to translation files
- **Date/Time Formats**: Respect user locale settings
- **Currency Handling**: Display correct currency symbols and conventions
- **Text Expansion**: Account for text length variations (German ~35% longer)
- **RTL Support**: Consider right-to-left language support

---

## 4. Performance Requirements

### 4.1 Performance Targets
| Metric | Target | Critical |
|--------|--------|----------|
| Page Load Time (First Contentful Paint) | < 2.5s | < 4s |
| Time to Interactive | < 3.8s | < 7s |
| Largest Contentful Paint | < 2.5s | < 4s |
| Cumulative Layout Shift | < 0.1 | < 0.25 |
| First Input Delay | < 100ms | < 300ms |
| API Response Time (p95) | < 500ms | < 1000ms |
| Database Query | < 100ms (p95) | < 500ms |

### 4.2 Frontend Performance
- **Bundle Size**: Keep main bundle < 200KB (gzipped)
- **Code Splitting**: Lazy load non-critical code
- **Image Optimization**: Use modern formats (WebP), responsive images
- **CSS/JS**: Minimize render-blocking resources
- **Caching Strategy**:
  - ✓ Cache busting for updates
  - ✓ Service worker for offline support
  - ✓ Browser cache for static assets (1 year)
- **Monitoring**: Track Core Web Vitals continuously

### 4.3 Backend Performance
- **API Response Time**: 95th percentile under 500ms
- **Database Optimization**:
  - ✓ Index frequently queried columns
  - ✓ Query optimization for large datasets
  - ✓ Connection pooling configuration
  - ✓ Regular query analysis and optimization
- **Caching Strategy**:
  - ✓ Redis for session/hot data (5-minute TTL default)
  - ✓ Application-level caching for expensive operations
  - ✓ Cache invalidation strategy for data consistency
- **Concurrency**: Handle minimum 1000 concurrent users
- **Resource Limits**: Set memory/CPU limits per service

### 4.4 Database Performance
- **Query Performance**: All queries must complete in < 100ms (p95)
- **Indexing Strategy**: Essential indexes must be in place before optimization
- **Query Analysis**: Use EXPLAIN PLAN for all queries
- **Connection Management**: Pool size 10-20 connections per application
- **Backup/Recovery**: RPO (Recovery Point Objective) < 1 hour
- **Monitoring**: Track slow queries, disk space, connection count

### 4.5 Scalability & Load Testing
- **Load Testing**: Test with 2x expected peak load
- **Stress Testing**: Identify breaking point and graceful degradation
- **Capacity Planning**: Plan for 3-6 month growth
- **Horizontal Scaling**: Ensure core services are horizontally scalable
- **Database Sharding**: Plan sharding strategy for large datasets

### 4.6 Performance Monitoring
- **Continuous Monitoring**: APM (Application Performance Monitoring) in production
- **Alerting**: Alert on performance degradation > 10%
- **Metrics to Track**:
  - ✓ Response time (p50, p95, p99)
  - ✓ Throughput (requests/second)
  - ✓ Error rate
  - ✓ Resource utilization (CPU, memory)
  - ✓ Cache hit rate
- **Reporting**: Weekly performance reports
- **Optimization**: Continuous optimization cycle based on metrics

---

## 5. Security & Reliability

### 5.1 Security Standards
- **Input Validation**: All user input must be validated
- **Authentication**: OAuth 2.0 / OpenID Connect for user auth
- **Authorization**: Role-based access control (RBAC) implementation
- **Encryption**: TLS 1.3 for all data in transit
- **Data Protection**: Encrypt sensitive data at rest
- **Secrets Management**: Never commit secrets; use environment variables
- **Dependency Scanning**: Weekly CVE scanning for all dependencies
- **Security Testing**: Monthly penetration testing for critical systems

### 5.2 Reliability Standards
- **Uptime SLA**: 99.9% uptime target (43 minutes downtime/month)
- **Monitoring**: 24/7 system monitoring with alerting
- **Incident Response**: < 15 minutes response time for critical issues
- **Graceful Degradation**: Services degrade gracefully under load
- **Circuit Breakers**: Implement circuit breakers for external dependencies
- **Retry Logic**: Implement exponential backoff with jitter

---

## 6. Documentation Standards

### 6.1 Code Documentation
- **Docstrings**: Required for all public methods
- **README**: Every project must have a comprehensive README
- **API Documentation**: Auto-generated (Swagger/OpenAPI)
- **Architecture Diagrams**: Included for complex systems
- **Setup Guide**: Clear local development setup instructions
- **Troubleshooting**: Common issues and solutions documented

### 6.2 Documentation Quality
- **Up-to-date**: Documentation must stay current with code
- **Examples**: Include working code examples
- **Visual Aids**: Screenshots/diagrams for UI documentation
- **Version Control**: Document version requirements and changes
- **Comments**: Explain "why" not "what"; code shows what

---

## 7. Continuous Integration & Deployment

### 7.1 CI/CD Pipeline Requirements
- **Automated Testing**: All tests run automatically on commit
- **Code Quality Checks**: Linting and static analysis on every PR
- **Build Artifacts**: Automatic build on every commit
- **Deployment Automation**: No manual deployment steps
- **Rollback Capability**: Always have immediate rollback available
- **Deployment Windows**: Clear maintenance windows communicated

### 7.2 Release Process
- **Versioning**: Semantic versioning (Major.Minor.Patch)
- **Changelog**: Detailed changelog for each release
- **Release Notes**: User-friendly release notes
- **Staged Rollout**: 
  - ✓ Canary deployment (5% of users)
  - ✓ Gradual rollout (25%, 50%, 100%)
  - ✓ Monitor metrics at each stage
- **Rollback Plan**: Tested, documented rollback procedure

---

## 8. Team Practices

### 8.1 Development Workflow
- **Branch Strategy**: Git Flow with main, develop, feature branches
- **Commit Messages**: Clear, descriptive commit messages
- **Pull Requests**: Require PR for all code changes
- **Issue Tracking**: Link all PRs to issues
- **Meeting Efficiency**: Timeboxed standups and meetings

### 8.2 Communication
- **Code Comments**: Explain business logic and edge cases
- **Commit Messages**: Include issue references and context
- **Pull Request Descriptions**: Clear summary of changes
- **Status Updates**: Proactive communication of blockers
- **Knowledge Sharing**: Document architectural decisions (ADR)

### 8.3 Continuous Learning
- **Code Reviews**: Learn from peer feedback
- **Tech Debt Management**: Allocate 20% of sprint for tech debt
- **Performance Analysis**: Regular performance review sessions
- **Professional Development**: Budget for training and conferences
- **Best Practices**: Share industry trends and new practices

---

## 9. Compliance & Validation

### 9.1 Linting & Static Analysis
- [ ] Code must pass all linting checks
- [ ] No code smells or duplicate code
- [ ] Cyclomatic complexity < 10 per function
- [ ] No unused variables or imports
- [ ] Type safety checks (where applicable)

### 9.2 Testing Validation
- [ ] Coverage > 80% minimum
- [ ] All tests pass before merge
- [ ] No flaky tests
- [ ] Load test results within targets

### 9.3 Performance Validation
- [ ] Core Web Vitals within targets
- [ ] API response times acceptable
- [ ] Database queries optimized
- [ ] Bundle size within limits

---

## 10. Enforcement & Metrics

### 10.1 Automated Enforcement
- **Pre-commit Hooks**: Prevent commits violating standards
- **CI/CD Gates**: Block merges failing checks
- **Code Review Rules**: Enforce via branch protection
- **Performance Budgets**: Fail builds exceeding limits

### 10.2 Success Metrics
- **Code Quality**: Sonarqube score > 80
- **Test Coverage**: Minimum 80% code coverage
- **Performance**: 99th percentile under targets
- **Security**: Zero critical vulnerabilities
- **Deployment Frequency**: Daily deployments capability
- **Lead Time**: < 24 hours from commit to production
- **Change Failure Rate**: < 5%
- **MTTR**: < 1 hour mean time to recovery

### 10.3 Regular Review
- **Quarterly Review**: Update standards based on learnings
- **Retrospectives**: Monthly team retrospectives
- **Metrics Dashboard**: Visible to all team members
- **Improvement Plans**: Track actual vs. target metrics

---

## 11. Acknowledgment

All team members developing under the Speckit framework commit to upholding these principles:

- ✓ I understand and commit to these standards
- ✓ I will code for quality, testability, and performance
- ✓ I participate in code reviews constructively
- ✓ I continuously work to improve our practices
- ✓ I raise concerns when standards are compromised

**Effective Date**: 2026-05-06  
**Review Date**: 2026-08-06

---

*"Excellence is not a skill, it's a habit." - Speckit Team*

