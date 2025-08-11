import {
  validateTranslationRequest,
  validateTextInput,
  sanitizeTextInput,
  hasMixedScripts,
  detectPrimaryScript,
  MAX_TEXT_LENGTH
} from '../../utils/validation';
import { TranslationRequest } from '../../types';

describe('Validation Utils', () => {
  describe('validateTranslationRequest', () => {
    const validRequest: TranslationRequest = {
      text: 'Hello world',
      sourceLanguage: 'en',
      targetLanguage: 'hi',
      enableCache: true,
      model: 'auto'
    };

    test('should validate correct translation request', () => {
      const result = validateTranslationRequest(validRequest);
      
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should reject empty text', () => {
      const request = { ...validRequest, text: '' };
      const result = validateTranslationRequest(request);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Text is required');
    });

    test('should reject whitespace-only text', () => {
      const request = { ...validRequest, text: '   \n\t   ' };
      const result = validateTranslationRequest(request);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Text cannot be empty or whitespace only');
    });

    test('should reject text exceeding max length', () => {
      const longText = 'a'.repeat(MAX_TEXT_LENGTH + 1);
      const request = { ...validRequest, text: longText };
      const result = validateTranslationRequest(request);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(`Text cannot exceed ${MAX_TEXT_LENGTH} characters`);
    });

    test('should reject missing source language', () => {
      const request = { ...validRequest, sourceLanguage: undefined };
      const result = validateTranslationRequest(request);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Source language is required');
    });

    test('should reject missing target language', () => {
      const request = { ...validRequest, targetLanguage: undefined };
      const result = validateTranslationRequest(request);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Target language is required');
    });

    test('should reject same source and target languages', () => {
      const request = { ...validRequest, sourceLanguage: 'en', targetLanguage: 'en' };
      const result = validateTranslationRequest(request);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Source and target languages must be different');
    });

    test('should reject unsupported language pairs', () => {
      const request = { ...validRequest, sourceLanguage: 'xyz', targetLanguage: 'abc' };
      const result = validateTranslationRequest(request);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Selected language pair is not supported');
    });
  });

  describe('validateTextInput', () => {
    test('should validate correct text input', () => {
      const result = validateTextInput('Hello world');
      
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    test('should reject empty text', () => {
      const result = validateTextInput('');
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Text is required');
    });

    test('should reject whitespace-only text', () => {
      const result = validateTextInput('   \n\t   ');
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Text cannot be empty or whitespace only');
    });

    test('should reject text exceeding max length', () => {
      const longText = 'a'.repeat(MAX_TEXT_LENGTH + 1);
      const result = validateTextInput(longText);
      
      expect(result.isValid).toBe(false);
      expect(result.errors).toContain(`Text cannot exceed ${MAX_TEXT_LENGTH} characters`);
    });
  });

  describe('sanitizeTextInput', () => {
    test('should return empty string for null/undefined input', () => {
      expect(sanitizeTextInput('')).toBe('');
    });

    test('should trim whitespace', () => {
      expect(sanitizeTextInput('  hello world  ')).toBe('hello world');
    });

    test('should normalize multiple whitespace', () => {
      expect(sanitizeTextInput('hello    world\n\ntest')).toBe('hello world test');
    });

    test('should limit to max length', () => {
      const longText = 'a'.repeat(MAX_TEXT_LENGTH + 100);
      const result = sanitizeTextInput(longText);
      
      expect(result.length).toBe(MAX_TEXT_LENGTH);
    });
  });

  describe('hasMixedScripts', () => {
    test('should detect mixed English and Hindi scripts', () => {
      const mixedText = 'Hello नमस्ते';
      expect(hasMixedScripts(mixedText)).toBe(true);
    });

    test('should return false for single script text', () => {
      expect(hasMixedScripts('Hello world')).toBe(false);
      expect(hasMixedScripts('नमस्ते दुनिया')).toBe(false);
      expect(hasMixedScripts('வணக்கம் உலகம்')).toBe(false);
    });

    test('should handle empty text', () => {
      expect(hasMixedScripts('')).toBe(false);
    });

    test('should detect multiple Indic scripts', () => {
      const mixedIndic = 'हिन्दी தமிழ்';
      expect(hasMixedScripts(mixedIndic)).toBe(true);
    });
  });

  describe('detectPrimaryScript', () => {
    test('should detect Latin script as primary', () => {
      const text = 'Hello world with some हिन्दी';
      expect(detectPrimaryScript(text)).toBe('latin');
    });

    test('should detect Devanagari script as primary', () => {
      const text = 'नमस्ते दुनिया with some English';
      expect(detectPrimaryScript(text)).toBe('devanagari');
    });

    test('should detect Tamil script as primary', () => {
      const text = 'வணக்கம் உலகம் hello';
      expect(detectPrimaryScript(text)).toBe('tamil');
    });

    test('should handle text with no recognized scripts', () => {
      const text = '123 456 789 !@#';
      expect(detectPrimaryScript(text)).toBe('latin'); // Should default to latin
    });

    test('should handle empty text', () => {
      expect(detectPrimaryScript('')).toBe('latin');
    });
  });
});
