# SmartKitchen Connect - Constitution

## Project Principles

This document establishes the guiding principles for SmartKitchen Connect development, aligned with IEEE 830 standards and Design Thinking methodology.

## 1. Code Quality Standards

### Django Best Practices
- Follow Django's "batteries included" philosophy
- Maintain clear separation of concerns (Models, Views, Serializers, Permissions)
- Use Django REST Framework conventions for API design
- Document all models, views, and serializers with docstrings
- Link all code to functional requirements (RF-XX) and non-functional requirements (RNF-XX)

### Code Structure
- **Apps**: Each Django app represents a bounded context (usuarios, pedidos, platos, inventario)
- **Models**: Use descriptive field names, include help_text, maintain referential integrity
- **Serializers**: Separate read/write serializers when needed, validate at serializer level
- **Views**: Use ViewSets with clear action methods, document each endpoint with swagger_auto_schema
- **Permissions**: Create custom permission classes for fine-grained access control

### Python Standards
- Follow PEP 8 style guide
- Use type hints where appropriate
- Maximum line length: 120 characters
- Use meaningful variable and function names in English
- Comments and docstrings in Spanish for business logic clarity

## 2. Testing Standards

### Coverage Requirements
- Minimum 80% code coverage (enforced in CI/CD)
- Target 100% coverage for critical business logic
- All new features must include tests

### Test Structure
- **Unit tests**: Test individual functions and methods in isolation
- **Endpoint tests**: Test API endpoints with various scenarios (success, validation errors, permissions)
- **Integration tests**: Test interactions between apps (deferred per project plan)

### Test Organization
- Tests in `tests.py`, `test_*.py` files within each app
- Use pytest fixtures for test data
- Mock external dependencies
- Test both happy paths and error cases

### Test Naming Convention
```python
def test_<feature>_<scenario>_<expected_result>():
    # Example: test_order_creation_with_valid_data_returns_201()
    pass
```

## 3. API Design Standards

### RESTful Principles
- Use standard HTTP methods: GET, POST, PUT, PATCH, DELETE
- Return appropriate status codes (200, 201, 400, 401, 403, 404, 500)
- Use nested routes sparingly, prefer flat URL structure
- Version API with `/api/v1/` prefix

### Request/Response Format
- Accept and return JSON
- Use snake_case for field names
- Include pagination for list endpoints
- Provide clear error messages with field-level validation errors

### Authentication & Authorization
- JWT token-based authentication (access + refresh tokens)
- Role-based access control (CUSTOMER, STAFF, ADMIN, COOK, etc.)
- Implement permission classes at ViewSet level
- Always validate user permissions before sensitive operations

### Documentation
- Use drf-yasg for OpenAPI/Swagger documentation
- Document all parameters, request bodies, and responses
- Include examples in Swagger annotations
- Link endpoints to functional requirements

## 4. Performance Requirements (RNF-01)

### Response Time Targets
- API endpoints: < 500ms for 95th percentile
- Complex queries: Use select_related() and prefetch_related()
- Database indexing on foreign keys and frequently queried fields

### Optimization Strategies
- Lazy loading for large datasets
- Pagination for list endpoints (default: 20 items)
- Caching for static data (categories, menu items)
- Database query optimization with Django Debug Toolbar in development

## 5. Security Standards (RNF-03)

### Authentication Security
- Passwords hashed with Django's default PBKDF2 algorithm
- JWT tokens with expiration (access: 1 hour, refresh: 7 days)
- HTTPS only in production
- CORS properly configured

### Input Validation
- Validate all user inputs at serializer level
- Sanitize HTML/SQL inputs to prevent injection attacks
- Rate limiting on authentication endpoints
- CSRF protection for non-API views

### Data Privacy
- Never log sensitive data (passwords, tokens)
- Implement proper permission checks for data access
- Audit trail for critical operations (RNF-04)

## 6. Scalability Standards (RNF-02)

### Database Design
- Proper indexing strategy
- Avoid N+1 queries with prefetch_related()
- Use database-level constraints
- Regular data archival strategy for historical data

### Application Architecture
- Stateless API design for horizontal scaling
- Background tasks for heavy operations (future: Celery)
- Media files served through CDN (future enhancement)

## 7. User Experience Standards

### Accessibility (RNF-06)
- Clear, descriptive error messages
- Field-level validation feedback
- Consistent response format across all endpoints
- Allergen information clearly documented

### Internationalization
- Support for Spanish language in business logic
- English for technical documentation
- Prepare for multi-language support (future)

## 8. Traceability & Auditing (RNF-04)

### Requirements Traceability
- Every model, view, and test linked to RF/RNF in docstrings
- IEEE 830 compliance maintained
- Design Thinking principles documented

### Audit Trail
- Timestamp fields (created_at, updated_at) on all models
- User tracking for sensitive operations
- Transaction logs for inventory changes
- Order status change history

## 9. Development Workflow

### Version Control
- Git with clear commit messages in Spanish
- Branch strategy: main (production), develop (integration), feature/* (new work)
- Pull requests required for main branch
- Commits linked to requirements when applicable

### CI/CD Pipeline
- Automated tests on every push
- Code coverage reporting
- OpenAPI spec generation and validation
- Spectral linting for API documentation quality
- Deployment blocked if tests fail or coverage < 80%

### Code Review Standards
- At least one approval required for main branch
- Check for requirements traceability
- Verify test coverage
- Validate API documentation

## 10. Documentation Standards

### Code Documentation
- Docstrings for all classes and public methods
- Inline comments for complex business logic
- README files in each app directory
- Architecture documentation in Docs/

### API Documentation
- OpenAPI/Swagger spec auto-generated from code
- Manual examples for complex endpoints
- Postman collection maintained (future)
- API changelog for breaking changes

### Project Documentation
- IEEE 830 requirements specification
- Design Thinking artifacts in Docs/design-thinking/
- Technical architecture diagrams
- Deployment and setup guides

## 11. Continuous Improvement

### Metrics to Track
- Test coverage percentage
- API response times
- Error rates by endpoint
- Code quality scores (future: SonarQube)

### Regular Reviews
- Weekly code quality checks
- Monthly architecture review
- Quarterly requirements validation
- Continuous feedback from stakeholders

## 12. Technology Stack

### Backend
- **Framework**: Django 4.2+ with Django REST Framework
- **Database**: SQLite (development), PostgreSQL (production target)
- **Authentication**: JWT via djangorestframework-simplejwt
- **Documentation**: drf-yasg for OpenAPI/Swagger
- **Testing**: pytest with pytest-django and pytest-cov
- **Linting**: Spectral for OpenAPI validation

### DevOps
- **Version Control**: Git (Azure DevOps + GitHub mirrors)
- **CI/CD**: Azure Pipelines
- **Spec Management**: GitHub Spec Kit + Spectral
- **Code Quality**: pytest-cov for coverage tracking

### Future Considerations
- Celery for background tasks
- Redis for caching
- Docker for containerization
- Kubernetes for orchestration

---

**Last Updated**: October 25, 2025  
**Standard**: IEEE 830  
**Methodology**: Design Thinking + Spec-Driven Development
