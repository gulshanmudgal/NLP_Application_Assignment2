import pytest
from datetime import datetime
from pydantic import ValidationError
from app.models.translation import (
    TranslationRequest,
    TranslationResult,
    TranslationResponse,
    ErrorResponse,
    TranslationHistoryItem,
    ValidationResult,
    TranslationMetrics,
    ModelType
)
from app.models.language import SupportedLanguage

class TestModelType:
    """Test ModelType enum"""
    
    def test_model_type_values(self):
        """Test that all model types have correct values"""
        assert ModelType.INDICTRANS == "indictrans"
        assert ModelType.MT5 == "mt5"
        assert ModelType.AUTO == "auto"

class TestTranslationRequest:
    """Test TranslationRequest model validation"""
    
    def test_valid_translation_request(self):
        """Test creating a valid translation request"""
        request = TranslationRequest(
            text="Hello world",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            enable_cache=True,
            model=ModelType.INDICTRANS
        )
        
        assert request.text == "Hello world"
        assert request.source_language == SupportedLanguage.ENGLISH
        assert request.target_language == SupportedLanguage.HINDI
        assert request.enable_cache is True
        assert request.model == ModelType.INDICTRANS
    
    def test_translation_request_defaults(self):
        """Test translation request with default values"""
        request = TranslationRequest(
            text="Hello world",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI
        )
        
        # Should have default values
        assert request.enable_cache is True
        assert request.model == ModelType.AUTO
    
    def test_empty_text_validation(self):
        """Test that empty text raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(
                text="",
                source_language=SupportedLanguage.ENGLISH,
                target_language=SupportedLanguage.HINDI
            )
        
        assert "Text cannot be empty" in str(exc_info.value)
    
    def test_whitespace_only_text_validation(self):
        """Test that whitespace-only text raises ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(
                text="   \n\t   ",
                source_language=SupportedLanguage.ENGLISH,
                target_language=SupportedLanguage.HINDI
            )
        
        assert "Text cannot be empty" in str(exc_info.value)
    
    def test_text_length_validation(self):
        """Test text length validation"""
        # Text too long
        long_text = "a" * 1001
        with pytest.raises(ValidationError):
            TranslationRequest(
                text=long_text,
                source_language=SupportedLanguage.ENGLISH,
                target_language=SupportedLanguage.HINDI
            )
    
    def test_same_source_target_validation(self):
        """Test that same source and target languages raise ValidationError"""
        with pytest.raises(ValidationError) as exc_info:
            TranslationRequest(
                text="Hello world",
                source_language=SupportedLanguage.ENGLISH,
                target_language=SupportedLanguage.ENGLISH
            )
        
        assert "Source and target languages must be different" in str(exc_info.value)
    
    def test_text_strip_validation(self):
        """Test that text is properly stripped"""
        request = TranslationRequest(
            text="  Hello world  ",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI
        )
        
        assert request.text == "Hello world"

class TestTranslationResult:
    """Test TranslationResult model"""
    
    def test_valid_translation_result(self):
        """Test creating a valid translation result"""
        result = TranslationResult(
            translated_text="नमस्ते संसार",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            confidence=0.95,
            model="indictrans",
            processing_time=0.245,
            from_cache=False,
            alternatives=["हैलो वर्ल्ड"]
        )
        
        assert result.translated_text == "नमस्ते संसार"
        assert result.source_language == SupportedLanguage.ENGLISH
        assert result.target_language == SupportedLanguage.HINDI
        assert result.confidence == 0.95
        assert result.model == "indictrans"
        assert result.processing_time == 0.245
        assert result.from_cache is False
        assert result.alternatives == ["हैलो वर्ल्ड"]
    
    def test_translation_result_without_optional_fields(self):
        """Test translation result without optional fields"""
        result = TranslationResult(
            translated_text="नमस्ते संसार",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            model="indictrans",
            processing_time=0.245,
            from_cache=False
        )
        
        assert result.confidence is None
        assert result.alternatives is None
    
    def test_confidence_range_validation(self):
        """Test confidence score range validation"""
        # Valid confidence scores
        result = TranslationResult(
            translated_text="Test",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            confidence=0.5,
            model="test",
            processing_time=1.0,
            from_cache=False
        )
        assert result.confidence == 0.5
        
        # Invalid confidence scores
        with pytest.raises(ValidationError):
            TranslationResult(
                translated_text="Test",
                source_language=SupportedLanguage.ENGLISH,
                target_language=SupportedLanguage.HINDI,
                confidence=1.5,  # Too high
                model="test",
                processing_time=1.0,
                from_cache=False
            )
        
        with pytest.raises(ValidationError):
            TranslationResult(
                translated_text="Test",
                source_language=SupportedLanguage.ENGLISH,
                target_language=SupportedLanguage.HINDI,
                confidence=-0.1,  # Too low
                model="test",
                processing_time=1.0,
                from_cache=False
            )
    
    def test_processing_time_validation(self):
        """Test processing time validation"""
        # Valid processing time
        result = TranslationResult(
            translated_text="Test",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            model="test",
            processing_time=0.0,
            from_cache=False
        )
        assert result.processing_time == 0.0
        
        # Invalid processing time
        with pytest.raises(ValidationError):
            TranslationResult(
                translated_text="Test",
                source_language=SupportedLanguage.ENGLISH,
                target_language=SupportedLanguage.HINDI,
                model="test",
                processing_time=-1.0,  # Negative
                from_cache=False
            )

