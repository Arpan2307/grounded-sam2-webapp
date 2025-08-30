import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders upload form', () => {
  render(<App />);
  const uploadElement = screen.getByText(/upload video/i);
  expect(uploadElement).toBeInTheDocument();
});

test('renders prompt input', () => {
  render(<App />);
  const promptElement = screen.getByPlaceholderText(/enter text prompt/i);
  expect(promptElement).toBeInTheDocument();
});

test('renders video player', () => {
  render(<App />);
  const videoPlayerElement = screen.getByText(/video output/i);
  expect(videoPlayerElement).toBeInTheDocument();
});

test('renders progress bar', () => {
  render(<App />);
  const progressBarElement = screen.getByRole('progressbar');
  expect(progressBarElement).toBeInTheDocument();
});