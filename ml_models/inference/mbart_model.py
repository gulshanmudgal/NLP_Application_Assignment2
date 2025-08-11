"""
mBART model implementation for multilingual translation.
"""
import asyncio
import torch
from typing import List, Dict, Any
from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
import logging

from .base_model import BaseMLModel, ModelResult, ModelPrediction

logger = logging.getLogger(__name__)


class MBartModel(BaseMLModel):
    """mBART model for multilingual translation."""
    
    def __init__(self, model_name: str, model_path: str = None):
        super().__init__(model_name, model_path)
        self.supported_languages = {"en", "hi", "ta", "te", "bn", "mr"}
        self.model_version = "large-50"
        
        # Language code mappings for mBART
        self.lang_mapping = {
            "en": "en_XX",
            "hi": "hi_IN", 
            "ta": "ta_IN",
            "te": "te_IN",
            "bn": "bn_IN",
            "mr": "mr_IN"
        }
    
    async def _load_model_impl(self) -> bool:
        """Load mBART model and tokenizer."""
        try:
            # Load in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            
            def load_sync():
                tokenizer = MBart50TokenizerFast.from_pretrained(
                    self.model_name if not self.model_path else self.model_path
                )
                model = MBartForConditionalGeneration.from_pretrained(
                    self.model_name if not self.model_path else self.model_path,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                
                # Move to GPU if available
                if torch.cuda.is_available():
                    model = model.cuda()
                    
                return tokenizer, model
            
            self._tokenizer, self._model = await loop.run_in_executor(None, load_sync)
            return True
            
        except Exception as e:
            logger.error(f"Failed to load mBART model: {e}")
            return False
    
    async def _translate_impl(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        **kwargs
    ) -> ModelResult:
        """Translate using mBART model."""
        try:
            # Map language codes
            src_lang = self.lang_mapping.get(source_lang)
            tgt_lang = self.lang_mapping.get(target_lang)
            
            if not src_lang or not tgt_lang:
                raise ValueError(f"Language mapping not found for {source_lang}->{target_lang}")
            
            # Run inference in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def translate_sync():
                # Set source language
                self._tokenizer.src_lang = src_lang
                
                # Tokenize input
                inputs = self._tokenizer(
                    text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )
                
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                # Generate translation
                with torch.no_grad():
                    generated_tokens = self._model.generate(
                        **inputs,
                        forced_bos_token_id=self._tokenizer.lang_code_to_id[tgt_lang],
                        max_length=512,
                        num_beams=4,
                        early_stopping=True,
                        pad_token_id=self._tokenizer.pad_token_id
                    )
                
                # Decode output
                translated_text = self._tokenizer.batch_decode(
                    generated_tokens, 
                    skip_special_tokens=True
                )[0]
                
                return translated_text
            
            translated_text = await loop.run_in_executor(None, translate_sync)
            
            # Create result
            prediction = ModelPrediction(
                text=translated_text,
                confidence=0.75,  # mBART moderate confidence
                metadata={
                    "source_lang": src_lang,
                    "target_lang": tgt_lang,
                    "model_type": "mbart"
                }
            )
            
            return ModelResult(
                predictions=[prediction],
                model_name=self.model_name,
                model_version=self.model_version,
                processing_time=0.0,  # Will be set by caller
                input_tokens=len(text.split()),
                output_tokens=len(translated_text.split())
            )
            
        except Exception as e:
            logger.error(f"mBART translation error: {e}")
            raise
    
    def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """Check if language pair is supported by mBART."""
        # mBART supports many-to-many translation for all our languages
        return (source_lang in self.supported_languages and 
                target_lang in self.supported_languages and
                source_lang != target_lang)
