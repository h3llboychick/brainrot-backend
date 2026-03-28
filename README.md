# Brainrot Automation Backend

FastAPI-based backend service for automated brainrot video generation and automatic social media publishing. The system uses clean architecture principles with Celery workers for asynchronous video processing, supporting multiple video formats and automated publishing to platforms like YouTube.

## 🏗️ Architecture

This project follows **Clean Architecture** principles:

```
src/
├── domain/              # Business logic layer (entities, DTOs, interfaces, use cases)
├── infrastructure/      # External concerns (database, services)
├── worker/              # Independent Celery worker service
└── presentation/        # API layer (FastAPI routers, schemas, DI)
```

### Key Components

- **FastAPI**: Modern async web framework for the REST API
- **Celery**: Distributed task queue for video processing
- **PostgreSQL**: Primary database for users, videos, and social accounts
- **Redis**: Caching and pub/sub for real-time updates
- **RabbitMQ**: Message broker for Celery tasks
- **MinIO**: S3-compatible object storage for video files
- **SQLAlchemy**: ORM with async support
- **Alembic**: Database migrations

## ✨ Features

- 🔐 **Authentication**: Email/password + Google OAuth with JWT tokens
- 📧 **Email Verification**: SMTP-based email confirmation system
- 🎬 **Video Generation**: AI-powered script generation with multiple format support
- 📱 **Social Media**: YouTube account linking and automated publishing
- 🔒 **Encryption**: Envelope encryption for storing social account credentials
- 💰 **Credit System**: User balance tracking for video generation
- 🔄 **Real-time Updates**: Redis pub/sub for job status notifications

## 📋 Prerequisites

- **Python 3.12+** (main API) or **Python 3.11+** (worker)
- **Docker** (recommended for easy setup)
- **uv** package manager (optional, for main API development)
- External API keys (see Environment Configuration)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/h3llboychick/brainrot-backend.git
cd brainrot-backend
```

### 2. Environment Configuration

Copy the example environment files and fill in your actual values:

```bash
# Main application
cp .env.example .env

# Worker (if running separately)
cp src/worker/.env.example src/worker/.env
```

**Important**: Generate secure keys for the following variables:

```bash
# JWT Secret Key
python -c "import secrets; print(secrets.token_hex(32))"

# Session Middleware Secret Key
python -c "import secrets; print(secrets.token_hex(32))"

# KEK Key (for encryption)
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3. Obtain External API Keys

You'll need to register and get API keys from:

