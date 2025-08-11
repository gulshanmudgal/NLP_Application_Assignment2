from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from .language import SupportedLanguage

class ModelType(str, Enum):
    """Enumeration of available translation models"""
    INDICTRANS = "indictrans"
    MT5 = "mt5"
    AUTO = "auto"

class TranslationRequest(BaseModel):
    """Request model for translation"""
    text: str = Field(..., min_length=1, max_length=1000, description="Text to translate")
    source_language: SupportedLanguage = Field(..., description="Source language code")
    target_language: SupportedLanguage = Field(..., description="Target language code")
    enable_cache: bool = Field(default=True, description="Whether to use cached results")
    model: Optional[str] = Field(default=None, description="Preferred translation model")
    
    @validator('text')
    def validate_text_content(cls, v):
        """Validate text content"""
        v = v.strip()
        if not v:
            raise ValueError('Text cannot be empty or whitespace only')
        return v
    
    @validator('target_language')
    def validate_different_languages(cls, v, values):
        """Ensure source and target languages are different"""
        if 'source_language' in values and v == values['source_language']:
            raise ValueError('Source and target languages must be different')
        return v
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "text": "Hello, how are you?",
                "source_language": "en",
                "target_language": "hi",
                "enable_cache": True,
                "model": "auto"
            }
        }

class TranslationResponse(BaseModel):
    """Response model for translation"""
    translated_text: str = Field(..., description="Translated text")
    source_language: SupportedLanguage = Field(..., description="Source language code")
    target_language: SupportedLanguage = Field(..., description="Target language code")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Translation confidence score")
    model_used: str = Field(..., description="Model used for translation")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")
    cached: bool = Field(..., description="Whether result was retrieved from cache")
    detected_language: Optional[str] = Field(None, description="Auto-detected source language")
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "translated_text": "नमस्ते, आप कैसे हैं?",
                "source_language": "en",
                "target_language": "hi",
                "confidence_score": 0.95,
                "model_used": "mock_translator",
                "processing_time": 0.245,
                "cached": False,
                "detected_language": "en"
            }
        }

class BatchTranslationRequest(BaseModel):
    """Request model for batch translation"""
    requests: List[TranslationRequest] = Field(..., min_items=1, max_items=100, description="List of translation requests")
    
    class Config:
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "text": "Hello",
                        "source_language": "en",
                        "target_language": "hi"
                    },
                    {
                        "text": "Good morning",
                        "source_language": "en",
                        "target_language": "hi"
                    }
                ]
            }
        }

class BatchTranslationResponse(BaseModel):
    """Response model for batch translation"""
    responses: List[TranslationResponse] = Field(..., description="List of translation responses")
    success_count: int = Field(..., description="Number of successful translations")
    error_count: int = Field(..., description="Number of failed translations")
    total_processing_time: float = Field(..., description="Total processing time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "responses": [
                    {
                        "translated_text": "नमस्ते",
                        "source_language": "en",
                        "target_language": "hi",
                        "confidence_score": 0.95,
                        "model_used": "mock_translator",
                        "processing_time": 0.1,
                        "cached": False
                    }
                ],
                "success_count": 1,
                "error_count": 0,
                "total_processing_time": 0.1
            }
        }

class ModelInfo(BaseModel):
    """Information about a translation model"""
    name: str = Field(..., description="Model name")
    source_languages: List[str] = Field(..., description="Supported source languages")
    target_languages: List[str] = Field(..., description="Supported target languages")
    description: str = Field(..., description="Model description")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Information timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TranslationStats(BaseModel):
    """Translation service statistics"""
    total_translations: int = Field(..., description="Total number of translations processed")
    total_cached_translations: int = Field(..., description="Number of cached translations served")
    average_processing_time: float = Field(..., description="Average processing time in seconds")
    supported_language_pairs: int = Field(..., description="Number of supported language pairs")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Statistics timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "error": "Unsupported language pair",
                "details": "Translation from 'xyz' to 'abc' is not supported",
                "code": "UNSUPPORTED_LANGUAGE_PAIR",
                "timestamp": "2025-08-09T10:30:00Z"
            }
        }

class ValidationResult(BaseModel):
    """Model for validation results"""
    is_valid: bool = Field(..., description="Whether the input is valid")
    errors: List[str] = Field(default_factory=list, description="List of validation errors")

class TranslationMetrics(BaseModel):
    """Model for translation service metrics"""
    total_translations: int = Field(..., ge=0, description="Total number of translations")
    average_processing_time: float = Field(..., ge=0.0, description="Average processing time in seconds")
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0, description="Cache hit rate percentage")
    popular_language_pairs: List[dict] = Field(default_factory=list, description="Popular language pairs with counts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_translations": 1500,
                "average_processing_time": 0.325,
                "cache_hit_rate": 0.78,
                "popular_language_pairs": [
                    {"source": "en", "target": "hi", "count": 450},
                    {"source": "hi", "target": "en", "count": 380}
                ]
            }
        }
