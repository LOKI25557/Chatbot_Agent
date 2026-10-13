import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { BookCard } from '../components/BookCard';
import { Book } from '../types';

const mockBookAvailable: Book = {
  id: 1,
  title: 'Clean Code',
  author: 'Robert C. Martin',
  isbn: '9780132350884',
  category: 'Computer Science',
  description: 'A handbook of agile software craftsmanship.',
  shelf_location: 'Floor 2, Shelf CS-101',
  total_copies: 3,
  available_copies: 2,
  borrowed_copies: 1,
  is_available: true,
  created_at: '2026-01-01T00:00:00Z',
  updated_at: '2026-01-01T00:00:00Z',
};

const mockBookUnavailable: Book = {
  ...mockBookAvailable,
  id: 2,
  title: 'The Pragmatic Programmer',
  author: 'David Thomas',
  total_copies: 2,
  available_copies: 0,
  borrowed_copies: 2,
  is_available: false,
};

describe('BookCard Component', () => {
  it('renders book title, author, category and shelf location accurately', () => {
    const handleSelect = vi.fn();
    render(<BookCard book={mockBookAvailable} onSelect={handleSelect} />);

    expect(screen.getByRole('heading', { name: /clean code/i })).toBeInTheDocument();
    expect(screen.getByText('by Robert C. Martin')).toBeInTheDocument();
    expect(screen.getByText('Computer Science')).toBeInTheDocument();
    expect(screen.getByText('Floor 2, Shelf CS-101')).toBeInTheDocument();
  });

  it('renders available copies badge when stock exists', () => {
    const handleSelect = vi.fn();
    render(<BookCard book={mockBookAvailable} onSelect={handleSelect} />);

    expect(screen.getByText('2 of 3 available')).toBeInTheDocument();
  });

  it('renders checked out status when available copies is 0', () => {
    const handleSelect = vi.fn();
    render(<BookCard book={mockBookUnavailable} onSelect={handleSelect} />);

    expect(screen.getByText('All checked out')).toBeInTheDocument();
  });

  it('triggers onSelect callback when clicking View Catalogue Details', () => {
    const handleSelect = vi.fn();
    render(<BookCard book={mockBookAvailable} onSelect={handleSelect} />);

    const button = screen.getByRole('button', { name: /view catalogue details/i });
    fireEvent.click(button);

    expect(handleSelect).toHaveBeenCalledWith(mockBookAvailable);
  });
});
