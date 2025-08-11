from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, validator

class SupportedLanguage(str, Enum):
    """Enumeration of supported language codes"""
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"

class ScriptType(str, Enum):
    """Enumeration of script types"""
    LATIN = "latin"
    DEVANAGARI = "devanagari"
    TAMIL = "tamil"
    TELUGU = "telugu"
    BENGALI = "bengali"

class TextDirection(str, Enum):
    """Text direction enumeration"""
    LTR = "ltr"
    RTL = "rtl"

class Language(BaseModel):
    """Language model with metadata"""
    code: SupportedLanguage
    name: str
    native_name: str
    direction: TextDirection = TextDirection.LTR
    script_type: ScriptType
    
    class Config:
        use_enum_values = True

# Predefined language configurations
LANGUAGE_CONFIGS = {
    SupportedLanguage.ENGLISH: Language(
        code=SupportedLanguage.ENGLISH,
        name="English",
        native_name="English",
        direction=TextDirection.LTR,
        script_type=ScriptType.LATIN
    ),
    SupportedLanguage.HINDI: Language(
        code=SupportedLanguage.HINDI,
        name="Hindi",
        native_name="हिन्दी",
        direction=TextDirection.LTR,
        script_type=ScriptType.DEVANAGARI
    ),
    SupportedLanguage.TAMIL: Language(
        code=SupportedLanguage.TAMIL,
        name="Tamil",
        native_name="தமிழ்",
        direction=TextDirection.LTR,
        script_type=ScriptType.TAMIL
    ),
    SupportedLanguage.TELUGU: Language(
        code=SupportedLanguage.TELUGU,
        name="Telugu",
        native_name="తెలుగు",
        direction=TextDirection.LTR,
        script_type=ScriptType.TELUGU
    ),
    SupportedLanguage.BENGALI: Language(
        code=SupportedLanguage.BENGALI,
        name="Bengali",
        native_name="বাংলা",
        direction=TextDirection.LTR,
        script_type=ScriptType.BENGALI
    ),
    SupportedLanguage.MARATHI: Language(
        code=SupportedLanguage.MARATHI,
        name="Marathi",
        native_name="मराठी",
        direction=TextDirection.LTR,
        script_type=ScriptType.DEVANAGARI
    )
}

class LanguagePair(BaseModel):
    """Language pair model for translation"""
    source: SupportedLanguage
    target: SupportedLanguage
    
    @validator('target')
    def validate_different_languages(cls, v, values):
        if 'source' in values and v == values['source']:
            raise ValueError('Source and target languages must be different')
        return v
    
    class Config:
        use_enum_values = True

def get_supported_languages() -> List[Language]:
    """Get list of all supported languages"""
    return list(LANGUAGE_CONFIGS.values())

def get_language_by_code(code: str) -> Optional[Language]:
    """Get language configuration by code"""
    try:
        lang_code = SupportedLanguage(code)
        return LANGUAGE_CONFIGS.get(lang_code)
    except ValueError:
        return None

def is_language_pair_supported(source: str, target: str) -> bool:
    """Check if a language pair is supported"""
    try:
        source_lang = SupportedLanguage(source)
        target_lang = SupportedLanguage(target)
        return source_lang != target_lang
    except ValueError:
        return False
