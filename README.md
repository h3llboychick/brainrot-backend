# Brainrot Automation Backend

FastAPI backend for automated "brainrot" video generation and social media publishing. The system uses **Clean Architecture**, **Celery** workers for async video processing, and supports pluggable video formats with automated publishing to platforms like YouTube.

> **Personal project** — built to explore clean architecture, distributed task processing, payment integration, and production-grade auth patterns in Python.

## Features

- **Auth** — Email/password + Google OAuth, JWT access/refresh tokens, email verification
- **Video Generation** — AI-scripted content (SambaNova), TTS (ElevenLabs), stock footage (Pexels), composed via ffmpeg
- **Social Publishing** — Link YouTube (+ extensible to TikTok/Instagram), automated upload after generation
- **Credit System** — Stripe-powered top-ups, balance ledger with reservation/compensation pattern
- **Encryption** — KEK/DEK envelope encryption for storing social account credentials
- **Real-time Updates** — Redis pub/sub for job status notifications
- **Rate Limiting** — SlowAPI middleware on API routes

## Key Decisions & Discoveries

This section covers the architectural choices I found most interesting while building the project.

### 🏢 Clean Architecture & Use Cases

I chose Clean Architecture because the layer separation (domain → infrastructure → presentation) makes sense to me intuitively. Business rules live in `domain/`, all external concerns (DB, Redis, APIs) are behind interfaces in `infrastructure/`, and the API surface is a thin `presentation/` layer. The **Interface Segregation** and **Dependency Inversion** principles keep every layer testable in isolation.

The **Use Case pattern** was new to me and turned out to be one of my favourite discoveries. Each operation (register user, generate video, connect social account…) is a single class with one `execute()` method. This keeps FastAPI routers simple and clean - they just validate input, call a use case, and return the response. No business logic leaks into the presentation layer.

### 👷 Celery & Worker Architecture

This was my first time working with Celery. The documentation for this tools is excellent and setting up a scalable worker pipeline (RabbitMQ broker → Celery → MinIO) was surprisingly easy. The worker runs as a **fully independent service** - it has its own Docker image (Alpine + ffmpeg + ImageMagick), its own DB models and repositories, and communicates with the main API only through RabbitMQ and Redis.

I designed the worker around **registries** - a `VideoFormatRegistry` and a `PlatformPublisherRegistry` - so adding a new video format or social platform is a matter of implementing a single class and registering it. No existing code needs to change (Open Closed Principle in practice).

### 🔐 JWT Refresh/Access Token Pattern

Reading about how refresh and access tokens work in depth was probably the most educational part. The access token is short-lived (30 min) and the refresh token is long-lived (30 days), hashed before storage. This combination gives a nice balance between security and UX - the client rarely needs to re-authenticate, but token theft has a limited blast radius.

### ✉️ KEK/DEK Envelope Encryption

I use envelope encryption to store social account credentials (YouTube OAuth tokens). A master **Key Encryption Key** (KEK) encrypts per-record **Data Encryption Keys** (DEKs), so rotating the master key doesn't require re-encrypting every record. I was surprised by how elegant and simple this turned out to be. The implementation is straightforward, yet it gives you real key-rotation capabilities.

### 💳 Stripe Integration

Stripe was really pleasant to work with. The SDK, docs, and webhook model are well-designed. I use a reservation-based payment flow - balance is reserved when a job starts and either confirmed or compensated depending on the outcome (a simplified **Saga pattern**). I'll definitely use Stripe again in future projects.

## Architecture

```
src/
├── domain/           # Entities, DTOs, interfaces, use cases, exceptions, enums
├── infrastructure/   # DB (SQLAlchemy/Alembic), Redis, services (JWT, email, Stripe, encryption…)
├── presentation/     # FastAPI routers, DI container, middlewares
└── worker/           # Independent Celery service (own models, tasks, clients)
```

### Tech Stack

| Concern | Technology |
|---------|-----------|
| API framework | FastAPI (async) |
| Task queue | Celery + RabbitMQ |
| Database | PostgreSQL + SQLAlchemy (async) + Alembic |
| Cache / Pub-sub | Redis |
| Object storage | MinIO (S3-compatible) |
| Payments | Stripe |
| AI / TTS / Footage | SambaNova, ElevenLabs, Pexels |
| Video compositing | ffmpeg + ImageMagick (in worker container) |

### Video Processing Pipeline

