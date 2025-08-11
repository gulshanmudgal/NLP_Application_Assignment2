# API Documentation

## Overview

The NLP Translation API provides high-performance multilingual text translation services. This RESTful API supports various language models and includes comprehensive caching, monitoring, and error handling.

## Base URLs

- **Production**: `https://api.yourdomain.com`
- **Staging**: `https://api-staging.yourdomain.com`
- **Development**: `http://localhost:8000`

## Authentication

Currently, the API uses rate limiting without authentication. Future versions will include API key authentication.

### Rate Limits

- **Free Tier**: 60 requests per minute
- **Burst Limit**: 10 requests per second
- **Daily Limit**: 1000 requests per day

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets (Unix timestamp)

## Endpoints

### Health Check

Check the API health and status.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "ml_models": "loaded"
  }
}
```

### Get Supported Languages

Retrieve list of supported source and target languages.

**Endpoint**: `GET /api/languages`

**Response**:
```json
{
  "languages": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English"
    },
    {
      "code": "es", 
      "name": "Spanish",
      "native_name": "Español"
    },
    {
      "code": "fr",
      "name": "French", 
      "native_name": "Français"
    },
    {
      "code": "de",
      "name": "German",
      "native_name": "Deutsch"
    },
    {
      "code": "hi",
      "name": "Hindi",
      "native_name": "हिन्दी"
    }
  ]
}
```

### Translate Text

Translate text from source language to target language.

**Endpoint**: `POST /api/translate`

**Request Body**:
```json
{
  "text": "Hello, how are you?",
  "source_lang": "en",
  "target_lang": "es",
  "model": "indictrans2"  // Optional, defaults to best available
}
```

**Parameters**:
- `text` (string, required): Text to translate (max 5000 characters)
- `source_lang` (string, required): Source language code (ISO 639-1)
- `target_lang` (string, required): Target language code (ISO 639-1)
- `model` (string, optional): Specific model to use

**Response**:
```json
{
  "translated_text": "Hola, ¿cómo estás?",
  "source_lang": "en",
  "target_lang": "es",
  "model_used": "indictrans2",
  "confidence": 0.95,
  "processing_time": 0.234,
  "cached": false,
  "translation_id": "trans_123456789"
}
```

### Batch Translation

Translate multiple texts in a single request.

**Endpoint**: `POST /api/translate/batch`

**Request Body**:
```json
{
  "texts": [
    "Hello world",
    "How are you?",
    "Good morning"
  ],
  "source_lang": "en",
  "target_lang": "es",
  "model": "indictrans2"
}
```

**Response**:
```json
{
  "translations": [
    {
      "input": "Hello world",
      "output": "Hola mundo",
      "confidence": 0.98
    },
    {
      "input": "How are you?", 
      "output": "¿Cómo estás?",
      "confidence": 0.95
    },
    {
      "input": "Good morning",
      "output": "Buenos días", 
      "confidence": 0.97
    }
  ],
  "source_lang": "en",
  "target_lang": "es",
  "model_used": "indictrans2",
  "total_processing_time": 0.456,
  "batch_id": "batch_123456789"
}
```

### Get Available Models

List all available translation models and their capabilities.

**Endpoint**: `GET /api/models`

**Response**:
```json
{
  "models": [
    {
      "name": "indictrans2",
      "description": "High-quality translation for Indian languages",
      "supported_languages": ["en", "hi", "bn", "ta", "te", "mr", "gu"],
      "model_size": "1.2GB",
      "avg_processing_time": 0.8,
      "quality_score": 0.92
    },
    {
      "name": "m2m100",
      "description": "Many-to-many multilingual translation",
      "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "ko", "zh"],
      "model_size": "2.4GB", 
      "avg_processing_time": 1.2,
      "quality_score": 0.89
    },
    {
      "name": "mbart50",
      "description": "Multilingual BART for translation",
      "supported_languages": ["en", "es", "fr", "de", "it", "pt", "ru", "ar", "hi", "zh"],
      "model_size": "2.6GB",
      "avg_processing_time": 1.0,
      "quality_score": 0.91
    }
  ]
}
```

### Get Translation History

Retrieve translation history for monitoring and analytics.

**Endpoint**: `GET /api/history`

**Query Parameters**:
- `limit` (integer, optional): Number of records to return (default: 50, max: 1000)
- `offset` (integer, optional): Number of records to skip (default: 0)
- `source_lang` (string, optional): Filter by source language
- `target_lang` (string, optional): Filter by target language
- `start_date` (string, optional): Start date (ISO format)
- `end_date` (string, optional): End date (ISO format)

**Response**:
```json
{
  "translations": [
    {
      "id": "trans_123456789",
      "text": "Hello world",
      "translated_text": "Hola mundo",
      "source_lang": "en",
      "target_lang": "es",
      "model": "indictrans2",
      "confidence": 0.98,
      "processing_time": 0.234,
      "timestamp": "2024-01-15T10:30:00Z",
      "cached": false
    }
  ],
  "total": 1247,
  "limit": 50,
  "offset": 0
}
```

### Cache Statistics

Get cache performance statistics.

**Endpoint**: `GET /api/cache/stats`

**Response**:
```json
{
  "cache_stats": {
    "hit_rate": 0.73,
    "total_requests": 15420,
    "cache_hits": 11257,
    "cache_misses": 4163,
    "cache_size": "245MB",
    "cache_entries": 8934,
    "avg_cache_time": 0.002
  },
  "top_cached_pairs": [
    {
      "source_lang": "en",
      "target_lang": "es", 
      "requests": 3421,
      "hit_rate": 0.81
    },
    {
      "source_lang": "en",
      "target_lang": "fr",
      "requests": 2156,
      "hit_rate": 0.76
    }
  ]
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error information.

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_LANGUAGE",
    "message": "Source language 'xyz' is not supported",
    "details": {
      "supported_languages": ["en", "es", "fr", "de", "hi"]
    },
    "request_id": "req_123456789",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | `INVALID_REQUEST` | Malformed request body or missing required fields |
| 400 | `INVALID_LANGUAGE` | Unsupported source or target language |
| 400 | `TEXT_TOO_LONG` | Input text exceeds maximum length limit |
| 400 | `EMPTY_TEXT` | Input text is empty or contains only whitespace |
| 429 | `RATE_LIMIT_EXCEEDED` | Rate limit exceeded for the client |
| 500 | `MODEL_ERROR` | Error loading or executing translation model |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Service temporarily unavailable |

### Error Examples

**Invalid Language**:
```json
{
  "error": {
    "code": "INVALID_LANGUAGE",
    "message": "Target language 'xyz' is not supported",
    "details": {
      "supported_languages": ["en", "es", "fr", "de", "hi", "bn", "ta"]
    }
  }
}
```

**Rate Limit Exceeded**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED", 
    "message": "Rate limit of 60 requests per minute exceeded",
    "details": {
      "limit": 60,
      "window": "1 minute",
      "reset_time": "2024-01-15T10:31:00Z"
    }
  }
}
```

**Text Too Long**:
```json
{
  "error": {
    "code": "TEXT_TOO_LONG",
    "message": "Input text exceeds maximum length of 5000 characters",
    "details": {
      "max_length": 5000,
      "provided_length": 7820
    }
  }
}
```

## SDKs and Libraries

### Python SDK

```python
import requests

