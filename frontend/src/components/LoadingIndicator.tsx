import React from 'react';
import styled, { keyframes } from 'styled-components';

interface LoadingIndicatorProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  message?: string;
  progress?: number; // 0-100 for progress indication
  className?: string;
}

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  size = 'medium',
  color = '#3b82f6',
  message,
  progress,
  className
}) => {
  const sizeConfig = {
    small: { spinner: 16, text: '0.75rem' },
    medium: { spinner: 24, text: '0.875rem' },
    large: { spinner: 32, text: '1rem' }
  };

  const config = sizeConfig[size];

  return (
    <Container 
      className={className}
      role="status"
      aria-label="Loading"
      aria-live="polite"
    >
      {progress !== undefined ? (
        <ProgressContainer>
          <ProgressBar>
            <ProgressFill progress={progress} color={color} />
          </ProgressBar>
          <ProgressText size={config.text}>
            {Math.round(progress)}%
          </ProgressText>
          {message && (
            <LoadingText size={config.text}>{message}</LoadingText>
          )}
        </ProgressContainer>
      ) : (
        <SpinnerContainer>
          <Spinner size={config.spinner} color={color}>
            <div></div>
            <div></div>
            <div></div>
            <div></div>
          </Spinner>
          {message && (
            <LoadingText size={config.text}>{message}</LoadingText>
          )}
        </SpinnerContainer>
      )}
    </Container>
  );
};

// Keyframes for animations
const spin = keyframes`
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
`;

const pulse = keyframes`
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
`;

// Styled Components
const Container = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SpinnerContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
`;

const Spinner = styled.div<{ size: number; color: string }>`
  display: inline-block;
  position: relative;
  width: ${props => props.size}px;
  height: ${props => props.size}px;

  div {
    box-sizing: border-box;
    display: block;
    position: absolute;
    width: ${props => props.size * 0.8}px;
    height: ${props => props.size * 0.8}px;
    margin: ${props => props.size * 0.1}px;
    border: ${props => Math.max(2, props.size * 0.1)}px solid ${props => props.color};
    border-radius: 50%;
    animation: ${spin} 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
    border-color: ${props => props.color} transparent transparent transparent;
  }

  div:nth-child(1) {
    animation-delay: -0.45s;
  }

  div:nth-child(2) {
    animation-delay: -0.3s;
  }

  div:nth-child(3) {
    animation-delay: -0.15s;
  }
`;

const LoadingText = styled.p<{ size: string }>`
  margin: 0;
  font-size: ${props => props.size};
  color: #6b7280;
  text-align: center;
`;

const ProgressContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  max-width: 200px;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
`;

const ProgressFill = styled.div<{ progress: number; color: string }>`
  height: 100%;
  width: ${props => props.progress}%;
  background: ${props => props.color};
  border-radius: 4px;
  transition: width 0.3s ease;
`;

const ProgressText = styled.span<{ size: string }>`
  font-size: ${props => props.size};
  color: #374151;
  font-weight: 500;
`;

// Alternative dot-style loading indicator
export const DotLoadingIndicator: React.FC<Pick<LoadingIndicatorProps, 'size' | 'color' | 'className'>> = ({
  size = 'medium',
  color = '#3b82f6',
  className
}) => {
  const sizeConfig = {
    small: 4,
    medium: 6,
    large: 8
  };

  const dotSize = sizeConfig[size];

  return (
    <DotContainer className={className}>
      <Dot size={dotSize} color={color} delay={0} />
      <Dot size={dotSize} color={color} delay={0.1} />
      <Dot size={dotSize} color={color} delay={0.2} />
    </DotContainer>
  );
};

const DotContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const Dot = styled.div<{ size: number; color: string; delay: number }>`
  width: ${props => props.size}px;
  height: ${props => props.size}px;
  background: ${props => props.color};
  border-radius: 50%;
  animation: ${pulse} 1.4s ease-in-out ${props => props.delay}s infinite both;
`;

// Alternative spinning bars indicator
export const BarsLoadingIndicator: React.FC<Pick<LoadingIndicatorProps, 'size' | 'color' | 'className'>> = ({
  size = 'medium',
  color = '#3b82f6',
  className
}) => {
  const sizeConfig = {
    small: { height: 12, width: 2 },
    medium: { height: 16, width: 3 },
    large: { height: 20, width: 4 }
  };

  const config = sizeConfig[size];

  return (
    <BarsContainer className={className}>
      {[0, 1, 2, 3, 4].map((index) => (
        <Bar
          key={index}
          height={config.height}
          width={config.width}
          color={color}
          delay={index * 0.1}
        />
      ))}
    </BarsContainer>
  );
};

const BarsContainer = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 1px;
`;

const barAnimation = keyframes`
  0%, 40%, 100% {
    transform: scaleY(0.4);
  }
  20% {
    transform: scaleY(1);
  }
`;

const Bar = styled.div<{ height: number; width: number; color: string; delay: number }>`
  width: ${props => props.width}px;
  height: ${props => props.height}px;
  background: ${props => props.color};
  animation: ${barAnimation} 1s ease-in-out ${props => props.delay}s infinite;
  transform-origin: bottom;
`;

export default LoadingIndicator;