```
User creates job → API reserves balance → RabbitMQ message
  → Worker generates script (AI) → TTS → stock footage → ffmpeg compose
    → Upload to MinIO → Publish to social accounts → Confirm charge
      → Status updates via Redis pub/sub
```

## Project Structure

```
backend/
├── src/
│   ├── domain/
│   │   ├── entities/           # User, VideoJob, SocialAccount, BalanceTransaction…
│   │   ├── dtos/               # auth/, encryption/, social_accounts/, videos/
│   │   ├── enums/              # UserRole, VideoJobStatus, SocialPlatform…
│   │   ├── exceptions/         # Granular exception hierarchy (auth, payments, videos…)
│   │   ├── interfaces/
│   │   │   ├── repositories/   # Abstract repos (user, token, video, balance…)
│   │   │   └── services/       # Abstract services (email, encryption, hashing…)
│   │   └── use_cases/          # auth/ payments/ social_accounts/ videos/
│   ├── infrastructure/
│   │   ├── db/                 # SQLAlchemy models, repository implementations
│   │   ├── redis/              # Verification code & YouTube OAuth state repos
│   │   ├── services/           # email/ encryption/ hashing/ jwt/ payment/ validators/ video_processing/
│   │   ├── logging/            # Structured logger
│   │   ├── rate_limiting/      # SlowAPI limiter
│   │   └── celery_app.py
│   ├── presentation/
│   │   ├── routers/            # auth/ users/ videos/ accounts/ payment/
│   │   ├── di/                 # Dependency injection providers
│   │   ├── middlewares/        # Error handler
│   │   └── schemas.py          # Pydantic request/response schemas
│   ├── worker/                 # Independent Celery worker service
│   │   ├── worker/
│   │   │   ├── app.py          # Celery app entry point
│   │   │   ├── tasks/          # generate_video, publish_video, confirm_charge, compensate
│   │   │   ├── services/       # video_formats/, platform_publishers/, voiceover, storage…
│   │   │   ├── clients/        # ai, elevenlabs, minio, pexels, redis
│   │   │   ├── db/             # Worker-side models & repositories
│   │   │   ├── domain/         # Worker domain (format registry, publisher registry)
│   │   │   ├── prompts/        # AI prompt templates
│   │   │   └── utils/          # Audio, AI helpers, encryption
│   │   ├── media/              # Static assets for video generation
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── main.py                 # FastAPI app factory + lifespan
│   └── settings.py             # Pydantic settings
├── alembic/                    # Database migration versions
├── scripts/                    # Admin utilities (balance, payments, pricing)
├── tests/unit/                 # Unit tests for domain use cases
├── compose.yaml                # Docker Compose (Postgres, Redis, RabbitMQ, MinIO, Worker)
├── setup.sh                    # Automated setup script
├── run.py                      # App launcher
└── pyproject.toml
```

## Quick Start

### Prerequisites

- **Python 3.12+** (main API) / **Python 3.11+** (worker)
- **Docker** with Compose
- External API keys: Google OAuth, YouTube API, SambaNova, ElevenLabs, Pexels, Stripe (see `.env.example`)

### Automated Setup

```bash
git clone https://github.com/h3llboychick/brainrot-backend.git
cd brainrot-backend
./setup.sh
```

The script will:
1. Create `.env` and `src/worker/.env` from their example files
2. Generate secure secrets (JWT, session, KEK) and sync KEK to the worker
3. Build the Celery worker Docker image
4. Start all Docker Compose services
5. Install Python dependencies (via `uv` if available, otherwise `pip`)
6. Run Alembic database migrations

After setup, fill in your API keys in `.env` and `src/worker/.env`, then:

```bash
python run.py            # API at http://127.0.0.1:8000
```

### Service Dashboards

| Service | URL |
|---------|-----|
| API Docs (Swagger) | http://127.0.0.1:8000/docs |
| RabbitMQ Management | http://127.0.0.1:15672 |
| MinIO Console | http://127.0.0.1:9001 |

## Contributing

1. Fork & create a feature branch
2. Follow the clean architecture pattern — business logic in `domain/`, implementations in `infrastructure/`
3. Write unit tests for new use cases
4. Use type hints; the project uses Ruff for linting and Mypy for type checking
5. Open a Pull Request

## Author

**h3llboychick** — [GitHub](https://github.com/h3llboychick)

---

*This is a personal/educational project. Use responsibly and follow all third-party service terms of service.*