class TestTranslationResponse:
    """Test TranslationResponse model"""
    
    def test_successful_translation_response(self):
        """Test successful translation response"""
        result = TranslationResult(
            translated_text="Test",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            model="test",
            processing_time=1.0,
            from_cache=False
        )
        
        response = TranslationResponse(
            success=True,
            data=result,
            message="Translation successful"
        )
        
        assert response.success is True
        assert response.data == result
        assert response.error is None
        assert response.message == "Translation successful"
        assert isinstance(response.timestamp, datetime)
    
    def test_error_translation_response(self):
        """Test error translation response"""
        response = TranslationResponse(
            success=False,
            error="Translation failed",
            message="Internal server error"
        )
        
        assert response.success is False
        assert response.data is None
        assert response.error == "Translation failed"
        assert response.message == "Internal server error"

class TestErrorResponse:
    """Test ErrorResponse model"""
    
    def test_basic_error_response(self):
        """Test basic error response"""
        error = ErrorResponse(
            error="Validation failed",
            details="Text is too long",
            code="VALIDATION_ERROR"
        )
        
        assert error.error == "Validation failed"
        assert error.details == "Text is too long"
        assert error.code == "VALIDATION_ERROR"
        assert isinstance(error.timestamp, datetime)
    
    def test_error_response_without_optional_fields(self):
        """Test error response without optional fields"""
        error = ErrorResponse(error="Something went wrong")
        
        assert error.error == "Something went wrong"
        assert error.details is None
        assert error.code is None

class TestValidationResult:
    """Test ValidationResult model"""
    
    def test_valid_validation_result(self):
        """Test valid validation result"""
        result = ValidationResult(is_valid=True, errors=[])
        
        assert result.is_valid is True
        assert result.errors == []
    
    def test_invalid_validation_result(self):
        """Test invalid validation result with errors"""
        errors = ["Text is empty", "Invalid language code"]
        result = ValidationResult(is_valid=False, errors=errors)
        
        assert result.is_valid is False
        assert result.errors == errors
    
    def test_validation_result_defaults(self):
        """Test validation result with defaults"""
        result = ValidationResult(is_valid=True)
        
        assert result.errors == []

class TestTranslationMetrics:
    """Test TranslationMetrics model"""
    
    def test_valid_translation_metrics(self):
        """Test valid translation metrics"""
        popular_pairs = [
            {"source": "en", "target": "hi", "count": 100},
            {"source": "hi", "target": "en", "count": 80}
        ]
        
        metrics = TranslationMetrics(
            total_translations=1000,
            average_processing_time=0.5,
            cache_hit_rate=0.75,
            popular_language_pairs=popular_pairs
        )
        
        assert metrics.total_translations == 1000
        assert metrics.average_processing_time == 0.5
        assert metrics.cache_hit_rate == 0.75
        assert metrics.popular_language_pairs == popular_pairs
    
    def test_metrics_validation_ranges(self):
        """Test metrics validation ranges"""
        # Valid ranges
        metrics = TranslationMetrics(
            total_translations=0,
            average_processing_time=0.0,
            cache_hit_rate=1.0
        )
        assert metrics.total_translations == 0
        assert metrics.cache_hit_rate == 1.0
        
        # Invalid ranges
        with pytest.raises(ValidationError):
            TranslationMetrics(
                total_translations=-1,  # Negative
                average_processing_time=0.5,
                cache_hit_rate=0.75
            )
        
        with pytest.raises(ValidationError):
            TranslationMetrics(
                total_translations=100,
                average_processing_time=-0.1,  # Negative
                cache_hit_rate=0.75
            )
        
        with pytest.raises(ValidationError):
            TranslationMetrics(
                total_translations=100,
                average_processing_time=0.5,
                cache_hit_rate=1.5  # > 1.0
            )

class TestTranslationHistoryItem:
    """Test TranslationHistoryItem model"""
    
    def test_valid_history_item(self):
        """Test valid translation history item"""
        request = TranslationRequest(
            text="Hello",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI
        )
        
        result = TranslationResult(
            translated_text="नमस्ते",
            source_language=SupportedLanguage.ENGLISH,
            target_language=SupportedLanguage.HINDI,
            model="test",
            processing_time=1.0,
            from_cache=False
        )
        
        history_item = TranslationHistoryItem(
            id="12345",
            request=request,
            result=result
        )
        
        assert history_item.id == "12345"
        assert history_item.request == request
        assert history_item.result == result
        assert isinstance(history_item.timestamp, datetime)
