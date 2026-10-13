import React from 'react';
import { SearchX, RotateCcw, BookOpen } from 'lucide-react';
import { motion } from 'framer-motion';

interface EmptyStateProps {
  query?: string;
  onReset: () => void;
  onBrowseAll?: () => void;
}

export const EmptyState: React.FC<EmptyStateProps> = ({ query, onReset, onBrowseAll }) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="p-8 sm:p-12 text-center rounded-3xl bg-white dark:bg-library-darkCard border border-library-border dark:border-library-darkBorder max-w-2xl mx-auto shadow-sm"
    >
      <div className="w-16 h-16 rounded-2xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto mb-5 border border-amber-200 dark:border-amber-800">
        <SearchX className="w-8 h-8" />
      </div>

      <h3 className="font-serif text-2xl font-bold text-slate-900 dark:text-white mb-2">
        {query ? `Not Listed in Library Catalogue` : 'No Books Found'}
      </h3>

      <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed mb-6 max-w-md mx-auto">
        {query ? (
          <>
            We searched the active catalogue but found no matches for{' '}
            <span className="font-semibold text-slate-900 dark:text-slate-100">"{query}"</span>.
            Our library may not currently hold this title, or it may be catalogued under a different title or author.
          </>
        ) : (
          'There are no catalogue items matching your currently active filters.'
        )}
      </p>

      <div className="flex flex-wrap items-center justify-center gap-3">
        <button
          onClick={onReset}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 text-sm font-medium transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
          <span>Clear Search & Filters</span>
        </button>

        {onBrowseAll && (
          <button
            onClick={onBrowseAll}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-library-navy dark:bg-emerald-600 hover:bg-slate-800 dark:hover:bg-emerald-500 text-white text-sm font-medium transition-colors shadow-sm"
          >
            <BookOpen className="w-4 h-4" />
            <span>Browse Full Catalogue</span>
          </button>
        )}
      </div>
    </motion.div>
  );
};
