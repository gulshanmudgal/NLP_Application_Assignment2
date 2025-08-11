"""
Translation service for handling multiple translation models.
"""
import asyncio
import time
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import logging

from app.models.language import get_language_by_code, get_supported_languages


logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Translation result from a model."""
    translated_text: str
    confidence: float
    model_used: str
    detected_language: Optional[str] = None
    alternatives: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class ModelType(Enum):
    """Available translation model types."""
    AUTO = "auto"
    INDICTRANS = "indictrans"
    M2M100 = "m2m100"
    MBART = "mbart"
    MOCK = "mock"  # For development/testing


class TranslationService:
    """Main translation service coordinating multiple models."""
    
    def __init__(self):
        self.models = {}
        self.stats = {
            "total_translations": 0,
            "translations_by_model": {},
            "translations_by_language": {},
            "average_processing_time": 0,
            "total_processing_time": 0
        }
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available translation models."""
        logger.info("Initializing translation models...")
        
        # Start with mock translator
        self.models = {
            ModelType.MOCK.value: MockTranslator(),
        }
        
        # Try to initialize ML models
        try:
            from app.services.ml_translators import (
                IndicTransTranslator, 
                M2M100Translator, 
                MBartTranslator,
                LightweightIndicTransTranslator
            )
            
            # Initialize lightweight version first as fallback
            self.models["lightweight_indictrans"] = LightweightIndicTransTranslator()
            
            # Try to initialize heavy ML models
            try:
                self.models[ModelType.INDICTRANS.value] = IndicTransTranslator()
                logger.info("IndicTrans model initialized")
            except Exception as e:
                logger.warning(f"IndicTrans model failed to initialize: {e}")
                
            try:
                self.models[ModelType.M2M100.value] = M2M100Translator()
                logger.info("M2M100 model initialized")
            except Exception as e:
                logger.warning(f"M2M100 model failed to initialize: {e}")
                
            try:
                self.models[ModelType.MBART.value] = MBartTranslator()
                logger.info("mBART model initialized")
            except Exception as e:
                logger.warning(f"mBART model failed to initialize: {e}")
                
        except ImportError as e:
            logger.warning(f"ML translators not available: {e}")
        
        # Add auto translator after models are loaded
        self.models[ModelType.AUTO.value] = AutoTranslator(self.models)
        
        logger.info(f"Initialized {len(self.models)} translation models: {list(self.models.keys())}")
    
    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        model: str = "auto"
    ) -> TranslationResult:
        """
        Translate text using specified or auto-selected model.
        
        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code  
            model: Model to use ("auto" for automatic selection)
            
        Returns:
            TranslationResult with translated text and metadata
        """
        start_time = time.time()
        
        try:
            # Validate languages
            source_lang = get_language_by_code(source_language)
            target_lang = get_language_by_code(target_language)
            
            if not source_lang:
                raise ValueError(f"Unsupported source language: {source_language}")
            if not target_lang:
                raise ValueError(f"Unsupported target language: {target_language}")
            
            # Select model
            selected_model = self._select_model(model, source_language, target_language)
            if not selected_model:
                raise ValueError(f"No suitable model found for {source_language}->{target_language}")
            
            # Perform translation
            translator = self.models[selected_model]
            result = await translator.translate(text, source_language, target_language)
            result.model_used = selected_model
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_stats(source_language, target_language, selected_model, processing_time)
            
            logger.info(
                f"Translation completed: {source_language}->{target_language} "
                f"using {selected_model} in {processing_time:.3f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise
    
    def _select_model(self, requested_model: str, source_lang: str, target_lang: str) -> Optional[str]:
        """Select the best available model for the language pair."""
        if requested_model != "auto" and requested_model in self.models:
            return requested_model
        
        # Auto-selection logic based on available models
        available_models = list(self.models.keys())
        
        # Priority order for model selection based on language pair
        if source_lang in {"hi", "ta", "te", "bn", "mr"} or target_lang in {"hi", "ta", "te", "bn", "mr"}:
            # For Indian languages, prefer lightweight then heavy models
            model_priority = [
                "lightweight_indictrans",    # Lightweight fallback (always works)
                ModelType.INDICTRANS.value,  # Best for Indian languages (if available)
                ModelType.M2M100.value,      # Good multilingual model
                ModelType.MBART.value,       # Alternative multilingual model
                ModelType.MOCK.value         # Final fallback
            ]
        else:
            # For other language pairs
            model_priority = [
                ModelType.M2M100.value,      # Good for general multilingual
                ModelType.MBART.value,       # Alternative multilingual
                "lightweight_indictrans",    # Basic fallback
                ModelType.INDICTRANS.value,  # May support the pair
                ModelType.MOCK.value         # Final fallback
            ]
        
        for model in model_priority:
            if model in available_models:
                return model
        
        return None
    
    def _update_stats(self, source_lang: str, target_lang: str, model: str, processing_time: float):
        """Update translation statistics."""
        self.stats["total_translations"] += 1
        self.stats["total_processing_time"] += processing_time
        self.stats["average_processing_time"] = (
            self.stats["total_processing_time"] / self.stats["total_translations"]
        )
        
        # Update by model
        if model not in self.stats["translations_by_model"]:
            self.stats["translations_by_model"][model] = 0
        self.stats["translations_by_model"][model] += 1
        
        # Update by language pair
        lang_pair = f"{source_lang}-{target_lang}"
        if lang_pair not in self.stats["translations_by_language"]:
            self.stats["translations_by_language"][lang_pair] = 0
        self.stats["translations_by_language"][lang_pair] += 1
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get information about available models."""
        models_info = []
        
        for model_name, translator in self.models.items():
            info = {
                "name": model_name,
                "type": type(translator).__name__,
                "loaded": True,
                "supported_languages": [lang.code for lang in get_supported_languages()],
                "description": getattr(translator, 'description', 'Translation model')
            }
            models_info.append(info)
        
        return models_info
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get translation service statistics."""
        return self.stats.copy()


class BaseTranslator:
    """Base class for translation models."""
    
    def __init__(self):
        self.description = "Base translator"
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Translate text. Must be implemented by subclasses."""
        raise NotImplementedError


class MockTranslator(BaseTranslator):
    """Mock translator for development and testing."""
    
    def __init__(self):
        super().__init__()
        self.description = "Mock translator for development"
        
        # Mock translations for common phrases
        self.mock_translations = {
            ("en", "hi"): {
                "Hello": "नमस्ते",
                "Hello world": "नमस्ते संसार", 
                "How are you?": "आप कैसे हैं?",
                "Good morning": "सुप्रभात",
                "Thank you": "धन्यवाद",
                "Welcome": "स्वागत है",
                "Goodbye": "अलविदा",
                "Please": "कृपया",
                "Yes": "हाँ",
                "No": "नहीं"
            },
            ("en", "ta"): {
                "Hello": "வணக்கம்",
                "Hello world": "வணக்கம் உலகம்",
                "How are you?": "நீங்கள் எப்படி இருக்கிறீர்கள்?",
                "Good morning": "காலை வணக்கம்",
                "Thank you": "நன்றி",
                "Welcome": "வரவேற்கிறோம்",
                "Goodbye": "பிரியாவிடை",
                "Please": "தயவு செய்து",
                "Yes": "ஆம்",
                "No": "இல்லை"
            },
            ("en", "te"): {
                "Hello": "నమస్కారం",
                "Hello world": "హలో ప్రపంచం",
                "How are you?": "మీరు ఎలా ఉన్నారు?",
                "Good morning": "శుభోదయం",
                "Thank you": "ధన్యవాదాలు",
                "Welcome": "స్వాగతం",
                "Goodbye": "వీడ్కోలు",
                "Please": "దయచేసి",
                "Yes": "అవును",
                "No": "లేదు"
            },
            ("en", "bn"): {
                "Hello": "হ্যালো",
                "Hello world": "হ্যালো বিশ্ব",
                "How are you?": "আপনি কেমন আছেন?",
                "Good morning": "সুপ্রভাত",
                "Thank you": "ধন্যবাদ",
                "Welcome": "স্বাগতম",
                "Goodbye": "বিদায়",
                "Please": "দয়া করে",
                "Yes": "হ্যাঁ",
                "No": "না"
            },
            ("en", "mr"): {
                "Hello": "नमस्कार",
                "Hello world": "हॅलो जग",
                "How are you?": "तुम्ही कसे आहात?",
                "Good morning": "शुभ सकाळ",
                "Thank you": "धन्यवाद",
                "Welcome": "स्वागत",
                "Goodbye": "निरोप",
                "Please": "कृपया",
                "Yes": "होय",
                "No": "नाही"
            }
        }
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Mock translation with simulated processing time."""
        # Simulate processing delay
        await asyncio.sleep(0.1 + len(text) * 0.001)  # Simulate realistic processing time
        
        # Get mock translation
        lang_pair = (source_lang, target_lang)
        translations = self.mock_translations.get(lang_pair, {})
        
        # Try exact match first
        if text in translations:
            translated = translations[text]
            confidence = 0.95
        else:
            # Generate a mock translation for unknown text
            if target_lang == "hi":
                translated = f"अनुवादित: {text}"
            elif target_lang == "ta":
                translated = f"மொழிபெயர்க்கப்பட்டது: {text}"
            elif target_lang == "te":
                translated = f"అనువదించబడింది: {text}"
            elif target_lang == "bn":
                translated = f"অনুবাদিত: {text}"
            elif target_lang == "mr":
                translated = f"भाषांतरित: {text}"
            elif target_lang == "en":
                translated = f"Translated: {text}"
            else:
                translated = f"[{target_lang}] {text}"
            
            confidence = 0.75  # Lower confidence for unknown phrases
        
        # Generate mock alternatives
        alternatives = []
        if len(text.split()) > 1:  # Only for multi-word phrases
            alternatives = [
                {"text": f"Alt 1: {translated}", "confidence": confidence - 0.1},
                {"text": f"Alt 2: {translated}", "confidence": confidence - 0.2},
            ]
        
        return TranslationResult(
            translated_text=translated,
            confidence=confidence,
            model_used="mock",
            alternatives=alternatives
        )


class AutoTranslator(BaseTranslator):
    """Auto translator that selects the best available model."""
    
    def __init__(self, available_models: Dict[str, BaseTranslator]):
        super().__init__()
        self.description = "Auto-selecting translator"
        self.available_models = available_models
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> TranslationResult:
        """Select best model and translate."""
        # For now, fall back to mock translator
        mock_translator = self.available_models.get("mock")
        if mock_translator:
            return await mock_translator.translate(text, source_lang, target_lang)
        
        raise ValueError("No suitable translator available")


# Global translation service instance
_translation_service = None


def get_translation_service() -> TranslationService:
    """Dependency function to get translation service instance."""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
