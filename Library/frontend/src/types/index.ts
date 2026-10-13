export interface Book {
  id: number;
  title: string;
  author?: string | null;
  isbn?: string | null;
  publisher?: string | null;
  publication_year?: number | null;
  category?: string | null;
  description?: string | null;
  cover_image_url?: string | null;
  shelf_location?: string | null;
  total_copies: number;
  available_copies: number;
  borrowed_copies: number;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

export interface BookCreateInput {
  title: string;
  author?: string;
  isbn?: string;
  publisher?: string;
  publication_year?: number;
  category?: string;
  description?: string;
  cover_image_url?: string;
  shelf_location?: string;
  total_copies: number;
  available_copies: number;
}

export interface BookUpdateInput {
  title?: string;
  author?: string;
  isbn?: string;
  publisher?: string;
  publication_year?: number;
  category?: string;
  description?: string;
  cover_image_url?: string;
  shelf_location?: string;
  total_copies?: number;
  available_copies?: number;
}

export interface BookPagination {
  items: Book[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface SearchIntent {
  intent: 'search' | 'availability' | 'details' | 'recommendation';
  title?: string | null;
  author?: string | null;
  isbn?: string | null;
  category?: string | null;
  only_available?: boolean | null;
  keywords: string[];
}

export interface SearchResponse {
  query: string;
  status: 'found' | 'multiple_found' | 'not_found';
  total_results: number;
  books: Book[];
  similar_books: Book[];
  ai_explanation: string;
  matched_by: 'exact_title' | 'isbn' | 'ai_intent' | 'fuzzy_keywords';
  extracted_intent?: SearchIntent | null;
}

export interface CatalogStats {
  total_books: number;
  total_copies: number;
  available_copies: number;
  borrowed_copies: number;
  categories_count: number;
  categories: { [key: string]: number };
}

export interface ImportPreviewItem {
  row: number;
  title: string;
  author?: string | null;
  isbn?: string | null;
  category?: string | null;
  shelf_location?: string | null;
  total_copies: number;
  available_copies: number;
  is_valid: boolean;
  errors: string[];
}

export interface ImportResponse {
  total_rows: number;
  imported: number;
  skipped_duplicates: number;
  failed_validation: number;
  errors: string[];
}
