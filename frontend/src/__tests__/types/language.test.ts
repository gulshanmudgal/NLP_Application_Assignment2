import {
  Language,
  SUPPORTED_LANGUAGES,
  getLanguageByCode,
  isLanguagePairSupported,
  LanguagePair
} from '../../types/language';

describe('Language Types', () => {
  describe('SUPPORTED_LANGUAGES', () => {
    test('should contain all required Indian languages', () => {
      const languageCodes = SUPPORTED_LANGUAGES.map(lang => lang.code);
      
      expect(languageCodes).toContain('en'); // English
      expect(languageCodes).toContain('hi'); // Hindi
      expect(languageCodes).toContain('ta'); // Tamil
      expect(languageCodes).toContain('te'); // Telugu
      expect(languageCodes).toContain('bn'); // Bengali
      expect(languageCodes).toContain('mr'); // Marathi
    });

    test('should have proper language structure', () => {
      SUPPORTED_LANGUAGES.forEach(language => {
        expect(language).toHaveProperty('code');
        expect(language).toHaveProperty('name');
        expect(language).toHaveProperty('nativeName');
        expect(language).toHaveProperty('direction');
        expect(language).toHaveProperty('scriptType');
        
        expect(typeof language.code).toBe('string');
        expect(typeof language.name).toBe('string');
        expect(typeof language.nativeName).toBe('string');
        expect(['ltr', 'rtl']).toContain(language.direction);
        expect(['latin', 'devanagari', 'tamil', 'telugu', 'bengali']).toContain(language.scriptType);
      });
    });

    test('should have unique language codes', () => {
      const codes = SUPPORTED_LANGUAGES.map(lang => lang.code);
      const uniqueCodes = Array.from(new Set(codes));
      
      expect(codes.length).toBe(uniqueCodes.length);
    });

    test('should have proper native names for Indian languages', () => {
      const hindi = SUPPORTED_LANGUAGES.find(lang => lang.code === 'hi');
      const tamil = SUPPORTED_LANGUAGES.find(lang => lang.code === 'ta');
      const telugu = SUPPORTED_LANGUAGES.find(lang => lang.code === 'te');
      const bengali = SUPPORTED_LANGUAGES.find(lang => lang.code === 'bn');
      const marathi = SUPPORTED_LANGUAGES.find(lang => lang.code === 'mr');
      
      expect(hindi?.nativeName).toBe('हिन्दी');
      expect(tamil?.nativeName).toBe('தமிழ்');
      expect(telugu?.nativeName).toBe('తెలుగు');
      expect(bengali?.nativeName).toBe('বাংলা');
      expect(marathi?.nativeName).toBe('मराठी');
    });
  });

  describe('getLanguageByCode', () => {
    test('should return correct language for valid code', () => {
      const hindi = getLanguageByCode('hi');
      
      expect(hindi).toBeDefined();
      expect(hindi?.code).toBe('hi');
      expect(hindi?.name).toBe('Hindi');
      expect(hindi?.nativeName).toBe('हिन्दी');
    });

    test('should return undefined for invalid code', () => {
      const invalidLang = getLanguageByCode('xyz');
      
      expect(invalidLang).toBeUndefined();
    });

    test('should return undefined for empty code', () => {
      const emptyLang = getLanguageByCode('');
      
      expect(emptyLang).toBeUndefined();
    });
  });

  describe('isLanguagePairSupported', () => {
    test('should return true for valid language pairs', () => {
      expect(isLanguagePairSupported('en', 'hi')).toBe(true);
      expect(isLanguagePairSupported('hi', 'en')).toBe(true);
      expect(isLanguagePairSupported('ta', 'te')).toBe(true);
    });

    test('should return false for same source and target', () => {
      expect(isLanguagePairSupported('en', 'en')).toBe(false);
      expect(isLanguagePairSupported('hi', 'hi')).toBe(false);
    });

    test('should return false for unsupported languages', () => {
      expect(isLanguagePairSupported('en', 'xyz')).toBe(false);
      expect(isLanguagePairSupported('xyz', 'hi')).toBe(false);
      expect(isLanguagePairSupported('abc', 'xyz')).toBe(false);
    });

    test('should return false for empty strings', () => {
      expect(isLanguagePairSupported('', 'hi')).toBe(false);
      expect(isLanguagePairSupported('en', '')).toBe(false);
      expect(isLanguagePairSupported('', '')).toBe(false);
    });
  });

  describe('Language interface', () => {
    test('should validate language structure', () => {
      const testLanguage: Language = {
        code: 'en',
        name: 'English',
        nativeName: 'English',
        direction: 'ltr',
        scriptType: 'latin'
      };

      expect(testLanguage.code).toBe('en');
      expect(testLanguage.direction).toBe('ltr');
      expect(testLanguage.scriptType).toBe('latin');
    });
  });

  describe('LanguagePair interface', () => {
    test('should validate language pair structure', () => {
      const testPair: LanguagePair = {
        source: 'en',
        target: 'hi'
      };

      expect(testPair.source).toBe('en');
      expect(testPair.target).toBe('hi');
    });
  });
});