- **Google OAuth**: [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
  - Create OAuth 2.0 credentials
  - Set authorized redirect URIs
  - Download `client_secrets.json`

- **YouTube API**: Same as Google OAuth (enable YouTube Data API v3)

- **SambaNova AI**: [SambaNova Platform](https://sambanova.ai/)

- **ElevenLabs**: [ElevenLabs Dashboard](https://elevenlabs.io/)

- **Pexels**: [Pexels API](https://www.pexels.com/api/)

### 4. Build the Worker Docker Image

The worker requires a custom Docker image with ffmpeg, ImageMagick, and Python dependencies. Build it once and reuse:

```bash
cd src/worker
docker build -t worker-base:py311-alpine-2025-10-31 .
```

### 5. Start Services with Docker Compose

```bash
# From the backend directory
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- RabbitMQ (ports 5672, 15672 for management UI)
- MinIO (ports 9000, 9001 for console)
- Celery Worker

### 6. Installing Dependencies

#### Main API (using uv)

```bash
# Install uv if you haven't
pip install uv

# Install dependencies
uv pip install -r requirements.txt
```

### 7. Run Database Migrations

```bash
# Install Alembic if not already installed
pip install alembic

# Run migrations
alembic upgrade head
```

### 8. Start the FastAPI Application

#### Using the run script

```bash
python run.py
```

The API will be available at `http://127.0.0.1:8000`.

### 9. Access Service Dashboards

- **API Documentation (Swagger)**: http://127.0.0.1:8000/docs
- **RabbitMQ Management**: http://127.0.0.1:15672 (guest/guest)
- **MinIO Console**: http://127.0.0.1:9001 (minioadmin/minioadmin)


## 📁 Project Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files (commit these!)
│   └── env.py                  # Alembic configuration
├── src/
│   ├── domain/                 # Business logic
│   │   ├── entities/           # Domain entities
│   │   ├── interfaces/         # Repository & service contracts
│   │   ├── use_cases/          # Application business logic
│   │   ├── dtos/               # Data transfer objects
│   │   ├── enums/              # Enumerations
│   │   └── exceptions/         # All exceptions
│   ├── infrastructure/         # External integrations
│   │   ├── db/                 # Database models & repositories
│   │   ├── redis/              # Redis repositories
│   │   └── services/           # Email, JWT, encryption, validation
│   ├── worker/                 # Celery worker application (independent service)
│   │   ├── worker/             # Worker code
│   │   │   ├── app.py          # Celery app configuration
│   │   │   ├── tasks/          # Celery tasks
│   │   │   ├── services/       # Video generation logic
│   │   │   └── clients/        # External API clients
│   │   ├── Dockerfile          # Worker image definition
│   │   └── requirements.txt    # Worker dependencies
│   ├── presentation/           # API layer
│   │   ├── routers/            # FastAPI route handlers
│   │   ├── di/                 # Dependency injection
│   │   └── middlewares/        # Error handlers
│   ├── main.py                 # Application entry point
│   └── settings.py             # App settings
├── .env.example                # Environment template
├── compose.yaml                # Docker Compose configuration
├── alembic.ini                 # Alembic configuration
└── run.py                      # Application launcher
```

## 🔧 Configuration

### Environment Variables

See `.env.example` for a complete list of required environment variables. Key categories:

- **Database**: PostgreSQL connection settings
- **Redis**: Cache and pub/sub configuration
- **Message Broker**: RabbitMQ/Celery settings
- **Storage**: MinIO S3-compatible object storage
- **Authentication**: JWT, session secrets, Google OAuth
- **External APIs**: YouTube, SambaNova AI, ElevenLabs, Pexels
- **Email**: SMTP configuration for sending verification emails
- **Encryption**: KEK key for envelope encryption

### Docker Compose Services

All services are configured in `compose.yaml`:

- **db**: PostgreSQL database with health checks
- **redis**: Redis for caching and pub/sub
- **rabbitmq**: Message broker with management UI
- **minio**: S3-compatible object storage
- **worker-1**: Celery worker for video processing

## 🎥 Video Processing Pipeline

1. **User creates video job** → API creates job in database
2. **Job posted to RabbitMQ** → Queue: `video.generate`
3. **Worker picks up task** → Generates video based on format
4. **Video uploaded to MinIO** → Stored in `videos` bucket
5. **Status updates via Redis** → Real-time notifications to clients
6. **Optional auto-publish** → Posts to connected social accounts

### Supported Video Formats

- Would You Rather (choice-based content)

## 🔐 Security

- **JWT Authentication**: Access + refresh token pattern
- **Envelope Encryption**: KEK/DEK for social account credentials
- **Password Hashing**: Secure password storage
- **Email Verification**: Confirm user email addresses
- **OAuth 2.0**: Google and YouTube integration
- **HTTPS Ready**: Configure reverse proxy for production

## 📊 Database Schema

Key entities:

- **User**: Authentication, balance, roles, verification status
- **RefreshToken**: JWT refresh token storage
- **SocialAccount**: Connected social media accounts (encrypted credentials)
- **VideoFormat**: Video generation templates/presets
- **VideoJob**: Video generation tasks with status tracking

## 🤝 Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Set up your development environment
4. Make your changes
5. Run tests and ensure they pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Follow the clean architecture pattern
- Write tests for new features
- Update documentation as needed
- Use type hints throughout
- Follow PEP 8 style guidelines
- Create meaningful commit messages

## 👥 Authors

- h3llboychick - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- Celery for distributed task processing
- All the external API providers (Google, SambaNova, ElevenLabs, Pexels)

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation

---

**Note**: This is an educational/personal project. Use responsibly and ensure compliance with all third-party service terms of service.
