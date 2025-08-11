"""
IndicTrans model implementation for Indian language translation.
"""
import asyncio
import torch
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import logging

from .base_model import BaseMLModel, ModelResult, ModelPrediction

logger = logging.getLogger(__name__)


class IndicTransModel(BaseMLModel):
    """IndicTrans model for English-Indian language translation."""
    
    def __init__(self, model_name: str, model_path: str = None):
        super().__init__(model_name, model_path)
        self.supported_languages = {"en", "hi", "ta", "te", "bn", "mr"}
        self.model_version = "2.0"
        
        # Language code mappings for IndicTrans
        self.lang_mapping = {
            "en": "eng_Latn",
            "hi": "hin_Deva", 
            "ta": "tam_Taml",
            "te": "tel_Telu",
            "bn": "ben_Beng",
            "mr": "mar_Deva"
        }
    
    async def _load_model_impl(self) -> bool:
        """Load IndicTrans model and tokenizer."""
        try:
            # Load in a separate thread to avoid blocking
            loop = asyncio.get_event_loop()
            
            def load_sync():
                tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name if not self.model_path else self.model_path,
                    trust_remote_code=True
                )
                model = AutoModelForSeq2SeqLM.from_pretrained(
                    self.model_name if not self.model_path else self.model_path,
                    trust_remote_code=True,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32
                )
                
                # Move to GPU if available
                if torch.cuda.is_available():
                    model = model.cuda()
                    
                return tokenizer, model
            
            self._tokenizer, self._model = await loop.run_in_executor(None, load_sync)
            return True
            
        except Exception as e:
            logger.error(f"Failed to load IndicTrans model: {e}")
            return False
    
    async def _translate_impl(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        **kwargs
    ) -> ModelResult:
        """Translate using IndicTrans model."""
        try:
            # Map language codes
            src_lang = self.lang_mapping.get(source_lang)
            tgt_lang = self.lang_mapping.get(target_lang)
            
            if not src_lang or not tgt_lang:
                raise ValueError(f"Language mapping not found for {source_lang}->{target_lang}")
            
            # Prepare input with language tokens
            input_text = f"{src_lang}: {text}"
            
            # Run inference in executor to avoid blocking
            loop = asyncio.get_event_loop()
            
            def translate_sync():
                # Tokenize input
                inputs = self._tokenizer(
                    input_text,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )
                
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                # Generate translation
                with torch.no_grad():
                    outputs = self._model.generate(
                        **inputs,
                        max_length=512,
                        num_beams=4,
                        early_stopping=True,
                        forced_bos_token_id=self._tokenizer.lang_code_to_id.get(tgt_lang),
                        pad_token_id=self._tokenizer.pad_token_id
                    )
                
                # Decode output
                translated_texts = self._tokenizer.batch_decode(
                    outputs, 
                    skip_special_tokens=True
                )
                
                return translated_texts[0]
            
            translated_text = await loop.run_in_executor(None, translate_sync)
            
            # Create result
            prediction = ModelPrediction(
                text=translated_text,
                confidence=0.85,  # IndicTrans typically has high confidence
                metadata={
                    "source_lang": src_lang,
                    "target_lang": tgt_lang,
                    "model_type": "indictrans"
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
            logger.error(f"IndicTrans translation error: {e}")
            raise
    
    def supports_language_pair(self, source_lang: str, target_lang: str) -> bool:
        """Check if language pair is supported by IndicTrans."""
        # IndicTrans primarily supports English <-> Indian languages
        if source_lang == "en" and target_lang in self.supported_languages:
            return True
        if source_lang in self.supported_languages and target_lang == "en":
            return True
        # Also supports some Indian-to-Indian translations
        if (source_lang in {"hi", "ta", "te", "bn", "mr"} and 
            target_lang in {"hi", "ta", "te", "bn", "mr"}):
            return True
        return False
