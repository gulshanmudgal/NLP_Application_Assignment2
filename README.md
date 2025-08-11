# NLP Translation Application

A multi-language translation web application supporting Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi) using state-of-the-art ML models.

## Project Structure

```
Assignment_Part_2_V/
├── frontend/              # React TypeScript frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── types/         # TypeScript type definitions
│   │   ├── services/      # API service layer
│   │   └── styles/        # CSS and styling
│   ├── public/            # Static assets
│   └── package.json       # Node.js dependencies
├── backend/               # FastAPI Python backend
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # Business logic
│   │   └── core/          # Core utilities
│   └── requirements.txt   # Python dependencies
├── ml_models/             # Machine learning components
│   ├── training/          # Model training scripts
│   ├── evaluation/        # Evaluation metrics
│   └── inference/         # Model inference
├── docker/                # Docker configuration
├── tests/                 # Test suites
└── docs/                  # Documentation
```

## Features

- **Multi-language Support**: Translation between English and Indian languages
- **Real-time Translation**: Fast, responsive translation interface
- **Caching**: Redis-based caching for improved performance
- **Model Integration**: Support for IndicTrans and mT5 models
- **Comprehensive Testing**: Unit, integration, and end-to-end tests
- **Production Ready**: Docker containerization and monitoring

## Supported Languages

- Hindi (हिन्दी)
- Tamil (தமிழ்)
- Telugu (తెలుగు)
- Bengali (বাংলা)
- Marathi (मराठी)
- English

## Technology Stack

### Frontend
- React 18 with TypeScript
- Styled Components for styling
- React Query for state management
- Jest & React Testing Library for testing

### Backend
- FastAPI for REST API
- Pydantic for data validation
- Redis for caching
- PostgreSQL for data persistence
- Uvicorn as ASGI server

### ML Models
- IndicTrans for Indic language translation
- mT5 for multilingual translation
- Hugging Face Transformers
- PyTorch for model inference

## 🚀 Production Deployment

### Quick Production Deployment

1. **Clone and Configure**:
   ```bash
   git clone https://github.com/your-org/nlp-translation-app.git
   cd nlp-translation-app
   cp docker/.env.prod.template docker/.env.prod
   # Edit .env.prod with your production values
   ```

2. **Deploy with Script**:
   ```bash
   chmod +x scripts/deploy-production.sh
   ./scripts/deploy-production.sh
   ```

3. **Access Application**:
   - Frontend: https://yourdomain.com
   - API: https://api.yourdomain.com
   - Monitoring: http://yourdomain.com:3001 (Grafana)

### Production Features

- **High Availability**: Load-balanced backend with health checks
- **Security**: SSL/HTTPS, secure credentials management
- **Monitoring**: Prometheus + Grafana dashboards
- **Backup**: Automated database and Redis backups
- **CI/CD**: GitHub Actions with automated testing and deployment
- **Caching**: Redis-based translation caching
- **Rate Limiting**: API rate limiting and abuse protection

### Scaling

The application supports horizontal scaling:
```yaml
# Increase backend replicas
backend:
  deploy:
    replicas: 4
```

### Monitoring

Access comprehensive monitoring at:
- **Grafana**: http://your-domain:3001
- **Prometheus**: http://your-domain:9090

Key metrics include:
- Translation requests/second
- API response times
- Error rates
- Resource utilization
- Cache hit rates

For detailed deployment instructions, see [docs/deployment-guide.md](docs/deployment-guide.md).

## 📖 Documentation

- [**Deployment Guide**](docs/deployment-guide.md) - Complete production deployment instructions
- [**API Documentation**](docs/api-documentation.md) - Comprehensive API reference
- [**Architecture Overview**](docs/architecture.md) - System design and components

## Development Workflow

1. **Setup Environment**: Use Docker for consistent development
2. **Run Tests**: Execute comprehensive test suite
3. **Code Quality**: Follow ESLint, Prettier, and Black formatting
4. **Documentation**: Update docs for new features

## API Endpoints

