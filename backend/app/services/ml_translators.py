"""
Real ML model translator implementations.
"""
import asyncio
import time
from typing import Optional
import logging

# Add the ml_models directory to the path
import sys
from pathlib import Path
ml_models_path = Path(__file__).parent.parent.parent / "ml_models"
sys.path.append(str(ml_models_path))

try:
    from ml_models.inference.model_loader import ModelLoader
    from ml_models.inference.indictrans_model import IndicTransModel
    from ml_models.inference.m2m100_model import M2M100Model
    from ml_models.inference.mbart_model import MBartModel
    ML_MODELS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"ML models not available: {e}")
    ML_MODELS_AVAILABLE = False

from app.services.translation_service import BaseTranslator, TranslationResult

logger = logging.getLogger(__name__)


class MLModelTranslator(BaseTranslator):
    """Base class for ML model-based translators."""
    
    def __init__(self, model_type: str, model_class=None):
        super().__init__()
        self.model_type = model_type
        self.model_class = model_class
        self.model_loader = None
        self.model = None
        self.is_loaded = False
        
    async def initialize(self):
        """Initialize the ML model."""
        if not ML_MODELS_AVAILABLE:
            raise RuntimeError("ML models are not available")
            
        try:
            self.model_loader = ModelLoader()
            self.model = await self.model_loader.load_model(
                self.model_type, 
                self.model_class
            )
            
            if self.model:
                self.is_loaded = True
                logger.info(f"Initialized {self.model_type} translator")
            else:
                raise RuntimeError(f"Failed to load {self.model_type} model")
                
        except Exception as e:
            logger.error(f"Failed to initialize {self.model_type} translator: {e}")
            raise
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate using the ML model."""
        if not self.is_loaded:
            await self.initialize()
            
        if not self.model:
            raise RuntimeError(f"{self.model_type} model not loaded")
            
        try:
            # Use the ML model for translation
            result = await self.model.translate(text, source_lang, target_lang)
            
            # Convert ML model result to TranslationResult
            best_prediction = result.best_prediction
            if not best_prediction:
                raise RuntimeError("No translation predictions generated")
                
            return TranslationResult(
                translated_text=best_prediction.text,
                confidence=best_prediction.confidence,
                model_used=self.model_type,
                detected_language=None,
                alternatives=[]
            )
            
        except Exception as e:
            logger.error(f"Translation error in {self.model_type}: {e}")
            # Fallback to basic translation on error
            return await self._fallback_translate(text, source_lang, target_lang)
    
    async def _fallback_translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Fallback translation when ML model fails."""
        return TranslationResult(
            translated_text=f"[{self.model_type} failed] {text}",
            confidence=0.1,
            model_used=f"{self.model_type}_fallback",
            detected_language=source_lang,
            alternatives=[]
        )


class IndicTransTranslator(MLModelTranslator):
    """IndicTrans translator for Indian languages."""
    
    def __init__(self):
        super().__init__("indictrans", IndicTransModel if ML_MODELS_AVAILABLE else None)
        self.description = "IndicTrans for English-Indian language translation"


class M2M100Translator(MLModelTranslator):
    """M2M100 translator for multilingual translation."""
    
    def __init__(self):
        super().__init__("m2m100", M2M100Model if ML_MODELS_AVAILABLE else None)
        self.description = "M2M100 for many-to-many multilingual translation"


class MBartTranslator(MLModelTranslator):
    """mBART translator for multilingual translation."""
    
    def __init__(self):
        super().__init__("mbart", MBartModel if ML_MODELS_AVAILABLE else None)
        self.description = "mBART for multilingual translation"


# Lightweight fallback translators that work without heavy ML dependencies
class LightweightIndicTransTranslator(BaseTranslator):
    """Lightweight IndicTrans translator using a basic approach."""
    
    def __init__(self):
        super().__init__()
        self.description = "Lightweight IndicTrans fallback"
        
        # Basic translation dictionary for common phrases
        self.translations = {
            ("en", "hi"): {
                "hello": "नमस्ते",
                "hello world": "नमस्ते संसार",
                "good morning": "सुप्रभात",
                "good evening": "शुभ संध्या",
                "thank you": "धन्यवाद",
                "how are you": "आप कैसे हैं",
                "what is your name": "आपका नाम क्या है",
                "nice to meet you": "आपसे मिलकर खुशी हुई",
                "goodbye": "अलविदा",
                "yes": "हाँ",
                "no": "नहीं",
                "please": "कृपया",
                "sorry": "माफ़ करें",
                "welcome": "स्वागत है"
            },
            ("hi", "en"): {
                "नमस्ते": "hello",
                "सुप्रभात": "good morning",
                "धन्यवाद": "thank you",
                "अलविदा": "goodbye",
                "हाँ": "yes",
                "नहीं": "no"
            }
        }
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate using basic dictionary lookup."""
        text_lower = text.lower().strip()
        lang_pair = (source_lang, target_lang)
        
        # Look for exact match
        if lang_pair in self.translations:
            if text_lower in self.translations[lang_pair]:
                return TranslationResult(
                    translated_text=self.translations[lang_pair][text_lower],
                    confidence=0.9,
                    model_used="lightweight_indictrans",
                    detected_language=source_lang,
                    alternatives=[]
                )
        
        # Basic word-by-word translation
        words = text_lower.split()
        translated_words = []
        
        for word in words:
            if lang_pair in self.translations and word in self.translations[lang_pair]:
                translated_words.append(self.translations[lang_pair][word])
            else:
                translated_words.append(word)  # Keep original if no translation
        
        return TranslationResult(
            translated_text=" ".join(translated_words),
            confidence=0.6,
            model_used="lightweight_indictrans",
            detected_language=source_lang,
            alternatives=[]
        )
