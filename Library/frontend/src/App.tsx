import React, { useState, useEffect } from 'react';
import { Book, SearchResponse } from './types';
import { api } from './services/api';
import { Navbar } from './components/Navbar';
import { SearchHero } from './components/SearchHero';
import { BookCard } from './components/BookCard';
import { BookDetailModal } from './components/BookDetailModal';
import { AIChatDrawer } from './components/AIChatDrawer';
import { SimilarBooks } from './components/SimilarBooks';
import { EmptyState } from './components/EmptyState';
import { LoadingSkeleton } from './components/LoadingSkeleton';
import { AdminDashboard } from './components/AdminDashboard';
import {
  Sparkles,
  BookOpen,
  CheckCircle,
  AlertTriangle,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  Info,
} from 'lucide-react';
import { motion } from 'framer-motion';

export const App: React.FC = () => {
  // Theme state
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return (
      localStorage.getItem('athenaeum_theme') === 'dark' ||
      (!('athenaeum_theme' in localStorage) &&
        window.matchMedia('(prefers-color-scheme: dark)').matches)
    );
  });

  // Admin view toggle
  const [isAdminView, setIsAdminView] = useState(false);

  // Chat drawer toggle
  const [isChatOpen, setIsChatOpen] = useState(false);

  // Selected book for details modal
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);

  // Search state
  const [activeQuery, setActiveQuery] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [onlyAvailable, setOnlyAvailable] = useState<boolean>(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Default browse catalogue state (when no active query)
  const [browseBooks, setBrowseBooks] = useState<Book[]>([]);
  const [browsePage, setBrowsePage] = useState(1);
  const [browseTotalPages, setBrowseTotalPages] = useState(1);
  const [browseTotal, setBrowseTotal] = useState(0);
  const [isBrowseLoading, setIsBrowseLoading] = useState(false);

  // Apply dark mode class to root HTML
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('athenaeum_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('athenaeum_theme', 'light');
    }
  }, [darkMode]);

  // Load categories and initial catalog on mount
  useEffect(() => {
    loadCategories();
    loadBrowseCatalog(1, selectedCategory, onlyAvailable);
  }, []);

  const loadCategories = async () => {
    try {
      const cats = await api.getCategories();
      setCategories(cats);
    } catch (err) {
      console.error('Failed to load categories', err);
    }
  };

  const loadBrowseCatalog = async (page = 1, category = 'All', avail = false) => {
    setIsBrowseLoading(true);
    try {
      const res = await api.getBooks(page, 9, undefined, category, avail);
      setBrowseBooks(res.items);
      setBrowsePage(res.page);
      setBrowseTotalPages(res.pages);
      setBrowseTotal(res.total);
    } catch (err) {
      console.error('Failed to load browse catalogue', err);
    } finally {
      setIsBrowseLoading(false);
    }
  };

  const handleSearch = async (
    query: string,
    onlyAvail: boolean = onlyAvailable,
    cat: string = selectedCategory
  ) => {
    if (!query.trim()) {
      handleResetSearch();
      return;
    }

    setIsSearching(true);
    setSearchError(null);
    setActiveQuery(query);

    try {
      const response = await api.search(query, onlyAvail, cat);
      setSearchResponse(response);
    } catch (err: any) {
      setSearchError(err.message || 'Failed to search catalogue.');
      setSearchResponse(null);
    } finally {
      setIsSearching(false);
    }
  };

  const handleResetSearch = () => {
    setActiveQuery('');
    setSearchResponse(null);
    setSearchError(null);
    loadBrowseCatalog(1, selectedCategory, onlyAvailable);
  };

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    if (activeQuery) {
      handleSearch(activeQuery, onlyAvailable, category);
    } else {
      loadBrowseCatalog(1, category, onlyAvailable);
    }
  };

  const handleToggleOnlyAvailable = () => {
    const nextVal = !onlyAvailable;
    setOnlyAvailable(nextVal);
    if (activeQuery) {
      handleSearch(activeQuery, nextVal, selectedCategory);
    } else {
      loadBrowseCatalog(1, selectedCategory, nextVal);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-library-bg dark:bg-library-darkBg text-slate-800 dark:text-slate-100 transition-colors duration-300">
      {/* Navbar */}
      <Navbar
        darkMode={darkMode}
        onToggleTheme={() => setDarkMode(!darkMode)}
        isAdminView={isAdminView}
        onToggleAdmin={() => setIsAdminView(!isAdminView)}
        onOpenChat={() => setIsChatOpen(true)}
      />

      {/* Main Content Area */}
      <main className="flex-1 pb-16">
        {isAdminView ? (
          <AdminDashboard />
        ) : (
          <>
            {/* Search Hero Section */}
            <SearchHero
              onSearch={handleSearch}
              categories={categories}
              selectedCategory={selectedCategory}
              onSelectCategory={handleCategoryChange}
              onlyAvailable={onlyAvailable}
              onToggleOnlyAvailable={handleToggleOnlyAvailable}
              isLoading={isSearching}
            />

            {/* Results / Catalogue Container */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
              {/* Error Message */}
              {searchError && (
                <div className="max-w-2xl mx-auto mb-8 p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-sm flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 shrink-0" />
                    <span>{searchError}</span>
                  </div>
                  <button
                    onClick={() => handleSearch(activeQuery)}
                    className="text-xs font-semibold underline hover:no-underline"
                  >
                    Retry
                  </button>
                </div>
              )}

              {/* SEARCH MODE: Search was executed */}
              {activeQuery && searchResponse && (
                <div className="space-y-8">
                  {/* Factual AI Explanation Banner (Strictly Grounded) */}
                  <motion.div
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`p-5 rounded-2xl border transition-all ${
                      searchResponse.status === 'found'
                        ? 'bg-emerald-50/80 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800'
                        : searchResponse.status === 'multiple_found'
                        ? 'bg-blue-50/80 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800'
                        : 'bg-amber-50/80 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="p-2 rounded-xl bg-white dark:bg-slate-900 shadow-sm shrink-0 mt-0.5">
                        <Sparkles
                          className={`w-5 h-5 ${
                            searchResponse.status === 'found'
                              ? 'text-emerald-600'
                              : searchResponse.status === 'multiple_found'
                              ? 'text-blue-600'
                              : 'text-amber-600'
                          }`}
                        />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between gap-2 mb-1">
                          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                            Catalogue Grounded Finding · Matched by{' '}
                            <span className="font-mono text-slate-700 dark:text-slate-300">
                              {searchResponse.matched_by}
                            </span>
                          </span>

                          <button
                            onClick={handleResetSearch}
                            className="text-xs text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 flex items-center gap-1 font-medium"
                          >
                            <RotateCcw className="w-3.5 h-3.5" />
                            <span>Clear Results</span>
                          </button>
                        </div>
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-100 leading-relaxed">
                          {searchResponse.ai_explanation}
                        </p>
                      </div>
                    </div>
                  </motion.div>

                  {/* Matching Books Grid */}
                  {searchResponse.books.length > 0 ? (
                    <div>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-serif text-xl font-bold text-slate-900 dark:text-white">
                          Matching Catalogue Records ({searchResponse.books.length})
                        </h3>
                      </div>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {searchResponse.books.map((book, idx) => (
                          <BookCard
                            key={book.id}
                            book={book}
                            index={idx}
                            onSelect={setSelectedBook}
                          />
                        ))}
                      </div>
                    </div>
                  ) : (
                    /* Book Not Found Empty State */
                    <EmptyState
                      query={activeQuery}
                      onReset={handleResetSearch}
                      onBrowseAll={handleResetSearch}
                    />
                  )}

                  {/* Similar Verified Books Grounded in Database */}
                  {searchResponse.similar_books && searchResponse.similar_books.length > 0 && (
                    <SimilarBooks
                      books={searchResponse.similar_books}
                      onSelect={setSelectedBook}
                      title={
                        searchResponse.books.length === 0
                          ? 'Genuinely Available Alternatives in Our Library'
                          : 'Related Books You May Also Enjoy'
                      }
                      subtitle="Every recommendation is verified to physically or digitally exist in our catalogue."
                    />
                  )}
                </div>
              )}

              {/* BROWSE MODE: No active search query */}
              {!activeQuery && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between pb-3 border-b border-library-border dark:border-library-darkBorder">
                    <div>
                      <h2 className="font-serif text-2xl font-bold text-library-navy dark:text-white">
                        Catalogue Collection
                      </h2>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Showing {browseBooks.length} of {browseTotal} verified library items
                      </p>
                    </div>

                    {selectedCategory !== 'All' && (
                      <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-300">
                        Genre: {selectedCategory}
                      </span>
                    )}
                  </div>

                  {isBrowseLoading || isSearching ? (
                    <LoadingSkeleton />
                  ) : browseBooks.length > 0 ? (
                    <>
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {browseBooks.map((book, idx) => (
                          <BookCard
                            key={book.id}
                            book={book}
                            index={idx}
                            onSelect={setSelectedBook}
                          />
                        ))}
                      </div>

                      {/* Browse Pagination */}
                      {browseTotalPages > 1 && (
                        <div className="pt-8 flex items-center justify-center gap-3">
                          <button
                            disabled={browsePage <= 1}
                            onClick={() =>
                              loadBrowseCatalog(browsePage - 1, selectedCategory, onlyAvailable)
                            }
                            className="p-2 rounded-xl bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors"
                          >
                            <ChevronLeft className="w-5 h-5" />
                          </button>
                          <span className="text-xs text-slate-500 font-medium px-2">
                            Page {browsePage} of {browseTotalPages}
                          </span>
                          <button
                            disabled={browsePage >= browseTotalPages}
                            onClick={() =>
                              loadBrowseCatalog(browsePage + 1, selectedCategory, onlyAvailable)
                            }
                            className="p-2 rounded-xl bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors"
                          >
                            <ChevronRight className="w-5 h-5" />
                          </button>
                        </div>
                      )}
                    </>
                  ) : (
                    <EmptyState onReset={handleResetSearch} />
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-library-border dark:border-library-darkBorder bg-white/50 dark:bg-slate-900/50 py-6 text-center text-xs text-slate-500 dark:text-slate-400">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <span className="font-serif font-bold text-slate-800 dark:text-slate-200">
              Athenaeum Library Agent
            </span>
            <span>· Factual Catalogue Search</span>
          </div>
          <p className="text-[11px]">
            Single Source of Truth: Verified Database Inventory · No Hallucinated Books
          </p>
        </div>
      </footer>

      {/* Book Detail Modal */}
      <BookDetailModal book={selectedBook} onClose={() => setSelectedBook(null)} />

      {/* AI Chat Drawer */}
      <AIChatDrawer
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
        onSelectBook={(book) => {
          setSelectedBook(book);
          setIsChatOpen(false);
        }}
      />
    </div>
  );
};
export default App;
