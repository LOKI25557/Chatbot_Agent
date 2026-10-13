import React, { useState, useEffect } from 'react';
import { Book, BookCreateInput } from '../types';
import { X, Check, AlertCircle } from 'lucide-react';

interface BookFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: BookCreateInput) => Promise<void>;
  initialBook?: Book | null;
  isLoading: boolean;
}

export const BookFormModal: React.FC<BookFormModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialBook,
  isLoading,
}) => {
  const [formData, setFormData] = useState<BookCreateInput>({
    title: '',
    author: '',
    isbn: '',
    category: '',
    publisher: '',
    publication_year: new Date().getFullYear(),
    shelf_location: '',
    total_copies: 1,
    available_copies: 1,
    description: '',
    cover_image_url: '',
  });

  const [validationError, setValidationError] = useState<string | null>(null);

  useEffect(() => {
    if (initialBook) {
      setFormData({
        title: initialBook.title,
        author: initialBook.author || '',
        isbn: initialBook.isbn || '',
        category: initialBook.category || '',
        publisher: initialBook.publisher || '',
        publication_year: initialBook.publication_year || undefined,
        shelf_location: initialBook.shelf_location || '',
        total_copies: initialBook.total_copies,
        available_copies: initialBook.available_copies,
        description: initialBook.description || '',
        cover_image_url: initialBook.cover_image_url || '',
      });
    } else {
      setFormData({
        title: '',
        author: '',
        isbn: '',
        category: '',
        publisher: '',
        publication_year: new Date().getFullYear(),
        shelf_location: '',
        total_copies: 1,
        available_copies: 1,
        description: '',
        cover_image_url: '',
      });
    }
    setValidationError(null);
  }, [initialBook, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setValidationError(null);

    if (!formData.title.trim()) {
      setValidationError('Book title is required.');
      return;
    }

    if (formData.total_copies < 0 || formData.available_copies < 0) {
      setValidationError('Copy counts must be non-negative.');
      return;
    }

    if (formData.available_copies > formData.total_copies) {
      setValidationError(
        `Available copies (${formData.available_copies}) cannot exceed total copies (${formData.total_copies}).`
      );
      return;
    }

    try {
      await onSubmit(formData);
      onClose();
    } catch (err: any) {
      setValidationError(err.message || 'Failed to save book.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-xl bg-white dark:bg-library-darkCard rounded-3xl shadow-2xl border border-library-border dark:border-library-darkBorder overflow-hidden z-10 max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-library-border dark:border-library-darkBorder flex items-center justify-between bg-slate-50 dark:bg-slate-900">
          <h3 className="font-serif text-xl font-bold text-slate-900 dark:text-white">
            {initialBook ? 'Edit Catalogue Book' : 'Add New Book to Catalogue'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto flex-1">
          {validationError && (
            <div className="p-3.5 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{validationError}</span>
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Title *
            </label>
            <input
              type="text"
              required
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="e.g. Clean Architecture"
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          {/* Author & ISBN */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Author
              </label>
              <input
                type="text"
                value={formData.author || ''}
                onChange={(e) => setFormData({ ...formData, author: e.target.value })}
                placeholder="e.g. Robert C. Martin"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                ISBN
              </label>
              <input
                type="text"
                value={formData.isbn || ''}
                onChange={(e) => setFormData({ ...formData, isbn: e.target.value })}
                placeholder="e.g. 9780134494166"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Category & Shelf Location */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Category / Genre
              </label>
              <input
                type="text"
                value={formData.category || ''}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                placeholder="e.g. Software Engineering"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Physical Shelf Location
              </label>
              <input
                type="text"
                value={formData.shelf_location || ''}
                onChange={(e) => setFormData({ ...formData, shelf_location: e.target.value })}
                placeholder="e.g. Floor 2, Shelf CS-105"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Copy Counts (Total & Available) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-3.5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Total Copies
              </label>
              <input
                type="number"
                min="0"
                value={formData.total_copies}
                onChange={(e) =>
                  setFormData({ ...formData, total_copies: parseInt(e.target.value) || 0 })
                }
                className="w-full px-3.5 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Available Copies
              </label>
              <input
                type="number"
                min="0"
                max={formData.total_copies}
                value={formData.available_copies}
                onChange={(e) =>
                  setFormData({ ...formData, available_copies: parseInt(e.target.value) || 0 })
                }
                className="w-full px-3.5 py-2 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Publisher & Year */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Publisher
              </label>
              <input
                type="text"
                value={formData.publisher || ''}
                onChange={(e) => setFormData({ ...formData, publisher: e.target.value })}
                placeholder="e.g. Prentice Hall"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
                Publication Year
              </label>
              <input
                type="number"
                value={formData.publication_year || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    publication_year: e.target.value ? parseInt(e.target.value) : undefined,
                  })
                }
                placeholder="e.g. 2017"
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-500 mb-1">
              Description
            </label>
            <textarea
              rows={3}
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Short synopsis or library catalog note..."
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>

          {/* Action Buttons */}
          <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 text-sm font-medium hover:bg-slate-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2.5 rounded-xl bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-500 transition-colors flex items-center gap-2 shadow-md disabled:opacity-50"
            >
              <Check className="w-4 h-4" />
              <span>{initialBook ? 'Save Changes' : 'Add to Catalogue'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
