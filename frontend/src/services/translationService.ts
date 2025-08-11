/**
 * Translation Service for communicating with the backend API
 */
import { TranslationRequest, TranslationResult, Language } from '../types';

// Backend API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API_VERSION = '/api/v1';

export class TranslationService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Translate text using the backend API
   */
  async translateText(request: TranslationRequest): Promise<TranslationResult> {
    try {
      const response = await fetch(`${this.baseUrl}${API_VERSION}/translate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: request.text,
          source_language: request.sourceLanguage,
          target_language: request.targetLanguage,
          model: request.model || 'auto',
          enable_cache: request.enableCache ?? true,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Translation failed with status: ${response.status}`
        );
      }

      const data = await response.json();
      
      return {
        translatedText: data.translated_text,
        sourceLanguage: data.source_language,
        targetLanguage: data.target_language,
        confidence: data.confidence_score,
        model: data.model_used,
        processingTime: data.processing_time,
        fromCache: data.cached,
        alternatives: data.alternatives || [],
      };
    } catch (error) {
      console.error('Translation service error:', error);
      throw error instanceof Error ? error : new Error('Translation service unavailable');
    }
  }

  /**
   * Get available translation models
   */
  async getAvailableModels(): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}${API_VERSION}/translate/models`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch models: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching models:', error);
      throw error instanceof Error ? error : new Error('Failed to fetch available models');
    }
  }

  /**
   * Get supported languages
   */
  async getSupportedLanguages(): Promise<Language[]> {
    try {
      const response = await fetch(`${this.baseUrl}${API_VERSION}/languages/`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch languages: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching languages:', error);
      // Fallback to default languages if API fails
      return [
        { code: 'en', name: 'English', nativeName: 'English', direction: 'ltr', scriptType: 'latin' },
        { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', direction: 'ltr', scriptType: 'devanagari' },
        { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', direction: 'ltr', scriptType: 'tamil' },
        { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', direction: 'ltr', scriptType: 'telugu' },
        { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', direction: 'ltr', scriptType: 'bengali' },
        { code: 'mr', name: 'Marathi', nativeName: 'मराठी', direction: 'ltr', scriptType: 'devanagari' },
      ];
    }
  }

  /**
   * Check if the translation service is healthy
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Create a singleton instance
export const translationService = new TranslationService();
export default translationService;
