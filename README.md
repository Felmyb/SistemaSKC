# SmartKitchen Connect

**Version:** 1.0.0  
**Standard:** IEEE 830 (Software Requirements Specification)  
**Methodology:** Design Thinking  
**Framework:** Django REST Framework  

## 📋 Overview

SmartKitchen Connect is an integral restaurant management system designed to optimize operational processes and enhance the experience for customers and employees. The system automates communication between kitchen, inventory, waitstaff, and administration, providing real-time information about orders, dish availability, preparation times, and overall performance.

## 🎯 Project Purpose

- **Empathize:** Understand pain points of customers, cooks, and inventory managers
- **Define:** Identify real problems (inefficiency, lack of coordination, visibility gaps)
- **Ideate:** Propose creative, technological, and human-centered solutions
- **Prototype:** Build iterative functional modules with Django and REST API
- **Evaluate:** Validate with real users, measuring satisfaction and performance

## 👥 Key Users and Roles

| Role | Responsibilities |
|------|-----------------|
| **Customer** | Place orders, view availability and estimated times, receive notifications |
| **Cook** | View orders by priority, update dish status |
| **Inventory Manager** | Control supplies, detect shortages, generate purchase orders |
| **Administrator** | Manage users, reports, dishes, and strategic decisions |
| **Waiter/Cashier** | Manage orders from digital menu and communicate with kitchen |

## 📦 Project Structure

```
SmartKitchenConnect/
├── Backend/                    # Django REST Framework backend
│   ├── apps/                   # Django applications (modular)
│   ├── config/                 # Configuration and settings
│   ├── core/                   # Core utilities and base classes
│   └── tests/                  # Unit and integration tests
├── Frontend/                   # React application (future)
├── IAC/                        # Infrastructure as Code
│   ├── docker/                 # Docker configurations
│   ├── kubernetes/             # K8s manifests (if applicable)
│   └── terraform/              # Cloud infrastructure
├── Docs/                       # Technical documentation
│   ├── requirements/           # IEEE 830 specifications
│   ├── design-thinking/        # DT artifacts
│   └── api/                    # OpenAPI/Swagger docs
└── Scripts/                    # Automation and utility scripts
```

## 🔧 Technical Architecture

- **Backend:** Django REST Framework
- **Database:** PostgreSQL
- **AI & Analytics:** Scikit-learn / TensorFlow
- **Frontend:** React (future development)
- **Infrastructure:** Docker, Nginx, Azure Pipelines
- **Documentation:** OpenAPI (Swagger) + Azure Wiki

## 📋 Functional Requirements (RF)

| ID | Description | Priority | Traceability |
|----|-------------|----------|--------------|
| RF-01 | Digital order panel with visual priority (colors, times, status) | High | `orders` app |
| RF-02 | Automatic inventory update when registering an order | High | `inventory` app |
| RF-03 | Demand and ingredient prediction with AI (weather, day, history) | Medium | `analytics` app |
| RF-04 | Order tracking for customer with estimated time and notifications | High | `orders` + `notifications` apps |
| RF-05 | Differentiated roles and permissions by user type | High | `users` app |
| RF-06 | Performance, efficiency, and sales reports in admin dashboard | Medium | `reports` app |

## 🔒 Non-Functional Requirements (RNF)

| ID | Description | Type |
|----|-------------|------|
| RNF-01 | Response time < 2 seconds average per endpoint | Performance |
| RNF-02 | PEP8 compliance and docstring documentation | Quality |
| RNF-03 | Security with JWT and HTTPS (SSL) | Security |
| RNF-04 | Traceability through OpenAPI documentation | Traceability |
| RNF-05 | Docker deployment support and CI/CD in Azure DevOps | Portability |
| RNF-06 | Accessibility compliant with WCAG 2.1 standards | Usability |

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Docker & Docker Compose
- Node.js 18+ (for frontend)

### Installation

```bash
# Clone repository
git clone <repository-url>
cd SmartKitchenConnect

# Setup backend
cd Backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configurations

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Docker Setup

```bash
# Build and run containers
docker-compose up --build

# Access at http://localhost:8000
```

## 📚 Documentation

- **API Documentation:** `http://localhost:8000/api/docs/` (Swagger UI)
- **Requirements Specification:** See `Docs/requirements/SRS_IEEE830.md`
- **Design Thinking Process:** See `Docs/design-thinking/`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Minimum coverage: 80%
```

## 🔐 Security

- JWT authentication for API endpoints
- Environment variables for sensitive data
- HTTPS/SSL in production
- Role-based access control (RBAC)

## 📖 Development Guidelines

- Follow PEP8 style guide
- Include docstrings (Google or reStructuredText format)
- Link every component to a functional or non-functional requirement
- Write descriptive commit messages
- Feature branch workflow
- Code review before merging to main
- Maintain minimum 80% test coverage

## 🤝 Contributing

1. Create feature branch from `develop`
2. Follow coding standards
3. Write/update tests
4. Update documentation
5. Submit pull request
6. Pass CI/CD checks
7. Get code review approval

## 📄 License

[Specify your license here]

## 📞 Contact

[Project maintainer contact information]

---

**Last Updated:** October 17, 2025  
**Maintained by:** SmartKitchen Connect Team
