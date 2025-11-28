#!/bin/bash

# Sectify - One-command Docker setup script

set -e

echo "🐳 Sectify Docker Setup"
echo "======================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads models
echo "✅ Directories created"
echo ""

# Ask user which mode
echo "Select deployment mode:"
echo "  1) Production (optimized build)"
echo "  2) Development (hot reload)"
read -p "Enter choice [1-2]: " mode

echo ""

if [ "$mode" = "2" ]; then
    echo "🚀 Starting in Development mode..."
    echo ""
    docker-compose -f docker-compose.dev.yml up --build
else
    echo "🚀 Starting in Production mode..."
    echo ""
    
    # Ask if they want to run in background
    read -p "Run in background? (y/n): " background
    
    if [ "$background" = "y" ] || [ "$background" = "Y" ]; then
        docker-compose up -d --build
        echo ""
        echo "✅ Application is running in the background!"
        echo ""
        echo "📍 Access points:"
        echo "   Frontend: http://localhost"
        echo "   Backend:  http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo ""
        echo "📊 View logs:"
        echo "   docker-compose logs -f"
        echo ""
        echo "🛑 Stop application:"
        echo "   docker-compose down"
    else
        docker-compose up --build
    fi
fi
