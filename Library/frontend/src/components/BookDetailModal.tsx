import React, { useEffect } from 'react';
import { Book } from '../types';
import { X, MapPin, Hash, Building2, Calendar, CheckCircle2, AlertCircle, Bookmark } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface BookDetailModalProps {
  book: Book | null;
  onClose: () => void;
}

export const BookDetailModal: React.FC<BookDetailModalProps> = ({ book, onClose }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (book) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [book, onClose]);

  if (!book) return null;

  const isAvailable = book.total_copies > 0 ? book.available_copies > 0 : null;

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
        {/* Backdrop */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm transition-opacity"
        />

        {/* Modal Window */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 15 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 15 }}
          transition={{ duration: 0.2 }}
          className="relative w-full max-w-2xl bg-white dark:bg-library-darkCard rounded-3xl shadow-2xl border border-library-border dark:border-library-darkBorder overflow-hidden z-10"
        >
          {/* Header Banner */}
          <div className="p-6 sm:p-8 bg-gradient-to-r from-library-navy to-slate-900 text-white relative">
            <button
              onClick={onClose}
              className="absolute top-5 right-5 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors"
              aria-label="Close modal"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 mb-3">
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-400/20 text-amber-300 border border-amber-400/30">
                {book.category || 'General Collection'}
              </span>
              <span className="text-xs text-slate-400">
                Catalogue ID #{book.id}
              </span>
            </div>

            <h2 className="font-serif text-2xl sm:text-3xl font-bold tracking-tight text-white mb-2 leading-tight">
              {book.title}
            </h2>
            <p className="text-slate-300 font-medium text-base">
              {book.author ? `by ${book.author}` : <span className="italic">Author not recorded</span>}
            </p>
          </div>

          {/* Modal Body */}
          <div className="p-6 sm:p-8 space-y-6 max-h-[70vh] overflow-y-auto">
            {/* Availability & Physical Shelf Status Card */}
            <div className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-700">
                <div>
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
                    Catalogue & Circulation Status
                  </span>
                  {book.total_copies > 0 ? (
                    isAvailable ? (
                      <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-semibold text-base">
                        <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                        <span>Ready for Borrowing ({book.available_copies} copies currently on shelf)</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400 font-semibold text-base">
                        <AlertCircle className="w-5 h-5 text-amber-600" />
                        <span>Listed in catalogue, but all {book.total_copies} copies are currently checked out</span>
                      </div>
                    )
                  ) : (
                    <div className="flex items-center gap-2 text-slate-600 dark:text-slate-300 font-semibold text-base">
                      <Bookmark className="w-5 h-5 text-slate-500" />
                      <span>Catalogue presence only (copy circulation not tracked)</span>
                    </div>
                  )}
                </div>

                {/* Copies Counter */}
                {book.total_copies > 0 && (
                  <div className="flex items-center gap-3 bg-white dark:bg-slate-900 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 text-center shrink-0">
                    <div>
                      <span className="text-xs text-slate-400 block">Available</span>
                      <span className="text-base font-bold text-emerald-600 dark:text-emerald-400">
                        {book.available_copies}
                      </span>
                    </div>
                    <span className="text-slate-300 dark:text-slate-600">/</span>
                    <div>
                      <span className="text-xs text-slate-400 block">Total</span>
                      <span className="text-base font-bold text-slate-700 dark:text-slate-200">
                        {book.total_copies}
                      </span>
                    </div>
                  </div>
                )}
              </div>

              {/* Physical Shelf Location */}
              <div className="pt-4 flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                <MapPin className="w-4 h-4 text-amber-600 shrink-0" />
                <span className="text-slate-500 dark:text-slate-400">Physical Location:</span>
                <span className="font-semibold text-slate-900 dark:text-white">
                  {book.shelf_location || 'Not assigned to a specific shelf'}
                </span>
              </div>
            </div>

            {/* Description */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-400 mb-2">
                Synopsis & Description
              </h4>
              <p className="text-slate-700 dark:text-slate-300 text-sm leading-relaxed">
                {book.description || (
                  <span className="italic text-slate-400">
                    No summary description has been recorded for this catalogue item.
                  </span>
                )}
              </p>
            </div>

            {/* Structured Metadata Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800 text-sm">
              <div className="flex items-start gap-3">
                <Hash className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-xs text-slate-400 block">ISBN</span>
                  <span className="font-mono text-xs font-medium text-slate-800 dark:text-slate-200">
                    {book.isbn || 'Not recorded'}
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Building2 className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-xs text-slate-400 block">Publisher</span>
                  <span className="text-xs font-medium text-slate-800 dark:text-slate-200">
                    {book.publisher || 'Not recorded'}
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Calendar className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-xs text-slate-400 block">Publication Year</span>
                  <span className="text-xs font-medium text-slate-800 dark:text-slate-200">
                    {book.publication_year || 'Not recorded'}
                  </span>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Bookmark className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <div>
                  <span className="text-xs text-slate-400 block">Catalogue Added</span>
                  <span className="text-xs font-medium text-slate-800 dark:text-slate-200">
                    {new Date(book.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 sm:p-6 bg-slate-50 dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 flex justify-end">
            <button
              onClick={onClose}
              className="px-6 py-2.5 rounded-xl bg-library-navy dark:bg-slate-800 text-white text-sm font-medium hover:bg-slate-800 dark:hover:bg-slate-700 transition-colors"
            >
              Close Details
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
};
