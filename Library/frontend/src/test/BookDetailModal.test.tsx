import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { BookDetailModal } from '../components/BookDetailModal';
import { Book } from '../types';

const mockBook: Book = {
  id: 42,
  title: 'Artificial Intelligence: A Modern Approach',
  author: 'Stuart Russell and Peter Norvig',
  isbn: '9780136042594',
  publisher: 'Pearson',
  publication_year: 2020,
  category: 'Artificial Intelligence',
  description: 'The standard leading textbook in AI algorithms and principles.',
  shelf_location: 'Floor 3, Shelf AI-301',
  total_copies: 5,
  available_copies: 4,
  borrowed_copies: 1,
  is_available: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

describe('BookDetailModal Component', () => {
  it('does not render when book is null', () => {
    const { container } = render(<BookDetailModal book={null} onClose={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders complete catalogue metadata and shelf location', () => {
    render(<BookDetailModal book={mockBook} onClose={vi.fn()} />);

    expect(screen.getByText('Artificial Intelligence: A Modern Approach')).toBeInTheDocument();
    expect(screen.getByText('by Stuart Russell and Peter Norvig')).toBeInTheDocument();
    expect(screen.getByText('Floor 3, Shelf AI-301')).toBeInTheDocument();
    expect(screen.getByText('9780136042594')).toBeInTheDocument();
    expect(screen.getByText('Pearson')).toBeInTheDocument();
    expect(screen.getByText('2020')).toBeInTheDocument();
    expect(screen.getByText('The standard leading textbook in AI algorithms and principles.')).toBeInTheDocument();
  });

  it('displays accurate available vs total copy counts', () => {
    render(<BookDetailModal book={mockBook} onClose={vi.fn()} />);

    expect(screen.getByText(/Ready for Borrowing/i)).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument(); // available
    expect(screen.getByText('5')).toBeInTheDocument(); // total
  });

  it('calls onClose when close buttons are clicked', () => {
    const onClose = vi.fn();
    render(<BookDetailModal book={mockBook} onClose={onClose} />);

    const closeButton = screen.getByRole('button', { name: /close details/i });
    fireEvent.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });
});
