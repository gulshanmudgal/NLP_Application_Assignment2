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
