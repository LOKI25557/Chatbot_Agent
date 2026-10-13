import React from 'react';
import { Book } from '../types';
import { MapPin, BookOpen, Layers, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface BookCardProps {
  book: Book;
  onSelect: (book: Book) => void;
  index?: number;
}

export const BookCard: React.FC<BookCardProps> = ({ book, onSelect, index = 0 }) => {
  const isAvailable = book.total_copies > 0 ? book.available_copies > 0 : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: Math.min(index * 0.05, 0.4) }}
      className="group flex flex-col justify-between bg-white dark:bg-library-darkCard rounded-2xl border border-library-border dark:border-library-darkBorder p-5 shadow-sm hover:shadow-book-hover hover:-translate-y-1 transition-all duration-300"
    >
      <div>
        {/* Cover / Placeholder & Status Badge */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            {/* Elegant Book Spine/Cover Placeholder */}
            {book.cover_image_url ? (
              <img
                src={book.cover_image_url}
                alt={book.title}
                className="w-14 h-20 object-cover rounded-lg shadow-sm border border-slate-200 dark:border-slate-700"
                onError={(e) => {
                  // Fallback to stylized placeholder on broken image
                  (e.target as HTMLElement).style.display = 'none';
                }}
              />
            ) : (
              <div className="w-14 h-20 rounded-lg bg-gradient-to-br from-slate-800 to-slate-900 text-amber-200 flex flex-col items-center justify-center p-1.5 shadow-sm border border-slate-700 text-center select-none">
                <BookOpen className="w-5 h-5 mb-1 opacity-70" />
                <span className="text-[9px] font-serif leading-tight font-bold line-clamp-2 uppercase">
                  {book.title.slice(0, 16)}
                </span>
              </div>
            )}

            <div>
              {/* Category pill */}
              {book.category && (
                <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 mb-1.5">
                  {book.category}
                </span>
              )}
              {/* Publication Year if present */}
              {book.publication_year && (
                <span className="text-xs text-slate-400 block font-normal">
                  Published {book.publication_year}
                </span>
              )}
            </div>
          </div>

          {/* Availability Status Badge */}
          <div>
            {book.total_copies > 0 ? (
              isAvailable ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/70 text-emerald-800 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                  <CheckCircle className="w-3 h-3 text-emerald-600 dark:text-emerald-400" />
                  <span>{book.available_copies} of {book.total_copies} available</span>
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 dark:bg-amber-950/70 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                  <AlertCircle className="w-3 h-3 text-amber-600 dark:text-amber-400" />
                  <span>All checked out</span>
                </span>
              )
            ) : (
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                <Layers className="w-3 h-3" />
                <span>Reference only</span>
              </span>
            )}
          </div>
        </div>

        {/* Title & Author */}
        <h3 className="font-serif text-lg font-bold text-slate-900 dark:text-white group-hover:text-emerald-700 dark:group-hover:text-emerald-400 transition-colors line-clamp-2 leading-snug mb-1">
          {book.title}
        </h3>
        <p className="text-sm font-medium text-slate-600 dark:text-slate-300 mb-3">
          {book.author ? `by ${book.author}` : <span className="italic text-slate-400">Author not recorded</span>}
        </p>

        {/* Short Description if present */}
        {book.description ? (
          <p className="text-xs text-slate-500 dark:text-slate-400 line-clamp-2 mb-4 leading-relaxed">
            {book.description}
          </p>
        ) : (
          <p className="text-xs italic text-slate-400 dark:text-slate-500 mb-4">
            No summary description recorded.
          </p>
        )}
      </div>

      <div>
        {/* Shelf location indicator */}
        <div className="pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-3">
          <div className="flex items-center gap-1.5 truncate">
            <MapPin className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" />
            <span className="truncate">
              {book.shelf_location ? (
                <span className="font-medium text-slate-700 dark:text-slate-300">{book.shelf_location}</span>
              ) : (
                <span className="italic">Shelf location unassigned</span>
              )}
            </span>
          </div>

          {book.isbn && (
            <span className="text-[11px] font-mono text-slate-400 shrink-0">
              ISBN {book.isbn.slice(-6)}
            </span>
          )}
        </div>

        {/* View Details Action Button */}
        <button
          onClick={() => onSelect(book)}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-slate-800/80 hover:bg-emerald-50 dark:hover:bg-emerald-950/60 text-slate-700 dark:text-slate-200 hover:text-emerald-800 dark:hover:text-emerald-300 border border-slate-200 dark:border-slate-700 hover:border-emerald-300 transition-colors"
        >
          <span>View Catalogue Details</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </motion.div>
  );
};
