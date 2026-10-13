import {
  Book,
  BookPagination,
  BookCreateInput,
  BookUpdateInput,
  SearchResponse,
  CatalogStats,
  ImportResponse,
  ImportPreviewItem,
} from '../types';

const API_BASE = '/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = 'Request failed';
    try {
      const errJson = await response.json();
      errorDetail = errJson.detail || errJson.message || JSON.stringify(errJson);
    } catch {
      errorDetail = `HTTP ${response.status} ${response.statusText}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  async health(): Promise<{ status: string; groq_configured: boolean; model: string }> {
    return request('/health');
  },

  async search(
    query: string,
    onlyAvailable?: boolean,
    category?: string,
    context?: string
  ): Promise<SearchResponse> {
    return request<SearchResponse>('/search', {
      method: 'POST',
      body: JSON.stringify({
        query,
        only_available: onlyAvailable,
        category: category && category !== 'All' ? category : undefined,
        context,
      }),
    });
  },

  async getBooks(
    page = 1,
    size = 12,
    search?: string,
    category?: string,
    onlyAvailable?: boolean
  ): Promise<BookPagination> {
    const params = new URLSearchParams();
    params.set('page', String(page));
    params.set('size', String(size));
    if (search && search.trim()) params.set('search', search.trim());
    if (category && category !== 'All') params.set('category', category);
    if (onlyAvailable) params.set('only_available', 'true');

    return request<BookPagination>(`/books?${params.toString()}`);
  },

  async getBook(id: number): Promise<Book> {
    return request<Book>(`/books/${id}`);
  },

  async getCategories(): Promise<string[]> {
    return request<string[]>('/books/categories');
  },

  /* Admin Endpoints */
  async getAdminStats(adminKey: string): Promise<CatalogStats> {
    return request<CatalogStats>('/admin/stats', {
      headers: { 'X-Admin-Key': adminKey },
    });
  },

  async createBook(book: BookCreateInput, adminKey: string): Promise<Book> {
    return request<Book>('/admin/books', {
      method: 'POST',
      headers: { 'X-Admin-Key': adminKey },
      body: JSON.stringify(book),
    });
  },

  async updateBook(id: number, book: BookUpdateInput, adminKey: string): Promise<Book> {
    return request<Book>(`/admin/books/${id}`, {
      method: 'PUT',
      headers: { 'X-Admin-Key': adminKey },
      body: JSON.stringify(book),
    });
  },

  async deleteBook(id: number, adminKey: string): Promise<{ success: boolean; message: string }> {
    return request<{ success: boolean; message: string }>(`/admin/books/${id}`, {
      method: 'DELETE',
      headers: { 'X-Admin-Key': adminKey },
    });
  },

  async previewImport(
    file: File,
    adminKey: string
  ): Promise<{ total_rows: number; preview: ImportPreviewItem[] }> {
    const formData = new FormData();
    formData.append('file', file);
    return request<{ total_rows: number; preview: ImportPreviewItem[] }>(
      '/admin/books/import?commit=false',
      {
        method: 'POST',
        headers: { 'X-Admin-Key': adminKey },
        body: formData,
      }
    );
  },

  async commitImport(file: File, adminKey: string): Promise<ImportResponse> {
    const formData = new FormData();
    formData.append('file', file);
    return request<ImportResponse>('/admin/books/import?commit=true', {
      method: 'POST',
      headers: { 'X-Admin-Key': adminKey },
      body: formData,
    });
  },

  getExportUrl(): string {
    return `${API_BASE}/admin/books/export`;
  },
};
