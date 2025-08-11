"""
Configuration and fixtures for testing the NLP Translation Application.

This module provides shared test fixtures, mock objects, and configuration
for the comprehensive test suite.
"""

import pytest
import asyncio
from typing import Dict, Any, AsyncGenerator
from unittest.mock import Mock, AsyncMock
import tempfile
import os

# Test data for translation testing
TRANSLATION_TEST_CASES = [
    {
        "text": "hello",
        "source_lang": "en",
        "target_lang": "hi",
        "expected_contains": ["नमस्ते", "हैलो"],  # Either translation is acceptable
        "model": "lightweight_indictrans"
    },
    {
        "text": "good morning",
        "source_lang": "en", 
        "target_lang": "hi",
        "expected_contains": ["सुप्रभात", "शुभ प्रभात"],
        "model": "lightweight_indictrans"
    },
    {
        "text": "thank you",
        "source_lang": "en",
        "target_lang": "hi", 
        "expected_contains": ["धन्यवाद", "शुक्रिया"],
        "model": "lightweight_indictrans"
    },
    {
        "text": "How are you?",
        "source_lang": "en",
        "target_lang": "hi",
        "expected_contains": ["कैसे हैं", "क्या हाल"],
        "model": "lightweight_indictrans"
    }
]

# Language pairs for testing
SUPPORTED_LANGUAGE_PAIRS = [
    ("en", "hi"),  # English to Hindi
    ("hi", "en"),  # Hindi to English
    ("en", "ta"),  # English to Tamil
    ("en", "te"),  # English to Telugu
    ("en", "bn"),  # English to Bengali
    ("en", "mr"),  # English to Marathi
]

# Models available for testing
AVAILABLE_MODELS = [
    "mock",
    "lightweight_indictrans", 
    "indictrans",
    "m2m100",
    "mbart",
    "auto"
]

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_redis():
    """Mock Redis connection for testing cache functionality."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.exists.return_value = False
    return mock_redis

@pytest.fixture
def mock_model_config():
    """Mock model configuration for testing."""
    return {
        "cache_dir": "/tmp/test_models",
        "max_memory_usage": "1GB",
        "device": "cpu",
        "batch_size": 1
    }

@pytest.fixture
def temp_model_cache():
    """Create temporary directory for model cache testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_translation_response():
    """Mock translation response for API testing."""
    return {
        "translated_text": "नमस्ते",
        "source_language": "en",
        "target_language": "hi", 
        "confidence_score": 0.9,
        "model_used": "lightweight_indictrans",
        "processing_time": 0.001,
        "cached": False,
        "detected_language": "en"
    }

@pytest.fixture
def mock_huggingface_model():
    """Mock HuggingFace model for testing without downloading."""
    mock_model = Mock()
    mock_model.generate.return_value = Mock()
    return mock_model

@pytest.fixture
def mock_tokenizer():
    """Mock tokenizer for testing without downloading."""
    mock_tokenizer = Mock()
    mock_tokenizer.encode.return_value = [1, 2, 3, 4, 5]
    mock_tokenizer.decode.return_value = "मॉक अनुवाद"
    mock_tokenizer.batch_encode_plus.return_value = {
        "input_ids": [[1, 2, 3, 4, 5]],
        "attention_mask": [[1, 1, 1, 1, 1]]
    }
    return mock_tokenizer

class MockMLModel:
    """Mock ML model for testing purposes."""
    
    def __init__(self, model_name: str = "test_model"):
        self.model_name = model_name
        self.is_loaded = False
        
    async def load_model(self) -> bool:
        """Mock model loading."""
        await asyncio.sleep(0.001)  # Simulate loading time
        self.is_loaded = True
        return True
        
    async def translate(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """Mock translation."""
        if not self.is_loaded:
            raise RuntimeError("Model not loaded")
            
        # Simulate translation based on input
        mock_translations = {
            ("en", "hi", "hello"): "नमस्ते",
            ("en", "hi", "good morning"): "सुप्रभात", 
            ("en", "hi", "thank you"): "धन्यवाद",
            ("en", "ta", "hello"): "வணக்கம்",
            ("hi", "en", "नमस्ते"): "hello"
        }
        
        translated_text = mock_translations.get(
            (source_lang, target_lang, text.lower()), 
            f"Mock translation of '{text}'"
        )
        
        return {
            "translated_text": translated_text,
            "confidence": 0.9 if (source_lang, target_lang, text.lower()) in mock_translations else 0.6,
            "processing_time": 0.001
        }
        
    def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """Mock language pair support."""
        supported_pairs = [("en", "hi"), ("hi", "en"), ("en", "ta")]
        return (source_lang, target_lang) in supported_pairs

@pytest.fixture
def mock_ml_model():
    """Fixture providing mock ML model."""
    return MockMLModel()

# Performance testing constants
PERFORMANCE_THRESHOLDS = {
    "max_translation_time_ms": 1000,  # 1 second max for translation
    "max_model_loading_time_s": 30,   # 30 seconds max for model loading
    "min_confidence_score": 0.5,      # Minimum acceptable confidence
    "max_memory_usage_mb": 512,       # Max memory per model (512MB)
}

# Error scenarios for testing
ERROR_TEST_CASES = [
    {
        "scenario": "empty_text",
        "text": "",
        "source_lang": "en",
        "target_lang": "hi",
        "expected_error": "Text cannot be empty"
    },
    {
        "scenario": "unsupported_language", 
        "text": "hello",
        "source_lang": "xyz",
        "target_lang": "hi",
        "expected_error": "Unsupported language"
    },
    {
        "scenario": "same_languages",
        "text": "hello", 
        "source_lang": "en",
        "target_lang": "en",
        "expected_error": "Source and target languages cannot be the same"
    },
    {
        "scenario": "invalid_model",
        "text": "hello",
        "source_lang": "en", 
        "target_lang": "hi",
        "model": "nonexistent_model",
        "expected_error": "Model not found"
    }
]
