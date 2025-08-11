"""
Unit tests for ML model components.

Tests the core ML model infrastructure including:
- BaseMLModel abstract class
- ModelLoader for HuggingFace integration
- Individual model implementations (IndicTrans, M2M100, mBART)
- Model prediction and result data structures
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import dataclass
import tempfile
import os
import sys

# Add the backend directory to Python path for imports
sys.path.append('/Users/gullu/Developer/BITS/NLP_App/Assignment_Part_2_V/backend')

from ml_models.inference.base_model import BaseMLModel, ModelPrediction, ModelResult
from ml_models.inference.model_loader import ModelLoader
from ml_models.inference.indictrans_model import IndicTransModel
from ml_models.inference.m2m100_model import M2M100Model 
from ml_models.inference.mbart_model import MBartModel


class TestModelPrediction:
    """Test ModelPrediction dataclass."""
    
    def test_model_prediction_creation(self):
        """Test creating ModelPrediction with valid data."""
        prediction = ModelPrediction(
            translated_text="नमस्ते",
            confidence=0.95,
            processing_time=0.123
        )
        
        assert prediction.translated_text == "नमस्ते"
        assert prediction.confidence == 0.95
        assert prediction.processing_time == 0.123
        
    def test_model_prediction_validation(self):
        """Test ModelPrediction validation constraints."""
        # Valid confidence range
        prediction = ModelPrediction("test", 0.5, 0.1)
        assert prediction.confidence == 0.5
        
        # Test edge cases
        prediction_low = ModelPrediction("test", 0.0, 0.1)
        assert prediction_low.confidence == 0.0
        
        prediction_high = ModelPrediction("test", 1.0, 0.1)
        assert prediction_high.confidence == 1.0


class TestModelResult:
    """Test ModelResult dataclass."""
    
    def test_model_result_creation(self):
        """Test creating ModelResult with predictions."""
        predictions = [
            ModelPrediction("नमस्ते", 0.9, 0.1),
            ModelPrediction("हैलो", 0.7, 0.1)
        ]
        
        result = ModelResult(
            predictions=predictions,
            model_name="test_model",
            source_language="en",
            target_language="hi"
        )
        
        assert len(result.predictions) == 2
        assert result.model_name == "test_model"
        assert result.source_language == "en"
        assert result.target_language == "hi"
        
    def test_best_prediction_property(self):
        """Test best_prediction property returns highest confidence."""
        predictions = [
            ModelPrediction("हैलो", 0.7, 0.1),
            ModelPrediction("नमस्ते", 0.9, 0.1),  # Best
            ModelPrediction("नमस्कार", 0.8, 0.1)
        ]
        
        result = ModelResult(predictions, "test", "en", "hi")
        best = result.best_prediction
        
        assert best.translated_text == "नमस्ते"
        assert best.confidence == 0.9


class TestBaseMLModel:
    """Test BaseMLModel abstract class."""
    
    def test_base_model_is_abstract(self):
        """Test that BaseMLModel cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseMLModel()
            
    def test_concrete_implementation(self):
        """Test concrete implementation of BaseMLModel."""
        
        class TestModel(BaseMLModel):
            def __init__(self):
                super().__init__("test_model", "Test Model for Testing")
                
            async def _load_model_impl(self) -> bool:
                await asyncio.sleep(0.001)
                return True
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> ModelPrediction:
                return ModelPrediction("test translation", 0.8, 0.001)
                
            def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
                return source_lang == "en" and target_lang == "hi"
        
        model = TestModel()
        assert model.model_name == "test_model"
        assert model.description == "Test Model for Testing"
        assert not model.is_loaded
        
    @pytest.mark.asyncio
    async def test_model_loading_lifecycle(self):
        """Test model loading and lifecycle management."""
        
        class TestModel(BaseMLModel):
            def __init__(self):
                super().__init__("test_model", "Test Model")
                self.load_called = False
                
            async def _load_model_impl(self) -> bool:
                self.load_called = True
                await asyncio.sleep(0.001)
                return True
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> ModelPrediction:
                return ModelPrediction("test", 0.8, 0.001)
                
            def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
                return True
        
        model = TestModel()
        
        # Initially not loaded
        assert not model.is_loaded
        assert not model.load_called
        
        # Load model
        success = await model.load_model()
        assert success
        assert model.is_loaded
        assert model.load_called
        
        # Subsequent loads should not call _load_model_impl again
        model.load_called = False
        await model.load_model()
        assert not model.load_called  # Should not reload
        
    @pytest.mark.asyncio
    async def test_translation_requires_loaded_model(self):
        """Test that translation requires model to be loaded."""
        
        class TestModel(BaseMLModel):
            def __init__(self):
                super().__init__("test_model", "Test Model")
                
            async def _load_model_impl(self) -> bool:
                return True
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> ModelPrediction:
                return ModelPrediction("test", 0.8, 0.001)
                
            def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
                return True
        
        model = TestModel()
        
        # Translation should fail if model not loaded
        with pytest.raises(RuntimeError, match="Model not loaded"):
            await model.translate("hello", "en", "hi")
            
        # Load model and try again
        await model.load_model()
        result = await model.translate("hello", "en", "hi")
        assert isinstance(result, ModelResult)


