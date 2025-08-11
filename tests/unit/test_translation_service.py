"""
Unit tests for translation service components.

Tests the translation service layer including:
- ML translator integrations
- Translation service orchestration
- Cache integration
- Model selection and fallback logic
- Performance monitoring
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import sys
import time

# Add the backend directory to Python path for imports
sys.path.append('/Users/gullu/Developer/BITS/NLP_App/Assignment_Part_2_V/backend')

from app.services.ml_translators import MLModelTranslator, LightweightIndicTransTranslator
from app.services.translation_service import TranslationService
from app.models.translation import TranslationRequest, TranslationResponse


class TestMLModelTranslator:
    """Test MLModelTranslator base class."""
    
    def test_ml_model_translator_initialization(self):
        """Test MLModelTranslator initialization."""
        
        class TestMLTranslator(MLModelTranslator):
            def __init__(self):
                super().__init__("test_translator", "Test ML Translator")
                
            async def _initialize_impl(self) -> bool:
                return True
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> dict:
                return {
                    "translated_text": f"Translated: {text}",
                    "confidence": 0.9,
                    "processing_time": 0.001
                }
                
            def _supports_language_pair_impl(self, source_lang: str, target_lang: str) -> bool:
                return source_lang == "en" and target_lang == "hi"
        
        translator = TestMLTranslator()
        assert translator.name == "test_translator"
        assert translator.description == "Test ML Translator"
        assert not translator.is_initialized
        
    @pytest.mark.asyncio
    async def test_ml_translator_lifecycle(self):
        """Test ML translator initialization and usage lifecycle."""
        
        class TestMLTranslator(MLModelTranslator):
            def __init__(self):
                super().__init__("test_translator", "Test ML Translator")
                self.init_called = False
                
            async def _initialize_impl(self) -> bool:
                self.init_called = True
                await asyncio.sleep(0.001)
                return True
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> dict:
                return {
                    "translated_text": f"Translated: {text}",
                    "confidence": 0.9,
                    "processing_time": 0.001
                }
                
            def _supports_language_pair_impl(self, source_lang: str, target_lang: str) -> bool:
                return True
        
        translator = TestMLTranslator()
        
        # Initially not initialized
        assert not translator.is_initialized
        assert not translator.init_called
        
        # Initialize
        success = await translator.initialize()
        assert success
        assert translator.is_initialized
        assert translator.init_called
        
        # Subsequent initializations should not call _initialize_impl again
        translator.init_called = False
        await translator.initialize()
        assert not translator.init_called
        
    @pytest.mark.asyncio
    async def test_translation_requires_initialization(self):
        """Test that translation requires initialization."""
        
        class TestMLTranslator(MLModelTranslator):
            def __init__(self):
                super().__init__("test_translator", "Test ML Translator")
                
            async def _initialize_impl(self) -> bool:
                return True
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> dict:
                return {
                    "translated_text": f"Translated: {text}",
                    "confidence": 0.9,
                    "processing_time": 0.001
                }
                
            def _supports_language_pair_impl(self, source_lang: str, target_lang: str) -> bool:
                return True
        
        translator = TestMLTranslator()
        
        # Translation should fail if not initialized
        with pytest.raises(RuntimeError, match="Translator not initialized"):
            await translator.translate("hello", "en", "hi")
            
        # Initialize and try again
        await translator.initialize()
        result = await translator.translate("hello", "en", "hi")
        assert result["translated_text"] == "Translated: hello"


class TestLightweightIndicTransTranslator:
    """Test LightweightIndicTransTranslator implementation."""
    
    def test_lightweight_translator_initialization(self):
        """Test lightweight translator initialization."""
        translator = LightweightIndicTransTranslator()
        assert translator.name == "lightweight_indictrans"
        assert "Lightweight" in translator.description
        assert "IndicTrans" in translator.description
        
    @pytest.mark.asyncio
    async def test_lightweight_translator_initialize(self):
        """Test lightweight translator initialization (should be fast)."""
        translator = LightweightIndicTransTranslator()
        
        start_time = time.time()
        success = await translator.initialize()
        init_time = time.time() - start_time
        
        assert success
        assert translator.is_initialized
        assert init_time < 0.1  # Should initialize very quickly
        
    def test_language_pair_support(self):
        """Test language pair support for lightweight translator."""
        translator = LightweightIndicTransTranslator()
        
        # Should support basic English-Hindi pairs
        assert translator.supports_language_pair("en", "hi")
        assert translator.supports_language_pair("hi", "en")
        
        # May have limited support for other languages
        # (depending on implementation)
        
    @pytest.mark.asyncio
    async def test_basic_translation(self):
        """Test basic translation functionality."""
        translator = LightweightIndicTransTranslator()
        await translator.initialize()
        
        # Test known translations
        result = await translator.translate("hello", "en", "hi")
        
        assert "translated_text" in result
        assert "confidence" in result
        assert "processing_time" in result
        assert isinstance(result["confidence"], (int, float))
        assert isinstance(result["processing_time"], (int, float))
        
        # For lightweight translator, should be fast
        assert result["processing_time"] < 0.1
        
    @pytest.mark.asyncio
    async def test_fallback_behavior(self):
        """Test fallback behavior for unsupported translations."""
        translator = LightweightIndicTransTranslator()
        await translator.initialize()
        
        # Test with potentially unsupported language pair
        result = await translator.translate("hello", "en", "xyz")
        
        # Should return something (even if just the original text)
        assert "translated_text" in result
        assert result["translated_text"] is not None


class TestTranslationService:
    """Test TranslationService orchestration."""
    
    @patch('app.services.translation_service.LightweightIndicTransTranslator')
    def test_translation_service_initialization(self, mock_lightweight_class):
        """Test translation service initialization with mocked dependencies."""
        # Setup mock
        mock_translator = AsyncMock()
        mock_translator.initialize.return_value = True
        mock_lightweight_class.return_value = mock_translator
        
        # Create service (this will call _initialize_models)
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            assert hasattr(service, 'models')
            
    @pytest.mark.asyncio
    async def test_model_selection_priority(self):
        """Test model selection based on priority and availability."""
        
        # Create mock models with different capabilities
        mock_lightweight = AsyncMock()
        mock_lightweight.name = "lightweight_indictrans"
        mock_lightweight.is_initialized = True
        mock_lightweight.supports_language_pair.return_value = True
        mock_lightweight.translate.return_value = {
            "translated_text": "नमस्ते",
            "confidence": 0.9,
            "processing_time": 0.001
        }
        
        mock_heavy = AsyncMock()
        mock_heavy.name = "indictrans"
        mock_heavy.is_initialized = False  # Not available
        mock_heavy.supports_language_pair.return_value = True
        
        mock_mock = AsyncMock()
        mock_mock.name = "mock"
        mock_mock.is_initialized = True
        mock_mock.supports_language_pair.return_value = True
        mock_mock.translate.return_value = {
            "translated_text": "मॉक अनुवाद: hello",
            "confidence": 0.75,
            "processing_time": 0.1
        }
        
        # Create service with mocked models
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            service.models = {
                "lightweight_indictrans": mock_lightweight,
                "indictrans": mock_heavy,
                "mock": mock_mock
            }
            service.model_priority = ["lightweight_indictrans", "indictrans", "mock"]
            
            # Test model selection for "auto"
            selected_model = service._select_model("auto", "en", "hi")
            assert selected_model.name == "lightweight_indictrans"  # Should prefer available lightweight
            
    @pytest.mark.asyncio  
    async def test_translation_with_caching(self):
        """Test translation with cache integration."""
        
        # Mock cache service
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None  # Cache miss first time
        mock_cache.set.return_value = True
        
        # Mock translator
        mock_translator = AsyncMock()
        mock_translator.name = "test_translator"
        mock_translator.is_initialized = True
        mock_translator.supports_language_pair.return_value = True
        mock_translator.translate.return_value = {
            "translated_text": "नमस्ते",
            "confidence": 0.9,
            "processing_time": 0.001
        }
        
        # Create service with mocks
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            service.models = {"test_translator": mock_translator}
            service.cache_service = mock_cache
            
            request = TranslationRequest(
                text="hello",
                source_language="en",
                target_language="hi",
                model="test_translator"
            )
            
            # First call - should hit translator and cache result
            response = await service.translate(request)
            
            assert response.translated_text == "नमस्ते"
            assert response.model_used == "test_translator"
            assert not response.cached
            
            # Verify cache was called
            mock_cache.get.assert_called()
            mock_cache.set.assert_called()
            
    @pytest.mark.asyncio
    async def test_unsupported_language_pair_fallback(self):
        """Test fallback behavior for unsupported language pairs."""
        
        # Mock translator that doesn't support the language pair
        mock_translator = AsyncMock()
        mock_translator.name = "limited_translator"
        mock_translator.is_initialized = True
        mock_translator.supports_language_pair.return_value = False
        
        # Mock fallback translator
        mock_fallback = AsyncMock()
        mock_fallback.name = "mock"
        mock_fallback.is_initialized = True
        mock_fallback.supports_language_pair.return_value = True
        mock_fallback.translate.return_value = {
            "translated_text": "Fallback translation",
            "confidence": 0.6,
            "processing_time": 0.1
        }
        
        # Create service
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            service.models = {
                "limited_translator": mock_translator,
                "mock": mock_fallback
            }
            service.model_priority = ["limited_translator", "mock"]
            
            request = TranslationRequest(
                text="hello",
                source_language="en",
                target_language="xyz",  # Unsupported language
                model="auto"
            )
            
            # Should fallback to mock translator
            with patch.object(service, 'cache_service', AsyncMock()):
                service.cache_service.get.return_value = None
                response = await service.translate(request)
            
            assert response.translated_text == "Fallback translation"
            assert response.model_used == "mock"
            
    @pytest.mark.asyncio
    async def test_error_handling_in_translation(self):
        """Test error handling during translation process."""
        
        # Mock translator that raises exception
        mock_translator = AsyncMock()
        mock_translator.name = "failing_translator"
        mock_translator.is_initialized = True
        mock_translator.supports_language_pair.return_value = True
        mock_translator.translate.side_effect = Exception("Translation failed")
        
        # Create service
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            service.models = {"failing_translator": mock_translator}
            
            request = TranslationRequest(
                text="hello",
                source_language="en", 
                target_language="hi",
                model="failing_translator"
            )
            
            # Should handle error gracefully
            with patch.object(service, 'cache_service', AsyncMock()):
                service.cache_service.get.return_value = None
                with pytest.raises(Exception):
                    await service.translate(request)
                    
    def test_language_pair_validation(self):
        """Test language pair validation."""
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            
            # Test valid language pairs
            assert service._is_valid_language_pair("en", "hi")
            assert service._is_valid_language_pair("hi", "en")
            
            # Test invalid language pairs
            assert not service._is_valid_language_pair("en", "en")  # Same language
            assert not service._is_valid_language_pair("", "hi")    # Empty source
            assert not service._is_valid_language_pair("en", "")    # Empty target
            
    def test_get_available_models(self):
        """Test getting list of available models."""
        mock_model1 = Mock()
        mock_model1.name = "model1"
        mock_model1.is_initialized = True
        
        mock_model2 = Mock()
        mock_model2.name = "model2"
        mock_model2.is_initialized = False
        
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            service.models = {
                "model1": mock_model1,
                "model2": mock_model2
            }
            
            # Should return only initialized models
            available = service.get_available_models()
            assert "model1" in available
            assert "model2" not in available


class TestPerformanceMetrics:
    """Test performance monitoring and metrics."""
    
    @pytest.mark.asyncio
    async def test_translation_timing(self):
        """Test that translation timing is tracked correctly."""
        
        # Mock translator with controlled timing
        mock_translator = AsyncMock()
        mock_translator.name = "timed_translator"
        mock_translator.is_initialized = True
        mock_translator.supports_language_pair.return_value = True
        
        async def slow_translate(*args, **kwargs):
            await asyncio.sleep(0.1)  # Simulate 100ms translation
            return {
                "translated_text": "Slow translation",
                "confidence": 0.8,
                "processing_time": 0.1
            }
            
        mock_translator.translate.side_effect = slow_translate
        
        # Create service
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            service.models = {"timed_translator": mock_translator}
            
            request = TranslationRequest(
                text="hello",
                source_language="en",
                target_language="hi", 
                model="timed_translator"
            )
            
            with patch.object(service, 'cache_service', AsyncMock()):
                service.cache_service.get.return_value = None
                
                start_time = time.time()
                response = await service.translate(request)
                total_time = time.time() - start_time
                
                # Should track timing accurately
                assert response.processing_time >= 0.05  # At least some of the sleep time
                assert total_time >= 0.1  # Total time should include the sleep
                
    def test_confidence_score_validation(self):
        """Test confidence score validation and normalization."""
        
        test_cases = [
            (0.0, 0.0),    # Minimum valid
            (0.5, 0.5),    # Normal case
            (1.0, 1.0),    # Maximum valid
            (-0.1, 0.0),   # Should clamp to 0
            (1.5, 1.0),    # Should clamp to 1
        ]
        
        with patch.object(TranslationService, '_initialize_models'):
            service = TranslationService()
            
            for input_confidence, expected in test_cases:
                normalized = service._normalize_confidence(input_confidence)
                assert normalized == expected
