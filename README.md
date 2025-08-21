# IA Developer Challenge - Financial Restructuring Assistant

A FastAPI application designed as a financial restructuring assistant using artificial intelligence. This project implements a scalable backend architecture with comprehensive API documentation and containerized deployment.

## 🎯 Project Overview

This technical challenge demonstrates the development of an AI-powered financial assistant that helps with financial restructuring tasks.

## ✨ Features

- 🚀 **FastAPI Framework** - High-performance async API with automatic OpenAPI documentation
- 🐳 **Docker Support** - Containerized application with Docker Compose orchestration
- 📦 **Modern Python Packaging** - Uses `uv` for fast dependency management
- 📖 **API Documentation** - Interactive Swagger UI documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- UV package manager (recommended) or pip

### Option 1: Docker Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd desafio_tecnico_ia_developer
   ```

2. **Start the application with Docker Compose**
   ```bash
   docker-compose up --build
   ```

3. **Access the application**
   - API Documentation (Swagger UI): http://localhost:8000/docs
   - Alternative Documentation (ReDoc): http://localhost:8000/redoc
   - Health Check: http://localhost:8000/api/v1/health

### Option 2: Local Development

1. **Navigate to the backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies using UV**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## ⚙️ Configuration

The application uses environment-based configuration. Key settings can be modified in `backend/app/core/config.py`

- **PROJECT_NAME**: Application name
- **PROJECT_DESCRIPTION**: Application description
- **VERSION**: API version
- **API_V1_STR**: API prefix (`/api/v1`)
- **ALLOWED_ORIGINS**: CORS origins configuration
- **HOST** and **PORT**: Server configuration
- **DEBUG**: Debug mode toggle

Or set environment variables directly in your deployment environment. A `.env.example` file is provided as a template.
