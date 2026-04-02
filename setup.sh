#!/usr/bin/env bash
# =============================================================================
# Brainrot Automation Backend — Setup Script
# =============================================================================
# Automates: env file creation, secret generation, Docker image build,
#            Docker Compose services startup, and database migrations.
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERR]${NC}   $*"; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

# ---- helpers ----------------------------------------------------------------

generate_secret() {
    python3 -c "import secrets; print(secrets.token_hex(32))"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "$1 is required but not installed."
        exit 1
    fi
}

# ---- pre-flight checks -----------------------------------------------------

info "Checking prerequisites..."
check_command python3
check_command docker
check_command docker

if ! docker compose version &> /dev/null && ! docker-compose version &> /dev/null; then
    error "docker compose (plugin or standalone) is required."
    exit 1
fi

COMPOSE_CMD="docker compose"
if ! docker compose version &> /dev/null; then
    COMPOSE_CMD="docker-compose"
fi

success "All prerequisites found (python3, docker, $COMPOSE_CMD)."

# ---- environment files ------------------------------------------------------

setup_env_file() {
    local src="$1" dest="$2" label="$3"
    if [[ -f "$dest" ]]; then
        warn "$label .env already exists at $dest — skipping."
    else
        cp "$src" "$dest"
        success "Created $dest from $src"
    fi
}

info "Setting up environment files..."
setup_env_file ".env.example" ".env" "Main app"
setup_env_file "src/worker/.env.example" "src/worker/.env" "Worker"

# ---- generate secrets -------------------------------------------------------

inject_secret() {
    local file="$1" key="$2" placeholder="$3"
    if grep -q "$placeholder" "$file" 2>/dev/null; then
        local secret
        secret=$(generate_secret)
        # works on both GNU and BSD sed
        sed -i.bak "s|${placeholder}|${secret}|" "$file" && rm -f "${file}.bak"
        success "Generated secret for $key in $file"
    fi
}

info "Generating secure keys (only replaces placeholders)..."
inject_secret ".env" "JWT_SECRET_KEY"                "your-secret-key"
inject_secret ".env" "SESSION_MIDDLEWARE_SECRET_KEY"  "your-session-secret-key"
inject_secret ".env" "SECRET_KEY"                     "your-general-secret-key-here"
inject_secret ".env" "KEK_KEY"                        "your-kek-key"

# The worker KEK must match the main app KEK
MAIN_KEK=$(grep '^KEK_KEY=' .env | cut -d'=' -f2-)
if [[ -n "$MAIN_KEK" ]]; then
    sed -i.bak "s|your-kek-key-here-replace-with-64-char-hex-string|${MAIN_KEK}|" src/worker/.env && rm -f src/worker/.env.bak
    success "Synced KEK_KEY to worker .env"
fi

# ---- build worker image ----------------------------------------------------

info "Building Celery worker Docker image..."
docker build -t worker-base:latest src/worker/
success "Worker image built: worker-base:latest"

# ---- start services ---------------------------------------------------------

info "Starting Docker Compose services..."
$COMPOSE_CMD up -d
success "All services are up."

# ---- wait for database ------------------------------------------------------

info "Waiting for PostgreSQL to be ready..."
RETRIES=30
until docker exec db pg_isready -U postgres &> /dev/null || [[ $RETRIES -eq 0 ]]; do
    sleep 1
    ((RETRIES--))
done

if [[ $RETRIES -eq 0 ]]; then
    error "PostgreSQL did not become ready in time."
    exit 1
fi
success "PostgreSQL is ready."

# ---- python dependencies ----------------------------------------------------

info "Installing Python dependencies..."
if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt
    success "Dependencies installed via uv."
else
    pip install -r requirements.txt
    success "Dependencies installed via pip."
fi

# ---- database migrations ----------------------------------------------------

info "Running Alembic migrations..."
alembic upgrade head
success "Database migrations applied."

# ---- done -------------------------------------------------------------------

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Setup complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
info "Next steps:"
echo "  1. Fill in your API keys in .env and src/worker/.env"
echo "     (Google OAuth, YouTube, SambaNova, ElevenLabs, Pexels, Stripe)"
echo "  2. Place your Google OAuth client_secrets.json in the project root"
echo "  3. Start the API server:  python run.py"
echo "  4. Open the docs:         http://127.0.0.1:8000/docs"
echo ""
info "Service dashboards:"
echo "  • RabbitMQ Management:  http://127.0.0.1:15672  (guest/guest)"
echo "  • MinIO Console:        http://127.0.0.1:9001   (minioadmin/minioadmin)"
echo ""
