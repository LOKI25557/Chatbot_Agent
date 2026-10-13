import React, { useState, useEffect } from 'react';
import { Book, CatalogStats, BookCreateInput, BookUpdateInput } from '../types';
import { api } from '../services/api';
import { BookFormModal } from './BookFormModal';
import { CSVImportModal } from './CSVImportModal';
import {
  Shield,
  Plus,
  Upload,
  Download,
  Search,
  Edit2,
  Trash2,
  BookOpen,
  Layers,
  CheckCircle,
  AlertCircle,
  Key,
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  LogOut,
} from 'lucide-react';
import { motion } from 'framer-motion';

export const AdminDashboard: React.FC = () => {
  const [adminKey, setAdminKey] = useState<string>(() => {
    return localStorage.getItem('athenaeum_admin_key') || '';
  });
  const [keyInput, setKeyInput] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [authError, setAuthError] = useState<string | null>(null);

  const [stats, setStats] = useState<CatalogStats | null>(null);
  const [books, setBooks] = useState<Book[]>([]);
  const [totalBooks, setTotalBooks] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Modals state
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const [isImportOpen, setIsImportOpen] = useState(false);
  const [bookToDelete, setBookToDelete] = useState<Book | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Authenticate by attempting to fetch stats
  const verifyAuth = async (keyToTest: string) => {
    setIsLoading(true);
    setAuthError(null);
    try {
      const statsData = await api.getAdminStats(keyToTest);
      setStats(statsData);
      setIsAuthenticated(true);
      localStorage.setItem('athenaeum_admin_key', keyToTest);
      loadCatalogue(1, searchQuery, keyToTest);
    } catch (err: any) {
      setIsAuthenticated(false);
      setAuthError(err.message || 'Invalid administrator secret key.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (adminKey) {
      verifyAuth(adminKey);
    }
  }, []);

  const loadCatalogue = async (page = 1, search = '', key = adminKey) => {
    setIsLoading(true);
    try {
      const res = await api.getBooks(page, 10, search);
      setBooks(res.items);
      setTotalBooks(res.total);
      setCurrentPage(res.page);
      setTotalPages(res.pages);

      // Refresh stats as well
      const statsData = await api.getAdminStats(key);
      setStats(statsData);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeySubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyInput.trim()) {
      setAdminKey(keyInput.trim());
      verifyAuth(keyInput.trim());
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('athenaeum_admin_key');
    setAdminKey('');
    setKeyInput('');
    setIsAuthenticated(false);
    setStats(null);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadCatalogue(1, searchQuery);
  };

  const handleSaveBook = async (data: BookCreateInput) => {
    setActionLoading(true);
    try {
      if (editingBook) {
        await api.updateBook(editingBook.id, data as BookUpdateInput, adminKey);
      } else {
        await api.createBook(data, adminKey);
      }
      setIsFormOpen(false);
      setEditingBook(null);
      loadCatalogue(currentPage, searchQuery);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteBook = async () => {
    if (!bookToDelete) return;
    setActionLoading(true);
    try {
      await api.deleteBook(bookToDelete.id, adminKey);
      setBookToDelete(null);
      loadCatalogue(currentPage, searchQuery);
    } finally {
      setActionLoading(false);
    }
  };

  // If not authenticated, render login form
  if (!isAuthenticated) {
    return (
      <div className="max-w-md mx-auto my-16 px-4">
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-8 rounded-3xl bg-white dark:bg-library-darkCard border border-library-border dark:border-library-darkBorder shadow-lg text-center"
        >
          <div className="w-14 h-14 rounded-2xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 flex items-center justify-center mx-auto mb-4 border border-amber-200 dark:border-amber-800">
            <Shield className="w-7 h-7" />
          </div>
          <h2 className="font-serif text-2xl font-bold text-slate-900 dark:text-white mb-2">
            Administrator Authentication
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-6 leading-relaxed">
            Please enter your configured administrative key (<code className="bg-slate-100 dark:bg-slate-800 px-1 py-0.5 rounded text-amber-600">X-Admin-Key</code>) to access catalogue management operations.
          </p>

          <form onSubmit={handleKeySubmit} className="space-y-4">
            {authError && (
              <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs">
                {authError}
              </div>
            )}

            <div className="relative">
              <input
                type="password"
                required
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                placeholder="Enter Admin Secret Key..."
                className="w-full px-4 py-3 rounded-xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
              />
              <Key className="w-4 h-4 text-slate-400 absolute right-3.5 top-3.5" />
            </div>

            <button
              type="submit"
              disabled={isLoading || !keyInput.trim()}
              className="w-full py-3 rounded-xl bg-library-navy dark:bg-emerald-600 text-white font-medium hover:bg-slate-800 dark:hover:bg-emerald-500 transition-colors disabled:opacity-50 text-sm shadow-md"
            >
              {isLoading ? 'Verifying...' : 'Authenticate & Open Dashboard'}
            </button>
          </form>

          <div className="mt-6 pt-4 border-t border-slate-100 dark:border-slate-800 text-[11px] text-slate-400">
            Protected endpoint authenticated via <code className="font-mono text-slate-600 dark:text-slate-300">ADMIN_SECRET_KEY</code>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-library-border dark:border-library-darkBorder">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
              Administrative Control
            </span>
          </div>
          <h2 className="font-serif text-3xl font-bold text-library-navy dark:text-white">
            Library Catalogue Management
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Manage catalogue records, physical copies inventory, shelf assignments, and bulk CSV transfers.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => loadCatalogue(currentPage, searchQuery)}
            className="p-2.5 rounded-xl bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 transition-colors"
            title="Refresh catalogue"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:text-rose-600 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Lock</span>
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-white dark:bg-library-darkCard border border-library-border dark:border-library-darkBorder shadow-sm">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">Total Titles</span>
              <BookOpen className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl font-bold font-serif text-slate-900 dark:text-white">
              {stats.total_books}
            </div>
            <span className="text-[11px] text-slate-400">Across {stats.categories_count} subjects</span>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-library-darkCard border border-library-border dark:border-library-darkBorder shadow-sm">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">Total Copies</span>
              <Layers className="w-4 h-4 text-blue-600" />
            </div>
            <div className="text-2xl font-bold font-serif text-slate-900 dark:text-white">
              {stats.total_copies}
            </div>
            <span className="text-[11px] text-slate-400">Physical stock items</span>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-library-darkCard border border-library-border dark:border-library-darkBorder shadow-sm">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">Available Copies</span>
              <CheckCircle className="w-4 h-4 text-emerald-600" />
            </div>
            <div className="text-2xl font-bold font-serif text-emerald-600 dark:text-emerald-400">
              {stats.available_copies}
            </div>
            <span className="text-[11px] text-emerald-600/80 font-medium">Ready on shelf</span>
          </div>

          <div className="p-5 rounded-2xl bg-white dark:bg-library-darkCard border border-library-border dark:border-library-darkBorder shadow-sm">
            <div className="flex items-center justify-between text-slate-400 mb-2">
              <span className="text-xs font-semibold uppercase tracking-wider">Checked Out</span>
              <AlertCircle className="w-4 h-4 text-amber-600" />
            </div>
            <div className="text-2xl font-bold font-serif text-amber-600 dark:text-amber-400">
              {stats.borrowed_copies}
            </div>
            <span className="text-[11px] text-slate-400">Currently in circulation</span>
          </div>
        </div>
      )}

      {/* Action Toolbar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearch} className="relative flex-1 max-w-md">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search records by title, author, or ISBN..."
            className="w-full pl-9 pr-4 py-2.5 rounded-xl bg-white dark:bg-library-darkCard border border-slate-200 dark:border-slate-700 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-sm"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
        </form>

        {/* Buttons */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => {
              setEditingBook(null);
              setIsFormOpen(true);
            }}
            className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Add New Book</span>
          </button>

          <button
            onClick={() => setIsImportOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 transition-colors text-xs font-medium"
          >
            <Upload className="w-3.5 h-3.5 text-blue-600" />
            <span>Import CSV</span>
          </button>

          <a
            href={api.getExportUrl()}
            download="library_catalogue_export.csv"
            className="flex items-center gap-1.5 px-3.5 py-2.5 rounded-xl bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 transition-colors text-xs font-medium"
          >
            <Download className="w-3.5 h-3.5 text-amber-600" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* Catalogue Table */}
      <div className="bg-white dark:bg-library-darkCard rounded-2xl border border-library-border dark:border-library-darkBorder shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 dark:bg-slate-900 text-slate-500 dark:text-slate-400 font-semibold border-b border-slate-100 dark:border-slate-800">
              <tr>
                <th className="py-3 px-4">Title & Author</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">ISBN</th>
                <th className="py-3 px-4">Shelf Location</th>
                <th className="py-3 px-4">Availability</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {books.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-400">
                    {isLoading ? 'Loading records...' : 'No catalogue books found.'}
                  </td>
                </tr>
              ) : (
                books.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 max-w-xs">
                      <span className="font-semibold text-slate-900 dark:text-white block truncate">
                        {b.title}
                      </span>
                      <span className="text-[11px] text-slate-500 truncate block">
                        {b.author || 'Author not recorded'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium">
                        {b.category || 'General'}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500">
                      {b.isbn || '—'}
                    </td>
                    <td className="py-3 px-4 text-slate-600 dark:text-slate-300 font-medium">
                      {b.shelf_location || <span className="italic text-slate-400">Unassigned</span>}
                    </td>
                    <td className="py-3 px-4">
                      {b.total_copies > 0 ? (
                        <span
                          className={`font-semibold ${
                            b.available_copies > 0 ? 'text-emerald-600' : 'text-amber-600'
                          }`}
                        >
                          {b.available_copies} / {b.total_copies}
                        </span>
                      ) : (
                        <span className="text-slate-400">Record only</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => {
                            setEditingBook(b);
                            setIsFormOpen(true);
                          }}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950/50 transition-colors"
                          title="Edit Book"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setBookToDelete(b)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/50 transition-colors"
                          title="Delete Book"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="p-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
          <span>
            Showing {books.length} of {totalBooks} items (Page {currentPage} of {totalPages})
          </span>
          <div className="flex items-center gap-2">
            <button
              disabled={currentPage <= 1}
              onClick={() => loadCatalogue(currentPage - 1, searchQuery)}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => loadCatalogue(currentPage + 1, searchQuery)}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 disabled:opacity-40 hover:bg-slate-50 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {bookToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm">
          <div className="bg-white dark:bg-library-darkCard rounded-2xl p-6 max-w-sm w-full border border-library-border dark:border-library-darkBorder shadow-2xl text-center">
            <div className="w-12 h-12 rounded-full bg-rose-50 dark:bg-rose-950 text-rose-600 flex items-center justify-center mx-auto mb-3">
              <Trash2 className="w-6 h-6" />
            </div>
            <h4 className="font-serif text-lg font-bold text-slate-900 dark:text-white mb-1">
              Delete Catalogue Record?
            </h4>
            <p className="text-xs text-slate-500 mb-5 leading-relaxed">
              Are you sure you want to permanently remove <span className="font-semibold text-slate-800 dark:text-slate-200">"{bookToDelete.title}"</span> from the library catalogue?
            </p>
            <div className="flex justify-center gap-3">
              <button
                onClick={() => setBookToDelete(null)}
                className="px-4 py-2 rounded-xl bg-slate-100 dark:bg-slate-800 text-xs font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-200 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteBook}
                disabled={actionLoading}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold transition-colors disabled:opacity-50"
              >
                {actionLoading ? 'Deleting...' : 'Confirm Delete'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add / Edit Form Modal */}
      <BookFormModal
        isOpen={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setEditingBook(null);
        }}
        onSubmit={handleSaveBook}
        initialBook={editingBook}
        isLoading={actionLoading}
      />

      {/* CSV Import Modal */}
      <CSVImportModal
        isOpen={isImportOpen}
        onClose={() => setIsImportOpen(false)}
        adminKey={adminKey}
        onImportComplete={() => loadCatalogue(1, searchQuery)}
      />
    </div>
  );
};
