#!/bin/bash

echo "Checking Docker installation..."

# Check if Docker Desktop app exists
if [ -d "/Applications/Docker.app" ]; then
    echo "✓ Docker Desktop is installed"
else
    echo "✗ Docker Desktop is not found in Applications"
fi

# Check if docker command is available
if command -v docker &> /dev/null; then
    echo "✓ Docker command is available"
    docker --version
else
    echo "✗ Docker command not found. Please start Docker Desktop first."
fi

# Check if docker compose command is available
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    echo "✓ Docker Compose is available"
    docker compose version
else
    echo "✗ Docker Compose not available. Please start Docker Desktop first."
fi

# Check if Docker daemon is running
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "✓ Docker daemon is running"
else
    echo "✗ Docker daemon is not running. Please start Docker Desktop from Applications."
fi

echo ""
echo "Next steps:"
echo "1. Open Docker Desktop from your Applications folder"
echo "2. Complete the initial setup if prompted"
echo "3. Wait for Docker to fully start (check menu bar for Docker icon)"
echo "4. Run this script again to verify everything is working"
