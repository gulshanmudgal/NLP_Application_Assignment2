import React from 'react';
import { render, screen } from '@testing-library/react';
import LoadingIndicator from '../../components/LoadingIndicator';

describe('LoadingIndicator', () => {
  test('renders loading indicator by default', () => {
    render(<LoadingIndicator />);
    
    // Check for loading container
    const container = screen.getByRole('status');
    expect(container).toBeInTheDocument();
    expect(container).toHaveAttribute('aria-label', 'Loading');
  });

  test('renders with custom message', () => {
    render(<LoadingIndicator message="Translating your text..." />);
    
    expect(screen.getByText('Translating your text...')).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('renders with progress value', () => {
    render(<LoadingIndicator progress={75} />);
    
    const progressContainer = screen.getByRole('status');
    expect(progressContainer).toBeInTheDocument();
  });

  test('renders different sizes', () => {
    const { rerender } = render(<LoadingIndicator size="small" />);
    expect(screen.getByRole('status')).toBeInTheDocument();

    rerender(<LoadingIndicator size="medium" />);
    expect(screen.getByRole('status')).toBeInTheDocument();

    rerender(<LoadingIndicator size="large" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('applies custom className when provided', () => {
    render(<LoadingIndicator className="custom-loading" />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('displays custom message', () => {
    const customMessage = 'Processing request...';
    
    render(<LoadingIndicator message={customMessage} />);
    expect(screen.getByText(customMessage)).toBeInTheDocument();
  });

  test('renders accessibility attributes correctly', () => {
    render(<LoadingIndicator message="Loading content" />);
    
    const statusElement = screen.getByRole('status');
    expect(statusElement).toHaveAttribute('aria-label', 'Loading');
    expect(statusElement).toHaveAttribute('aria-live', 'polite');
  });

  test('renders without message when not provided', () => {
    render(<LoadingIndicator />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.queryByText(/processing/i)).not.toBeInTheDocument();
  });

  test('handles progress values correctly', () => {
    // Test with 0% progress
    const { rerender } = render(<LoadingIndicator progress={0} />);
    expect(screen.getByRole('status')).toBeInTheDocument();

    // Test with 50% progress
    rerender(<LoadingIndicator progress={50} />);
    expect(screen.getByRole('status')).toBeInTheDocument();

    // Test with 100% progress
    rerender(<LoadingIndicator progress={100} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('renders with custom color', () => {
    render(<LoadingIndicator color="#ff0000" />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('renders progress indicator when progress is provided', () => {
    render(<LoadingIndicator progress={45} message="Loading..." />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('renders spinner when no progress is provided', () => {
    render(<LoadingIndicator message="Loading..." />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});
