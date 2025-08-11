import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';

// Mock the validation utility
jest.mock('../utils/validation', () => ({
  validateTranslationRequest: jest.fn(),
  sanitizeTextInput: jest.fn((text) => text),
  MAX_TEXT_LENGTH: 1000
}));

const mockValidateTranslationRequest = require('../utils/validation').validateTranslationRequest;

describe('App', () => {
  beforeEach(() => {
    mockValidateTranslationRequest.mockClear();
    mockValidateTranslationRequest.mockReturnValue({ isValid: true, errors: [] });
  });

  test('renders app with header and main components', () => {
    render(<App />);

    expect(screen.getByText('Multi-Language Translation Platform')).toBeInTheDocument();
    expect(screen.getByText('Powered by Advanced NLP Models')).toBeInTheDocument();
    expect(screen.getByText('Multi-Language Translation')).toBeInTheDocument();
    expect(screen.getByText('© 2024 Translation Platform. All rights reserved.')).toBeInTheDocument();
  });

  test('renders translation interface', () => {
    render(<App />);

    expect(screen.getByPlaceholderText('Enter text to translate...')).toBeInTheDocument();
    expect(screen.getByText('From')).toBeInTheDocument();
    expect(screen.getByText('To')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /translate/i })).toBeInTheDocument();
  });

  test('performs mock translation successfully', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello world');
    await user.click(translateButton);

    await waitFor(() => {
      // Should show some translated text (mock implementation)
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Time:/)).toBeInTheDocument();
  });

  test('handles translation from English to Hindi', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const sourceSelector = screen.getAllByRole('combobox')[0];
    const targetSelector = screen.getAllByRole('combobox')[1];
    const translateButton = screen.getByRole('button', { name: /translate/i });

    // Set language pair to English -> Hindi
    await user.selectOptions(sourceSelector, 'en');
    await user.selectOptions(targetSelector, 'hi');
    await user.type(textArea, 'Hello');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
    });
  });

  test('handles translation between Indian languages', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const sourceSelector = screen.getAllByRole('combobox')[0];
    const targetSelector = screen.getAllByRole('combobox')[1];
    const translateButton = screen.getByRole('button', { name: /translate/i });

    // Set language pair to Hindi -> Tamil
    await user.selectOptions(sourceSelector, 'hi');
    await user.selectOptions(targetSelector, 'ta');
    await user.type(textArea, 'नमस्ते');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
    });
  });

  test('shows loading state during translation', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Test text');
    await user.click(translateButton);

    // Should show loading state briefly
    expect(screen.getByText('Translating...')).toBeInTheDocument();

    // Wait for translation to complete
    await waitFor(() => {
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
    });
  });

  test('handles validation errors', async () => {
    const user = userEvent.setup();
    mockValidateTranslationRequest.mockReturnValue({
      isValid: false,
      errors: ['Text is required']
    });

    render(<App />);

    const translateButton = screen.getByRole('button', { name: /translate/i });
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText('Please fix the following issues:')).toBeInTheDocument();
    });
    
    expect(screen.getByText('Text is required')).toBeInTheDocument();
  });

  test('displays confidence scores in results', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText(/Confidence:/)).toBeInTheDocument();
    });
  });

  test('shows processing time in results', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Hello');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText(/Time:/)).toBeInTheDocument();
    });
  });

  test('handles empty text input', () => {
    render(<App />);

    const translateButton = screen.getByRole('button', { name: /translate/i });
    
    // Button should be disabled when no text is entered
    expect(translateButton).toBeDisabled();
  });

  test('enables translate button when text is entered', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const translateButton = screen.getByRole('button', { name: /translate/i });

    await user.type(textArea, 'Some text');
    
    expect(translateButton).toBeEnabled();
  });

  test('clears translation result when text is cleared', async () => {
    const user = userEvent.setup();
    render(<App />);

    const textArea = screen.getByPlaceholderText('Enter text to translate...');
    const clearButton = screen.getByRole('button', { name: /clear/i });
    const translateButton = screen.getByRole('button', { name: /translate/i });

    // First translate something
    await user.type(textArea, 'Hello');
    await user.click(translateButton);

    await waitFor(() => {
      expect(screen.getByText(/Model:/)).toBeInTheDocument();
    });

    // Then clear
    await user.click(clearButton);

    expect(textArea).toHaveValue('');
    expect(screen.getByText('Your translation will appear here')).toBeInTheDocument();
  });
});