class TestModelLoader:
    """Test ModelLoader for HuggingFace integration."""
    
    def test_model_loader_initialization(self, temp_model_cache):
        """Test ModelLoader initialization with cache directory."""
        loader = ModelLoader(cache_dir=temp_model_cache)
        assert loader.cache_dir == temp_model_cache
        assert os.path.exists(temp_model_cache)
        
    @patch('ml_models.inference.model_loader.AutoTokenizer')
    @patch('ml_models.inference.model_loader.AutoModelForSeq2SeqLM')
    def test_load_model_from_cache(self, mock_model_class, mock_tokenizer_class, temp_model_cache):
        """Test loading model from cache."""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        
        loader = ModelLoader(cache_dir=temp_model_cache)
        
        # Load model
        model, tokenizer = loader.load_model("test/model")
        
        assert model == mock_model
        assert tokenizer == mock_tokenizer
        
        # Verify correct calls
        mock_model_class.from_pretrained.assert_called_once()
        mock_tokenizer_class.from_pretrained.assert_called_once()
        
    def test_ensure_model_cached(self, temp_model_cache):
        """Test model caching functionality."""
        loader = ModelLoader(cache_dir=temp_model_cache)
        
        # Create a fake model directory
        model_name = "test/model"
        model_path = os.path.join(temp_model_cache, model_name.replace("/", "_"))
        os.makedirs(model_path, exist_ok=True)
        
        # Create some fake model files
        with open(os.path.join(model_path, "config.json"), "w") as f:
            f.write('{"model_type": "test"}')
            
        # Test cache checking
        cached_path = loader._ensure_model_cached(model_name)
        assert cached_path == model_path
        assert os.path.exists(cached_path)


class TestIndicTransModel:
    """Test IndicTransModel implementation."""
    
    def test_indictrans_initialization(self):
        """Test IndicTransModel initialization."""
        model = IndicTransModel()
        assert model.model_name == "indictrans"
        assert "IndicTrans" in model.description
        assert not model.is_loaded
        
    def test_language_pair_support(self):
        """Test IndicTrans language pair support."""
        model = IndicTransModel()
        
        # Supported pairs
        assert model.supports_language_pair("en", "hi")
        assert model.supports_language_pair("hi", "en")
        assert model.supports_language_pair("en", "ta")
        assert model.supports_language_pair("en", "te")
        
        # Unsupported pairs
        assert not model.supports_language_pair("en", "fr")  # French not supported
        assert not model.supports_language_pair("hi", "ta")  # Cross-Indic not supported
        assert not model.supports_language_pair("en", "en")  # Same language
        
    def test_language_code_mapping(self):
        """Test language code mapping for IndicTrans."""
        model = IndicTransModel()
        
        # Test internal language mapping
        assert hasattr(model, '_get_indictrans_lang_code')
        
        # English mappings
        assert model._get_indictrans_lang_code("en") == "en"
        
        # Hindi mappings
        assert model._get_indictrans_lang_code("hi") == "hi"
        
        # Other Indian languages
        assert model._get_indictrans_lang_code("ta") == "ta"
        assert model._get_indictrans_lang_code("te") == "te"
        assert model._get_indictrans_lang_code("bn") == "bn"


