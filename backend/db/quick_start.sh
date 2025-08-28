#!/bin/bash

# Healthcare AI Database Quick Start Script
# This script automates the database setup process

set -e  # Exit on any error

echo "🏥 Healthcare AI Database Quick Start"
echo "===================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run this script from the backend/db directory"
    exit 1
fi

echo "📂 Current directory: $(pwd)"

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down --remove-orphans

# Remove old volumes if requested
read -p "🗑️  Do you want to reset the database (delete all data)? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Removing old volumes..."
    docker volume rm healthcare_postgres_data 2>/dev/null || true
    docker volume rm healthcare_pgadmin_data 2>/dev/null || true
fi

# Start the containers
echo "🚀 Starting database containers..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose exec postgres pg_isready -U postgres -d healthcare_ai >/dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ PostgreSQL failed to start within 30 seconds"
        docker-compose logs postgres
        exit 1
    fi
    sleep 1
done

# Check containers status
echo "🔍 Checking container status..."
docker-compose ps

# Test database connection
echo "🔗 Testing database connection..."
if docker-compose exec postgres psql -U postgres -d healthcare_ai -c "SELECT 'Database connection successful!' as status;" >/dev/null 2>&1; then
    echo "✅ Database connection test passed"
else
    echo "❌ Database connection test failed"
    exit 1
fi

# Show connection information
echo ""
echo "🎉 Database setup completed successfully!"
echo ""
echo "📊 Database Information:"
echo "   - Database: healthcare_ai"
echo "   - Host: localhost"
echo "   - Port: 5432"
echo "   - Username: postgres"
echo "   - Password: postgres"
echo ""
echo "🌐 PgAdmin (Database Management UI):"
echo "   - URL: http://localhost:8080"
echo "   - Email: admin@healthcare.com"
echo "   - Password: healthcare123"
echo ""
echo " Next Steps:"
echo "   1. Go to backend directory: cd .."
echo "   2. Install Python dependencies: pip install -r requirements.txt"
echo "   3. Start the server: python run_server.py"
echo ""
echo "📖 For detailed documentation, see: backend/db/README.md"
echo ""
echo "🛠️  Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop containers: docker-compose down"
echo "   - Restart: docker-compose restart"
echo "   - Connect to DB: docker-compose exec postgres psql -U postgres -d healthcare_ai"

# Optional: Create .env file template
ENV_FILE="../.env"
if [ ! -f "$ENV_FILE" ]; then
    echo ""
    read -p "📄 Do you want to create a .env file template? (Y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        cat > "$ENV_FILE" << EOF
# Healthcare AI Environment Configuration

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=healthcare_ai
DB_USER=postgres
DB_PASSWORD=postgres
DB_DEBUG=false

# API Keys (REQUIRED - Replace with your actual keys)
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Optional Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=info
EOF
        echo "✅ Created .env file template at $ENV_FILE"
        echo "⚠️  IMPORTANT: Please update the API keys in $ENV_FILE before starting the server"
    fi
fi

echo ""
echo "🎯 Setup completed! Your Healthcare AI database is ready to use." 