- `POST /translate` - Translate text between languages
- `GET /languages` - Get supported language pairs
- `GET /health` - Health check endpoint

## Scripts

### 1. `deploy-dev.sh` (Full Development Deployment)

A comprehensive development deployment script that:
- Checks all prerequisites (Node.js, npm, Python 3, pip3)
- Installs all frontend dependencies (npm packages)
- Creates Python virtual environment and installs backend dependencies
- Starts both frontend and backend servers concurrently
- Performs health checks on both services
- Provides real-time log monitoring
- Handles graceful shutdown with Ctrl+C

**Usage:**
```bash
./scripts/deploy-dev.sh
```

**Features:**
- ✅ Automatic dependency installation
- ✅ Port conflict detection and resolution
- ✅ Health checks for both services
- ✅ Real-time log monitoring
- ✅ Graceful shutdown handling
- ✅ Colored output for better readability

**Services Started:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 2. `dev-simple.sh` (Quick Development Start)

A simpler script for quick development setup:
- Installs frontend and backend dependencies
- Starts backend in background
- Starts frontend in foreground

**Usage:**
```bash
./scripts/dev-simple.sh
```

## Makefile Integration

The scripts are integrated into the project Makefile for easy access:

```bash
# Quick development start
make dev

# Full development deployment with monitoring
make dev-full

# Traditional setup (dependencies only)
make setup

# Start only frontend
make frontend

# Start only backend  
make backend
```

## Prerequisites

Before running any development deployment script, ensure you have:

1. **Node.js** (v14 or higher)
2. **npm** (usually comes with Node.js)
3. **Python 3** (v3.8 or higher)
4. **pip3** (Python package manager)

## Ports Used

The application uses the following ports in development:

- **3000**: React frontend development server
- **8000**: FastAPI backend server

Make sure these ports are available before running the scripts.

## Logs

When using `deploy-dev.sh`, logs are saved to:
- Backend logs: `backend/backend.log`
- Frontend logs: `frontend/frontend.log`

## Stopping Services

### For `deploy-dev.sh`:
- Press `Ctrl+C` to stop both services gracefully

### For `dev-simple.sh`:
- Press `Ctrl+C` to stop the frontend
- Backend runs in background - you may need to find and kill the process manually:
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```

## Troubleshooting

### Port Already in Use
The `deploy-dev.sh` script automatically detects and kills processes using ports 3000 and 8000. If you encounter port conflicts with `dev-simple.sh`, manually kill the processes:

```bash
# Kill process on port 3000 (frontend)
lsof -ti:3000 | xargs kill -9

# Kill process on port 8000 (backend)  
lsof -ti:8000 | xargs kill -9
```

### Dependencies Not Installing
1. Ensure you have the correct Node.js and Python versions
2. Check your internet connection
3. Clear npm cache: `npm cache clean --force`
4. Remove `node_modules` and reinstall: `rm -rf frontend/node_modules && cd frontend && npm install`

### Backend Not Starting
1. Check if all Python dependencies are installed
2. Ensure you're using the correct Python version
3. Check the backend logs for detailed error messages

### Frontend Not Starting
1. Check if all npm packages are installed correctly
2. Ensure port 3000 is available
3. Check the frontend logs for detailed error messages

## Development Workflow

Recommended workflow for development:

1. **First time setup:**
   ```bash
   make dev-full
   ```

2. **Subsequent development sessions:**
   ```bash
   make dev
   ```

3. **When you need to see detailed logs:**
   ```bash
   make dev-full
   ```

4. **For testing individual components:**
   ```bash
   make backend  # Start only backend
   # or
   make frontend # Start only frontend
   ```


## Model Performance

The application uses fine-tuned models achieving:
- BLEU scores: 25-35 for major Indian language pairs
- Average latency: <500ms per translation
- Supports batch translation for efficiency

## Contributing

1. Follow the implementation plan in the project root
2. Write tests for all new features
3. Ensure code passes linting and formatting checks
4. Update documentation for significant changes

## License

This project is developed for educational purposes as part of NLP coursework.
