"""
Base ML model class for translation models.
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ModelPrediction:
    """Single translation prediction from a model."""
    text: str
    confidence: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass 
class ModelResult:
    """Result from ML model inference."""
    predictions: List[ModelPrediction]
    model_name: str
    model_version: str
    processing_time: float
    input_tokens: int = 0
    output_tokens: int = 0
    
    @property
    def best_prediction(self) -> Optional[ModelPrediction]:
        """Get the prediction with highest confidence."""
        if not self.predictions:
            return None
        return max(self.predictions, key=lambda p: p.confidence)


class BaseMLModel(ABC):
    """Abstract base class for ML translation models."""
    
    def __init__(self, model_name: str, model_path: Optional[str] = None):
        self.model_name = model_name
        self.model_path = model_path
        self.is_loaded = False
        self.load_time = None
        self.model_size_mb = 0
        self.supported_languages = set()
        self._model = None
        self._tokenizer = None
        
    async def load_model(self) -> bool:
        """
        Load the model asynchronously.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        if self.is_loaded:
            return True
            
        start_time = time.time()
        try:
            logger.info(f"Loading model {self.model_name}...")
            success = await self._load_model_impl()
            
            if success:
                self.load_time = time.time() - start_time
                self.is_loaded = True
                logger.info(f"Model {self.model_name} loaded in {self.load_time:.2f}s")
                return True
            else:
                logger.error(f"Failed to load model {self.model_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model {self.model_name}: {e}")
            return False
    
    @abstractmethod
    async def _load_model_impl(self) -> bool:
        """Implementation-specific model loading logic."""
        pass
    
    async def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        **kwargs
    ) -> ModelResult:
        """
        Translate text using the model.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            **kwargs: Additional model-specific parameters
            
        Returns:
            ModelResult with predictions and metadata
        """
        if not self.is_loaded:
            await self.load_model()
            
        if not self.is_loaded:
            raise RuntimeError(f"Model {self.model_name} is not loaded")
            
        if not self.supports_language_pair(source_lang, target_lang):
            raise ValueError(f"Language pair {source_lang}->{target_lang} not supported by {self.model_name}")
        
        start_time = time.time()
        try:
            result = await self._translate_impl(text, source_lang, target_lang, **kwargs)
            result.processing_time = time.time() - start_time
            return result
        except Exception as e:
            logger.error(f"Translation error in {self.model_name}: {e}")
            raise
    
    @abstractmethod
    async def _translate_impl(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        **kwargs
    ) -> ModelResult:
        """Implementation-specific translation logic."""
        pass
    
    def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """Check if the model supports the given language pair."""
        return (source_lang in self.supported_languages and 
                target_lang in self.supported_languages)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and statistics."""
        return {
            "name": self.model_name,
            "path": self.model_path,
            "is_loaded": self.is_loaded,
            "load_time": self.load_time,
            "size_mb": self.model_size_mb,
            "supported_languages": list(self.supported_languages)
        }
    
    async def unload_model(self):
        """Unload the model to free memory."""
        if self.is_loaded:
            try:
                await self._unload_model_impl()
                self.is_loaded = False
                self._model = None
                self._tokenizer = None
                logger.info(f"Model {self.model_name} unloaded")
            except Exception as e:
                logger.error(f"Error unloading model {self.model_name}: {e}")
    
    async def _unload_model_impl(self):
        """Implementation-specific model unloading logic."""
        # Default implementation - can be overridden
        pass
