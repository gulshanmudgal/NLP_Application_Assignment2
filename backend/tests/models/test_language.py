import pytest
from pydantic import ValidationError
from app.models.language import (
    Language,
    LanguagePair,
    SupportedLanguage,
    ScriptType,
    TextDirection,
    LANGUAGE_CONFIGS,
    get_supported_languages,
    get_language_by_code,
    is_language_pair_supported
)

class TestSupportedLanguage:
    """Test SupportedLanguage enum"""
    
    def test_supported_language_values(self):
        """Test that all required languages are supported"""
        assert SupportedLanguage.ENGLISH == "en"
        assert SupportedLanguage.HINDI == "hi"
        assert SupportedLanguage.TAMIL == "ta"
        assert SupportedLanguage.TELUGU == "te"
        assert SupportedLanguage.BENGALI == "bn"
        assert SupportedLanguage.MARATHI == "mr"
    
    def test_supported_language_count(self):
        """Test that we have the expected number of supported languages"""
        assert len(list(SupportedLanguage)) == 6

class TestLanguageModel:
    """Test Language model validation and structure"""
    
    def test_valid_language_creation(self):
        """Test creating a valid language model"""
        language = Language(
            code=SupportedLanguage.HINDI,
            name="Hindi",
            native_name="हिन्दी",
            direction=TextDirection.LTR,
            script_type=ScriptType.DEVANAGARI
        )
        
        assert language.code == SupportedLanguage.HINDI
        assert language.name == "Hindi"
        assert language.native_name == "हिन्दी"
        assert language.direction == TextDirection.LTR
        assert language.script_type == ScriptType.DEVANAGARI
    
    def test_language_with_defaults(self):
        """Test language creation with default values"""
        language = Language(
            code=SupportedLanguage.ENGLISH,
            name="English",
            native_name="English",
            script_type=ScriptType.LATIN
        )
        
        # Should default to LTR
        assert language.direction == TextDirection.LTR
    
    def test_invalid_language_code(self):
        """Test that invalid language codes raise ValidationError"""
        with pytest.raises(ValidationError):
            Language(
                code="invalid_code",
                name="Invalid",
                native_name="Invalid",
                script_type=ScriptType.LATIN
            )

class TestLanguagePair:
    """Test LanguagePair model validation"""
    
    def test_valid_language_pair(self):
        """Test creating a valid language pair"""
        pair = LanguagePair(
            source=SupportedLanguage.ENGLISH,
            target=SupportedLanguage.HINDI
        )
        
        assert pair.source == SupportedLanguage.ENGLISH
        assert pair.target == SupportedLanguage.HINDI
    
    def test_same_source_target_validation(self):
        """Test that same source and target languages are rejected"""
        with pytest.raises(ValidationError) as exc_info:
            LanguagePair(
                source=SupportedLanguage.ENGLISH,
                target=SupportedLanguage.ENGLISH
            )
        
        assert "Source and target languages must be different" in str(exc_info.value)
    
    def test_invalid_language_in_pair(self):
        """Test that invalid language codes in pairs raise ValidationError"""
        with pytest.raises(ValidationError):
            LanguagePair(
                source="invalid",
                target=SupportedLanguage.HINDI
            )

