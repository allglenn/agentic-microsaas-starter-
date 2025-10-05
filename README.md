# 🚀 Agentic MicroSaaS Starter

A comprehensive, production-ready microsaas starter with AI agents, full-stack features, and modern architecture.

## 🎯 **Quick Start**

```bash
# Clone and setup
git clone <your-repo>
cd agentic-microsaas-starter-full-personalized

# Start infrastructure
make dev.up

# Install dependencies
make install

# Run services
make dev
```

## 🏗️ **Architecture Overview**

```
┌─────────────────┐         ┌─────────────────┐
│   Web Service   │         │   API Service  │
│   (Next.js)     │◄────────┤   (FastAPI)    │
│   • Frontend    │         │   • Business   │
│   • Auth        │         │   • API        │
│   • Dashboard   │         │   • Database   │
└─────────────────┘         └─────────────────┘
         │                           │
         └───────────────────────────┼───────────────────────────┐
                                     │                           │
                            ┌─────────────────┐         ┌─────────────────┐
                            │ Agent Service   │         │   Database      │
                            │ (Celery)        │         │   (PostgreSQL)  │
                            │ • AI Processing │         │   • Models      │
                            │ • Task Queue    │         │   • Migrations  │
                            └─────────────────┘         └─────────────────┘
```

## ✨ **Key Features**

### 🤖 **AI-Powered**
- **Multiple Agent Types**: Customer Support, Data Analysis, Content Generation
- **Flexible Architecture**: Simple and Enhanced agent systems
- **OpenAI Integration**: GPT-3.5, GPT-4 with centralized configuration
- **Task Management**: Async processing with Celery

### 💳 **SaaS Features**
- **Payment & Billing**: Stripe integration with subscriptions
- **Email Notifications**: SendGrid with templates and preferences
- **User Management**: Teams, RBAC, invitations
- **File Storage**: GCP Cloud Storage with sharing
- **Social Auth**: Google, GitHub, Microsoft, Apple

### 🏗️ **Modern Architecture**
- **Shared Models**: Centralized database models
- **Shared Modules**: Configuration, Auth, Logging, Monitoring
- **Microservices**: API, Agent, Web services
- **Production Ready**: Structured logging, monitoring, health checks

## 📚 **Documentation**

> **📚 [Complete Documentation](docs/README.md)** - All project documentation organized in one place  
> **📋 [Shared Models Architecture](docs/SHARED_MODELS_ARCHITECTURE.md)** - Complete guide to the shared models system  
> **🏗️ [Shared Modules Architecture](docs/SHARED_MODULES_ARCHITECTURE.md)** - Phase 2 complete: Configuration, Authentication, Logging, OpenAI, Utilities, and Monitoring modules

## 🛠️ **Quick Start**

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- Git

### 1. Clone and Setup
```bash
git clone <your-repo>
cd agentic-microsaas-starter-full-personalized
```

### 2. Environment Setup
```bash
# Copy environment files
cp .env.example .env
cp docs/stripe.env.example stripe.env.example
cp docs/sendgrid.env.example sendgrid.env.example
cp docs/gcp-storage.env.example gcp-storage.env.example
cp docs/social-auth.env.example social-auth.env.example

# Edit .env with your settings
```

### 3. Start Infrastructure
```bash
# Start database and Redis
make dev.up

# Install dependencies
make install
```

### 4. Run Services
```bash
# Start all services
make dev

# Or start individually
make dev.api      # API service
make dev.agent    # Agent service  
make dev.web      # Web service
```

## 🎯 **What's Included**

### **Backend Services**
- **API Service** (FastAPI): Business logic, authentication, database
- **Agent Service** (Celery): AI processing, task execution
- **Database** (PostgreSQL): Centralized models and data

### **Frontend**
- **Web App** (Next.js): Dashboard, authentication, user interface
- **Components**: Subscription management, team management, file storage

### **Infrastructure**
- **Docker**: Containerized services
- **Terraform**: GCP deployment configuration
- **Monitoring**: Health checks, metrics, logging

## 🚀 **Deployment**

### Local Development
```bash
make dev
```

### Production (GCP)
```bash
# Deploy to GCP
cd infra/terraform
terraform init
terraform plan
terraform apply
```

## 📊 **Project Status**

**Phase 2 Complete!** Essential operational modules implemented:
- ✅ Configuration Management
- ✅ Authentication Utilities  
- ✅ Agent Configuration
- ✅ Logging Configuration
- ✅ OpenAI Configuration
- ✅ Common Utilities
- ✅ Monitoring Utilities

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Ready to build your AI-powered SaaS?** 🚀

Check out the [complete documentation](docs/README.md) for detailed setup and usage instructions.