class NLPTranslationClient:
    def __init__(self, base_url="https://api.yourdomain.com"):
        self.base_url = base_url
        
    def translate(self, text, source_lang, target_lang, model=None):
        response = requests.post(
            f"{self.base_url}/api/translate",
            json={
                "text": text,
                "source_lang": source_lang, 
                "target_lang": target_lang,
                "model": model
            }
        )
        return response.json()
        
    def get_languages(self):
        response = requests.get(f"{self.base_url}/api/languages")
        return response.json()

# Usage
client = NLPTranslationClient()
result = client.translate("Hello world", "en", "es")
print(result["translated_text"])  # "Hola mundo"
```

### JavaScript SDK

```javascript
class NLPTranslationClient {
    constructor(baseUrl = 'https://api.yourdomain.com') {
        this.baseUrl = baseUrl;
    }
    
    async translate(text, sourceLang, targetLang, model = null) {
        const response = await fetch(`${this.baseUrl}/api/translate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text,
                source_lang: sourceLang,
                target_lang: targetLang,
                model
            })
        });
        return response.json();
    }
    
    async getLanguages() {
        const response = await fetch(`${this.baseUrl}/api/languages`);
        return response.json();
    }
}

// Usage
const client = new NLPTranslationClient();
const result = await client.translate('Hello world', 'en', 'es');
console.log(result.translated_text); // "Hola mundo"
```

### cURL Examples

**Basic Translation**:
```bash
curl -X POST https://api.yourdomain.com/api/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, how are you?",
    "source_lang": "en",
    "target_lang": "es"
  }'
```

**Batch Translation**:
```bash
curl -X POST https://api.yourdomain.com/api/translate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Hello", "World", "How are you?"],
    "source_lang": "en", 
    "target_lang": "es"
  }'
```

**Get Languages**:
```bash
curl https://api.yourdomain.com/api/languages
```

## Performance Guidelines

### Best Practices

1. **Caching**: The API automatically caches translations. Avoid unnecessary duplicate requests.

2. **Batch Requests**: Use batch translation for multiple texts to reduce overhead.

3. **Model Selection**: Choose the appropriate model for your language pair and quality requirements.

4. **Rate Limiting**: Implement client-side rate limiting to avoid hitting API limits.

5. **Error Handling**: Always implement proper error handling and retry logic.

### Performance Metrics

- **Average Response Time**: 200-800ms depending on text length and model
- **Throughput**: Up to 100 requests per second
- **Cache Hit Rate**: ~75% for common language pairs
- **Uptime**: 99.9% SLA

### Optimization Tips

1. **Text Length**: Shorter texts translate faster. Consider breaking long texts into sentences.

2. **Language Pairs**: Some language pairs are faster than others due to model optimization.

3. **Caching**: Identical requests are served from cache with <5ms response time.

4. **Batch Size**: Optimal batch size is 10-50 texts per request.

## Support

### Getting Help

- **Documentation**: This API documentation
- **Email Support**: api-support@yourdomain.com
- **Issue Tracker**: https://github.com/your-org/nlp-translation-app/issues
- **Status Page**: https://status.yourdomain.com

### SLA and Uptime

- **Availability**: 99.9% uptime guarantee
- **Response Time**: <1 second for 95% of requests
- **Support Hours**: 24/7 for critical issues, business hours for general support

### Changelog

#### Version 1.0.0 (Current)
- Initial API release
- Support for 15+ languages
- 3 translation models
- Caching and rate limiting
- Comprehensive monitoring

#### Upcoming Features
- API key authentication
- Webhook notifications
- Custom model training
- Real-time translation streaming
- Advanced analytics dashboard