class TestLanguageConfigs:
    """Test predefined language configurations"""
    
    def test_language_configs_completeness(self):
        """Test that all supported languages have configurations"""
        expected_languages = set(SupportedLanguage)
        configured_languages = set(LANGUAGE_CONFIGS.keys())
        
        assert expected_languages == configured_languages
    
    def test_language_configs_structure(self):
        """Test that all language configs have proper structure"""
        for lang_code, config in LANGUAGE_CONFIGS.items():
            assert isinstance(config, Language)
            assert config.code == lang_code
            assert len(config.name) > 0
            assert len(config.native_name) > 0
    
    def test_indian_language_native_names(self):
        """Test that Indian languages have proper native names"""
        hindi_config = LANGUAGE_CONFIGS[SupportedLanguage.HINDI]
        tamil_config = LANGUAGE_CONFIGS[SupportedLanguage.TAMIL]
        telugu_config = LANGUAGE_CONFIGS[SupportedLanguage.TELUGU]
        bengali_config = LANGUAGE_CONFIGS[SupportedLanguage.BENGALI]
        marathi_config = LANGUAGE_CONFIGS[SupportedLanguage.MARATHI]
        
        assert hindi_config.native_name == "हिन्दी"
        assert tamil_config.native_name == "தமிழ்"
        assert telugu_config.native_name == "తెలుగు"
        assert bengali_config.native_name == "বাংলা"
        assert marathi_config.native_name == "मराठी"
    
    def test_script_types_correct(self):
        """Test that languages have correct script types"""
        hindi_config = LANGUAGE_CONFIGS[SupportedLanguage.HINDI]
        tamil_config = LANGUAGE_CONFIGS[SupportedLanguage.TAMIL]
        english_config = LANGUAGE_CONFIGS[SupportedLanguage.ENGLISH]
        
        assert hindi_config.script_type == ScriptType.DEVANAGARI
        assert tamil_config.script_type == ScriptType.TAMIL
        assert english_config.script_type == ScriptType.LATIN

class TestLanguageUtils:
    """Test language utility functions"""
    
    def test_get_supported_languages(self):
        """Test getting all supported languages"""
        languages = get_supported_languages()
        
        assert len(languages) == 6
        assert all(isinstance(lang, Language) for lang in languages)
        
        # Check that all expected languages are present
        codes = {lang.code for lang in languages}
        expected_codes = {lang for lang in SupportedLanguage}
        assert codes == expected_codes
    
    def test_get_language_by_code_valid(self):
        """Test getting language by valid code"""
        hindi = get_language_by_code("hi")
        
        assert hindi is not None
        assert hindi.code == SupportedLanguage.HINDI
        assert hindi.name == "Hindi"
        assert hindi.native_name == "हिन्दी"
    
    def test_get_language_by_code_invalid(self):
        """Test getting language by invalid code"""
        invalid_lang = get_language_by_code("xyz")
        
        assert invalid_lang is None
    
    def test_get_language_by_code_empty(self):
        """Test getting language by empty code"""
        empty_lang = get_language_by_code("")
        
        assert empty_lang is None
    
    def test_is_language_pair_supported_valid(self):
        """Test checking valid language pairs"""
        assert is_language_pair_supported("en", "hi") is True
        assert is_language_pair_supported("hi", "en") is True
        assert is_language_pair_supported("ta", "te") is True
    
    def test_is_language_pair_supported_same_language(self):
        """Test checking same language pairs"""
        assert is_language_pair_supported("en", "en") is False
        assert is_language_pair_supported("hi", "hi") is False
    
    def test_is_language_pair_supported_invalid(self):
        """Test checking invalid language pairs"""
        assert is_language_pair_supported("en", "xyz") is False
        assert is_language_pair_supported("xyz", "hi") is False
        assert is_language_pair_supported("abc", "def") is False
    
    def test_is_language_pair_supported_empty(self):
        """Test checking empty language codes"""
        assert is_language_pair_supported("", "hi") is False
        assert is_language_pair_supported("en", "") is False
        assert is_language_pair_supported("", "") is False

class TestEnumValues:
    """Test enum value consistency"""
    
    def test_script_type_values(self):
        """Test ScriptType enum values"""
        assert ScriptType.LATIN == "latin"
        assert ScriptType.DEVANAGARI == "devanagari"
        assert ScriptType.TAMIL == "tamil"
        assert ScriptType.TELUGU == "telugu"
        assert ScriptType.BENGALI == "bengali"
    
    def test_text_direction_values(self):
        """Test TextDirection enum values"""
        assert TextDirection.LTR == "ltr"
        assert TextDirection.RTL == "rtl"
