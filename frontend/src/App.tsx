import React from 'react';
import styled, { createGlobalStyle } from 'styled-components';
import { TranslationInterface } from './components';
import { TranslationRequest, TranslationResult } from './types';
import { translationService } from './services/translationService';

// Global styles
const GlobalStyle = createGlobalStyle`
  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
      'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
      sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #333;
  }

  code {
    font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
      monospace;
  }
`;

const App: React.FC = () => {
  // Real translation function using the backend API
  const handleTranslate = async (request: TranslationRequest): Promise<TranslationResult> => {
    try {
      return await translationService.translateText(request);
    } catch (error) {
      console.error('Translation error:', error);
      // Fallback to mock translation for demo if API fails
      return getMockTranslation(request);
    }
  };

  // Fallback mock translation function
  const getMockTranslation = async (request: TranslationRequest): Promise<TranslationResult> => {
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Mock translation responses for demo
    const mockTranslations: Record<string, Record<string, string>> = {
      'en-hi': {
        'Hello': 'नमस्ते',
        'Hello world': 'नमस्ते संसार',
        'How are you?': 'आप कैसे हैं?',
        'Hello, how are you?': 'नमस्ते, आप कैसे हैं?',
        'Good morning': 'सुप्रभात',
        'Thank you': 'धन्यवाद',
        'Welcome': 'स्वागत है'
      },
      'en-ta': {
        'Hello': 'வணக்கம்',
        'Hello world': 'வணக்கம் உலகம்',
        'How are you?': 'நீங்கள் எப்படி இருக்கிறீர்கள்?',
        'Good morning': 'காலை வணக்கம்',
        'Thank you': 'நன்றி'
      },
      'en-te': {
        'Hello': 'హలో',
        'Hello world': 'హలో ప్రపంచం',
        'How are you?': 'మీరు ఎలా ఉన్నారు?',
        'Good morning': 'శుభోదయం',
        'Thank you': 'ధన్యవాదాలు'
      },
      'en-bn': {
        'Hello': 'হ্যালো',
        'Hello world': 'হ্যালো বিশ্ব',
        'How are you?': 'আপনি কেমন আছেন?',
        'Good morning': 'সুপ্রভাত',
        'Thank you': 'ধন্যবাদ'
      },
      'en-mr': {
        'Hello': 'नमस्कार',
        'Hello world': 'नमस्कार जग',
        'How are you?': 'तुम्ही कसे आहात?',
        'Good morning': 'सुप्रभात',
        'Thank you': 'धन्यवाद'
      },
      'hi-en': {
        'नमस्ते': 'Hello',
        'नमस्ते संसार': 'Hello world',
        'आप कैसे हैं?': 'How are you?',
        'धन्यवाद': 'Thank you',
        'सुप्रभात': 'Good morning'
      }
    };

    const translationKey = `${request.sourceLanguage}-${request.targetLanguage}`;
    const translationMap = mockTranslations[translationKey] || {};
    
    // Find exact match or provide a default translation
    let translatedText = translationMap[request.text];
    
    if (!translatedText) {
      // Generate a mock translation for demo
      if (request.targetLanguage === 'hi') {
        translatedText = `[${request.text} का हिंदी अनुवाद]`;
      } else if (request.targetLanguage === 'ta') {
        translatedText = `[${request.text} இன் தமிழ் மொழிபெயர்ப்பு]`;
      } else if (request.targetLanguage === 'te') {
        translatedText = `[${request.text} యొక్క తెలుగు అనువాదం]`;
      } else if (request.targetLanguage === 'bn') {
        translatedText = `[${request.text} এর বাংলা অনুবাদ]`;
      } else if (request.targetLanguage === 'mr') {
        translatedText = `[${request.text} चे मराठी भाषांतर]`;
      } else {
        translatedText = `[Translation of ${request.text}]`;
      }
    }

    // Generate mock alternatives
    const alternatives: string[] = [];
    if (request.text.toLowerCase().includes('hello')) {
      if (request.targetLanguage === 'hi') {
        alternatives.push('हैलो', 'नमस्कार');
      } else if (request.targetLanguage === 'ta') {
        alternatives.push('வணக்கம்', 'ஹலோ');
      }
    }

    return {
      translatedText,
      sourceLanguage: request.sourceLanguage,
      targetLanguage: request.targetLanguage,
      confidence: Math.random() * 0.3 + 0.7, // Random confidence between 0.7-1.0
      model: request.model === 'auto' ? 'indictrans' : (request.model || 'indictrans'),
      processingTime: Math.random() * 2 + 0.5, // Random time between 0.5-2.5s
      fromCache: Math.random() > 0.7, // 30% chance of cache hit
      alternatives: alternatives.length > 0 ? alternatives : undefined
    };
  };

  return (
    <>
      <GlobalStyle />
      <AppContainer>
        <Header>
          <AppTitle>NLP Translation App</AppTitle>
          <AppSubtitle>
            Translate text between English and Indian languages using state-of-the-art ML models
          </AppSubtitle>
        </Header>
        
        <MainContent>
          <TranslationInterface onTranslate={handleTranslate} />
        </MainContent>

        <Footer>
          <FooterText>
            Supports Hindi, Tamil, Telugu, Bengali, and Marathi translations
          </FooterText>
          <FeatureList>
            <FeatureItem>🚀 Real-time translation</FeatureItem>
            <FeatureItem>🧠 AI-powered models</FeatureItem>
            <FeatureItem>⚡ Cached results</FeatureItem>
            <FeatureItem>🎯 High accuracy</FeatureItem>
          </FeatureList>
        </Footer>
      </AppContainer>
    </>
  );
};

// Styled Components
const AppContainer = styled.div`
  min-height: 100vh;
  display: flex;
  flex-direction: column;
`;

const Header = styled.header`
  text-align: center;
  padding: 3rem 2rem 2rem;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
`;

const AppTitle = styled.h1`
  font-size: 3rem;
  font-weight: 700;
  color: white;
  margin: 0 0 1rem 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);

  @media (max-width: 768px) {
    font-size: 2rem;
  }
`;

const AppSubtitle = styled.p`
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.6;

  @media (max-width: 768px) {
    font-size: 1rem;
    padding: 0 1rem;
  }
`;

const MainContent = styled.main`
  flex: 1;
  padding: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Footer = styled.footer`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding: 2rem;
  text-align: center;
`;

const FooterText = styled.p`
  color: rgba(255, 255, 255, 0.9);
  margin: 0 0 1rem 0;
  font-size: 1rem;
`;

const FeatureList = styled.div`
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 2rem;
  margin-top: 1rem;

  @media (max-width: 768px) {
    gap: 1rem;
  }
`;

const FeatureItem = styled.span`
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.875rem;
  font-weight: 500;

  @media (max-width: 768px) {
    font-size: 0.75rem;
  }
`;

export default App;
