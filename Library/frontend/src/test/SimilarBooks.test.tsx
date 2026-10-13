import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { SimilarBooks } from '../components/SimilarBooks';
import { Book } from '../types';

const mockSimilarBooks: Book[] = [
  {
    id: 10,
    title: 'The Guide',
    author: 'R. K. Narayan',
    isbn: '9780143039648',
    publisher: 'Penguin Classics',
    publication_year: 1958,
    category: 'Fiction',
    description: 'Masterpiece novel of transformation.',
    shelf_location: 'Floor 1, Shelf LIT-407',
    total_copies: 3,
    available_copies: 2,
    borrowed_copies: 1,
    is_available: true,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z',
  },
];

describe('SimilarBooks Component', () => {
  it('does not render when book list is empty', () => {
    const { container } = render(<SimilarBooks books={[]} onSelect={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders verified recommendation cards with title and author', () => {
    render(<SimilarBooks books={mockSimilarBooks} onSelect={vi.fn()} />);

    expect(screen.getByText('The Guide')).toBeInTheDocument();
    expect(screen.getByText('by R. K. Narayan')).toBeInTheDocument();
    expect(screen.getByText('Floor 1, Shelf LIT-407')).toBeInTheDocument();
  });

  it('triggers onSelect when recommendation card is clicked', () => {
    const onSelect = vi.fn();
    render(<SimilarBooks books={mockSimilarBooks} onSelect={onSelect} />);

    const card = screen.getByText('The Guide');
    fireEvent.click(card);

    expect(onSelect).toHaveBeenCalledWith(mockSimilarBooks[0]);
  });
});
