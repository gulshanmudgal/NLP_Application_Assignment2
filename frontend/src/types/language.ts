// Language interface for supported languages
export interface Language {
  code: string;
  name: string;
  nativeName: string;
  direction: 'ltr' | 'rtl';
  scriptType: 'latin' | 'devanagari' | 'tamil' | 'telugu' | 'bengali';
}

// Supported Indian languages configuration
export const SUPPORTED_LANGUAGES: Language[] = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    direction: 'ltr',
    scriptType: 'latin'
  },
  {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    direction: 'ltr',
    scriptType: 'devanagari'
  },
  {
    code: 'ta',
    name: 'Tamil',
    nativeName: 'தமிழ்',
    direction: 'ltr',
    scriptType: 'tamil'
  },
  {
    code: 'te',
    name: 'Telugu',
    nativeName: 'తెలుగు',
    direction: 'ltr',
    scriptType: 'telugu'
  },
  {
    code: 'bn',
    name: 'Bengali',
    nativeName: 'বাংলা',
    direction: 'ltr',
    scriptType: 'bengali'
  },
  {
    code: 'mr',
    name: 'Marathi',
    nativeName: 'मराठी',
    direction: 'ltr',
    scriptType: 'devanagari'
  }
];

// Language pair interface
export interface LanguagePair {
  source: string;
  target: string;
}

// Get language by code
export const getLanguageByCode = (code: string): Language | undefined => {
  return SUPPORTED_LANGUAGES.find(lang => lang.code === code);
};

// Check if language pair is supported
export const isLanguagePairSupported = (source: string, target: string): boolean => {
  const sourceExists = SUPPORTED_LANGUAGES.some(lang => lang.code === source);
  const targetExists = SUPPORTED_LANGUAGES.some(lang => lang.code === target);
  return sourceExists && targetExists && source !== target;
};
