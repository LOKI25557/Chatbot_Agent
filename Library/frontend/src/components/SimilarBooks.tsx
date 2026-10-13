import React from 'react';
import { Book } from '../types';
import { Sparkles, ArrowRight, BookOpen, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';

interface SimilarBooksProps {
  books: Book[];
  onSelect: (book: Book) => void;
  title?: string;
  subtitle?: string;
}

export const SimilarBooks: React.FC<SimilarBooksProps> = ({
  books,
  onSelect,
  title = "Related Books in Our Collection",
  subtitle = "These recommendations genuinely exist in our library catalogue.",
}) => {
  if (!books || books.length === 0) return null;

  return (
    <div className="mt-10 pt-8 border-t border-library-border dark:border-library-darkBorder">
      <div className="flex items-center gap-2 mb-1">
        <Sparkles className="w-5 h-5 text-amber-500" />
        <h3 className="font-serif text-2xl font-bold text-library-navy dark:text-white">
          {title}
        </h3>
      </div>
      <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">
        {subtitle}
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {books.map((book, idx) => (
          <motion.div
            key={book.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.08 }}
            onClick={() => onSelect(book)}
            className="group p-4 rounded-2xl bg-white dark:bg-library-darkCard border border-library-border dark:border-library-darkBorder hover:border-amber-400 dark:hover:border-amber-400 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="flex items-start justify-between gap-2 mb-2">
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-amber-50 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  {book.category || 'General'}
                </span>
                {book.available_copies > 0 && (
                  <span className="text-[11px] text-emerald-600 dark:text-emerald-400 flex items-center gap-1 font-medium">
                    <CheckCircle className="w-3 h-3" />
                    Available
                  </span>
                )}
              </div>

              <h4 className="font-serif font-bold text-slate-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors line-clamp-1 text-base">
                {book.title}
              </h4>
              <p className="text-xs text-slate-600 dark:text-slate-400 mb-2">
                {book.author ? `by ${book.author}` : 'Author unknown'}
              </p>
              {book.description && (
                <p className="text-xs text-slate-500 line-clamp-2 leading-relaxed">
                  {book.description}
                </p>
              )}
            </div>

            <div className="mt-3 pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
              <span className="text-[11px]">{book.shelf_location || 'Shelf not recorded'}</span>
              <span className="font-semibold text-amber-600 dark:text-amber-400 flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                View <ArrowRight className="w-3 h-3" />
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};
