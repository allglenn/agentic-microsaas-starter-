# Agentic MicroSaaS Starter — Personalized

A comprehensive, production-ready microsaas boilerplate with AI agents, modern web interface, and cloud deployment capabilities.

## 🚀 Features

- **🤖 AI Agents**: Intelligent task processing with OpenAI integration
- **🌐 Modern Web App**: Next.js 14 with TypeScript, Tailwind CSS, and authentication
- **⚡ Fast API**: High-performance FastAPI backend with async support
- **🗄️ Database**: PostgreSQL with pgvector for semantic search
- **☁️ Cloud Ready**: Complete GCP deployment with Terraform
- **📊 Monitoring**: Built-in logging and performance tracking
- **🐳 Containerized**: Docker support for all services

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │   FastAPI API   │    │  Celery Agent   │
│   (Port 3000)   │◄──►│   (Port 8000)   │◄──►│   (Background)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   + pgvector    │
                    │   (Port 5432)   │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Redis       │
                    │   (Port 6379)   │
                    └─────────────────┘
```

## 🛠️ Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker & Docker Compose
- Google Cloud SDK (for deployment)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd agentic-microsaas-starter-full-personalized
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start infrastructure**:
   ```bash
   make dev.up
   # This starts PostgreSQL and Redis
   ```

3. **Start services** (in separate terminals):
   ```bash
   make web.dev    # Next.js web app
   make api.dev    # FastAPI backend
   make agent.dev  # Celery worker
   ```

4. **Access the application**:
   - Web App: http://localhost:3000
   - API Docs: http://localhost:8000/docs
   - Database: localhost:5432

### Environment Variables

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentic_microsaas
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Google Cloud
GOOGLE_CLOUD_PROJECT=agentic-microsaas
GOOGLE_CLOUD_REGION=europe-west1

# Authentication
NEXTAUTH_SECRET=your_nextauth_secret_here
NEXTAUTH_URL=http://localhost:3000

# API Keys
API_SECRET_KEY=your_api_secret_key_here
```

## 🚀 Deployment

### Google Cloud Platform

1. **Initialize Terraform**:
   ```bash
   make tf.init
   ```

2. **Deploy infrastructure**:
   ```bash
   make tf.apply
   ```

3. **Deploy services**:
   ```bash
   make cr.deploy
   ```

### Docker Compose

For local development with containers:

```bash
docker-compose up -d
```

## 📁 Project Structure

```
├── apps/
│   ├── web/           # Next.js frontend
│   ├── api/           # FastAPI backend
│   └── agent/         # Celery worker
├── infra/
│   └── terraform/     # Infrastructure as code
├── docker-compose.yml # Local development
└── Makefile          # Development commands
```

## 🔧 Development Commands

```bash
# Start local infrastructure
make dev.up

# Start individual services
make web.dev
make api.dev
make agent.dev

# Database operations
make sql.init

# Terraform operations
make tf.init
make tf.apply

# Cloud Run deployment
make cr.deploy
```

## 🧪 API Endpoints

### Authentication
- `POST /users` - Create user
- `GET /users/me` - Get current user

### Agents
- `POST /agents` - Create agent
- `GET /agents` - List user agents
- `GET /agents/{id}` - Get agent details

### Tasks
- `POST /tasks` - Create task
- `GET /tasks` - List user tasks
- `GET /tasks/{id}` - Get task details

### Analytics
- `GET /analytics/api-calls` - API usage analytics

## 🤖 AI Agents

The platform supports intelligent AI agents that can:

- Process natural language tasks
- Make decisions based on context
- Integrate with external APIs
- Learn from user interactions

### Creating an Agent

```python
agent_data = {
    "name": "Customer Support Agent",
    "description": "Handles customer inquiries",
    "prompt": "You are a helpful customer support agent..."
}
```

## 📊 Monitoring

Built-in monitoring includes:

- Request/response logging
- Performance metrics
- Error tracking
- Task execution monitoring

## 🔒 Security

- JWT-based authentication
- CORS protection
- Input validation
- SQL injection prevention
- Rate limiting (configurable)

## 🚀 Production Considerations

- Use environment-specific configurations
- Set up proper secret management
- Configure monitoring and alerting
- Set up backup strategies
- Implement proper logging
- Use HTTPS everywhere
- Set up CI/CD pipelines

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For questions and support, please open an issue in the repository.

## Author

Created by **Glenn Allogho**

-   **Email**: `glennfreelance365@gmail.com`
-   **LinkedIn**: [glenn-allogho](https://www.linkedin.com/in/glenn-allogho-94649688/)
-   **Medium**: [@glennlenormand](https://medium.com/@glennlenormand)
-   **Twitter**: [@glenn_all](https://twitter.com/glenn_all)
-   **GitHub**: [@allglenn](https://github.com/allglenn)
-   **GitLab**: [@glennlenormand](https://gitlab.com/glennlenormand)
