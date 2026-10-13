import React, { useState } from 'react';
import { Search, X, Check, Sparkles, Filter } from 'lucide-react';
import { motion } from 'framer-motion';

interface SearchHeroProps {
  onSearch: (query: string, onlyAvailable: boolean, category?: string) => void;
  categories: string[];
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
  onlyAvailable: boolean;
  onToggleOnlyAvailable: () => void;
  isLoading: boolean;
}

const EXAMPLE_QUERIES = [
  "Find Clean Code by Robert C. Martin",
  "Do you have books about Python programming?",
  "Search for books written by R. K. Narayan",
  "Find a book about artificial intelligence for beginners",
  "Show me available books about data structures"
];

export const SearchHero: React.FC<SearchHeroProps> = ({
  onSearch,
  categories,
  selectedCategory,
  onSelectCategory,
  onlyAvailable,
  onToggleOnlyAvailable,
  isLoading,
}) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim(), onlyAvailable, selectedCategory);
    }
  };

  const handleClear = () => {
    setQuery('');
  };

  const handleSelectExample = (example: string) => {
    setQuery(example);
    onSearch(example, onlyAvailable, selectedCategory);
  };

  return (
    <section className="relative pt-10 pb-8 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto text-center">
      {/* Refined subtle badge */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-200/80 dark:border-emerald-800/80 text-xs font-semibold uppercase tracking-wider mb-6 shadow-sm"
      >
        <Sparkles className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
        Factual Catalogue Search Powered by Groq AI
      </motion.div>

      {/* Primary Welcoming Prompt */}
      <motion.h1
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="font-serif text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight text-library-navy dark:text-white mb-4 leading-tight"
      >
        Welcome to your Library Assistant.
        <br />
        <span className="text-emerald-700 dark:text-emerald-400 italic font-serif">
          What book are you looking for today?
        </span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="text-slate-600 dark:text-slate-300 text-base sm:text-lg max-w-2xl mx-auto mb-8 font-normal"
      >
        Search by book title, author name, ISBN, subject, or natural-language query.
        All responses are grounded strictly in our physical and digital catalogue records.
      </motion.p>

      {/* Main Search Input Form */}
      <motion.form
        initial={{ opacity: 0, scale: 0.98 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.25 }}
        onSubmit={handleSubmit}
        className="relative max-w-3xl mx-auto"
      >
        <div className="relative flex items-center bg-white dark:bg-library-darkCard rounded-2xl shadow-book border border-library-border dark:border-library-darkBorder focus-within:ring-2 focus-within:ring-emerald-600 dark:focus-within:ring-emerald-400 focus-within:border-transparent transition-all overflow-hidden p-1.5">
          <div className="pl-4 text-slate-400">
            <Search className="w-6 h-6" />
          </div>

          <input
            type="text"
            id="book-search-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by title, author, ISBN, category, or ask naturally..."
            className="w-full py-3.5 px-4 bg-transparent text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none text-base sm:text-lg"
          />

          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 transition-colors"
              aria-label="Clear query"
            >
              <X className="w-5 h-5" />
            </button>
          )}

          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="flex items-center gap-2 px-6 py-3.5 rounded-xl bg-library-navy dark:bg-emerald-600 text-white font-medium hover:bg-slate-800 dark:hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shrink-0"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <span>Search</span>
              </>
            )}
          </button>
        </div>
      </motion.form>

      {/* Filter Row: Category & Availability */}
      <div className="mt-6 flex flex-wrap items-center justify-center gap-3 sm:gap-4 max-w-3xl mx-auto text-sm">
        {/* Availability Toggle */}
        <button
          type="button"
          onClick={onToggleOnlyAvailable}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all text-sm font-medium ${
            onlyAvailable
              ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
              : 'bg-white dark:bg-library-darkCard text-slate-600 dark:text-slate-300 border-slate-200 dark:border-slate-700 hover:border-slate-300'
          }`}
        >
          <div
            className={`w-4 h-4 rounded-full flex items-center justify-center text-white ${
              onlyAvailable ? 'bg-white/20' : 'border border-slate-300 dark:border-slate-600'
            }`}
          >
            {onlyAvailable && <Check className="w-3 h-3 text-white" />}
          </div>
          <span>Available for Borrowing Only</span>
        </button>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto py-1 max-w-full">
          <Filter className="w-4 h-4 text-slate-400 mr-1 shrink-0 hidden sm:inline" />
          <button
            type="button"
            onClick={() => {
              onSelectCategory('All');
              if (query.trim()) onSearch(query.trim(), onlyAvailable, 'All');
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
              selectedCategory === 'All'
                ? 'bg-library-navy dark:bg-slate-700 text-white'
                : 'bg-white dark:bg-library-darkCard text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:bg-slate-50'
            }`}
          >
            All Genres
          </button>
          {categories.slice(0, 5).map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => {
                const nextCat = selectedCategory === cat ? 'All' : cat;
                onSelectCategory(nextCat);
                if (query.trim()) onSearch(query.trim(), onlyAvailable, nextCat);
              }}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
                selectedCategory === cat
                  ? 'bg-emerald-700 dark:bg-emerald-600 text-white'
                  : 'bg-white dark:bg-library-darkCard text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:bg-slate-50'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Suggested Example Queries */}
      <div className="mt-7 text-left max-w-3xl mx-auto">
        <span className="text-xs uppercase font-semibold tracking-wider text-slate-400 dark:text-slate-500 block mb-2 text-center">
          Suggested Queries to Explore
        </span>
        <div className="flex flex-wrap items-center justify-center gap-2">
          {EXAMPLE_QUERIES.map((example, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => handleSelectExample(example)}
              className="text-xs px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700 hover:bg-amber-50 hover:border-amber-300 dark:hover:bg-slate-700 hover:text-amber-800 dark:hover:text-amber-300 transition-all text-left"
            >
              "{example}"
            </button>
          ))}
        </div>
      </div>
    </section>
  );
};