class TestM2M100Model:
    """Test M2M100Model implementation."""
    
    def test_m2m100_initialization(self):
        """Test M2M100Model initialization."""
        model = M2M100Model()
        assert model.model_name == "m2m100"
        assert "M2M100" in model.description
        assert not model.is_loaded
        
    def test_language_pair_support(self):
        """Test M2M100 language pair support (broader than IndicTrans)."""
        model = M2M100Model()
        
        # Should support more language pairs than IndicTrans
        assert model.supports_language_pair("en", "hi")
        assert model.supports_language_pair("en", "fr")  # Should support French
        assert model.supports_language_pair("en", "es")  # Should support Spanish
        assert model.supports_language_pair("hi", "ta")  # Should support cross-Indic
        
        # Should not support same language
        assert not model.supports_language_pair("en", "en")


class TestMBartModel:
    """Test MBartModel implementation."""
    
    def test_mbart_initialization(self):
        """Test MBartModel initialization."""
        model = MBartModel()
        assert model.model_name == "mbart"
        assert "mBART" in model.description
        assert not model.is_loaded
        
    def test_language_pair_support(self):
        """Test mBART language pair support."""
        model = MBartModel()
        
        # Should support multilingual translation
        assert model.supports_language_pair("en", "hi")
        assert model.supports_language_pair("en", "ar")  # Should support Arabic
        assert model.supports_language_pair("hi", "en")
        
        # Should not support same language
        assert not model.supports_language_pair("en", "en")


class TestModelIntegration:
    """Integration tests for model components working together."""
    
    @pytest.mark.asyncio
    async def test_model_loading_error_handling(self):
        """Test error handling during model loading."""
        
        class FailingModel(BaseMLModel):
            def __init__(self):
                super().__init__("failing_model", "Model that fails to load")
                
            async def _load_model_impl(self) -> bool:
                # Simulate loading failure
                raise Exception("Failed to load model")
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> ModelPrediction:
                return ModelPrediction("test", 0.8, 0.001)
                
            def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
                return True
        
        model = FailingModel()
        
        # Loading should handle errors gracefully
        success = await model.load_model()
        assert not success
        assert not model.is_loaded
        
    @pytest.mark.asyncio 
    async def test_translation_error_handling(self):
        """Test error handling during translation."""
        
        class TranslationFailingModel(BaseMLModel):
            def __init__(self):
                super().__init__("translation_failing_model", "Model that fails translation")
                
            async def _load_model_impl(self) -> bool:
                return True
                
            async def _translate_impl(self, text: str, source_lang: str, target_lang: str) -> ModelPrediction:
                raise Exception("Translation failed")
                
            def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
                return True
        
        model = TranslationFailingModel()
        await model.load_model()
        
        # Translation should handle errors gracefully
        with pytest.raises(Exception, match="Translation failed"):
            await model.translate("hello", "en", "hi")
            
    def test_all_models_implement_interface(self):
        """Test that all model implementations properly implement BaseMLModel."""
        models = [IndicTransModel(), M2M100Model(), MBartModel()]
        
        for model in models:
            # Check required attributes
            assert hasattr(model, 'model_name')
            assert hasattr(model, 'description')
            assert hasattr(model, 'is_loaded')
            
            # Check required methods
            assert hasattr(model, 'load_model')
            assert hasattr(model, 'translate')
            assert hasattr(model, 'supports_language_pair')
            
            # Check abstract methods are implemented
            assert hasattr(model, '_load_model_impl')
            assert hasattr(model, '_translate_impl')
            
            # Test language pair support method works
            result = model.supports_language_pair("en", "hi")
            assert isinstance(result, bool)
