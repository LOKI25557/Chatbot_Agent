# AI-Powered Library Agent — Architecture & Design

## 1. System Overview

The **AI-Powered Library Agent** (*Athenaeum*) is an intelligent catalogue discovery and availability system designed to bridge natural language queries with relational database records.

```
┌────────────────────────────────────────────────────────┐
│                   React 18 + Vite Frontend             │
│   • Natural Language Search Hero & Filters             │
│   • Interactive Book Cards & Details Modal             │
│   • Grounded AI Assistant Drawer (Conversational)      │
│   • Admin Dashboard (Metrics, CRUD, CSV Import/Export) │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON
                            ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Backend Service                │
│   • /api/v1/search   (Fast-path + Groq Intent + Rank)  │
│   • /api/v1/books    (Paginated catalog & details)     │
│   • /api/v1/admin/*  (Protected with X-Admin-Key)      │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│       Groq AI API         │ │   SQLite / SQLAlchemy     │
│ • Intent & entity parser  │ │ • Indexed book catalogue  │
│ • Factual explanation     │ │ • Integrity constraints   │
│ • Fallback heuristics     │ │ • Grounded source of truth│
└───────────────────────────┘ └───────────────────────────┘
```

---

## 2. Source of Truth & Grounded AI Protocol

A fundamental requirement of the Library Agent is **absolute factual grounding**:

1. **Database as the Sole Ground Truth**:
   The Groq Large Language Model is strictly used to parse user queries into structured filters (`title`, `author`, `isbn`, `category`, `only_available`) and to generate polite, conversational explanations of the *actual* database results returned.
2. **Zero Hallucination Guarantee**:
   The LLM is never prompted or permitted to decide whether a book exists in the library or what its shelf location is. Only books actually returned by the database query are sent back to the user.
3. **Truthful Not-Found Handling**:
   When a query yields no database record, the agent explicitly clarifies that the book is not currently in the catalogue, and provides verified similar books genuine to the database.
4. **Circulation Status Distinction**:
   The system strictly distinguishes between *catalogue presence* and *borrowing availability* (`available_copies > 0` vs `available_copies == 0` when `total_copies > 0`).

---

## 3. Database Architecture

- **Engine**: SQLite (default local file `library.db`), migration-ready for PostgreSQL.
- **Model**: `Book`
  - `id`: Integer primary key, autoincrement.
  - `title`: String (255), not null, indexed.
  - `author`: String (255), nullable, indexed.
  - `isbn`: String (32), nullable, indexed, unique where present.
  - `publisher`: String (255), nullable.
  - `publication_year`: Integer, nullable.
  - `category`: String (100), nullable, indexed.
  - `description`: Text, nullable.
  - `cover_image_url`: String (500), nullable.
  - `shelf_location`: String (100), nullable.
  - `total_copies`: Integer, default 1, non-negative constraint.
  - `available_copies`: Integer, default 1, non-negative constraint.
  - `created_at`: DateTime, default UTC now.
  - `updated_at`: DateTime, default UTC now.

### Database Constraints
```sql
CONSTRAINT ck_total_copies_non_negative CHECK (total_copies >= 0)
CONSTRAINT ck_available_copies_non_negative CHECK (available_copies >= 0)
CONSTRAINT ck_available_not_exceed_total CHECK (available_copies <= total_copies)
```

---

## 4. Search Pipeline & Ranking Algorithm

1. **Fast-Path ISBN & Exact Title Lookup**:
   If the user supplies an exact ISBN or exact book title, the repository immediately queries the database directly, avoiding unnecessary LLM latency.
2. **Groq Intent Extraction**:
   For natural language queries (e.g. *"Do you have books on Python for beginners?"*), Groq extracts structured intent and search tokens in JSON format.
3. **Multi-Strategy Database Query**:
   - Exact and case-insensitive matches.
   - Partial / substring matches on Title, Author, Category, and Description.
   - Token-based word intersection.
4. **Relevance Scoring**:
   - Exact title matches score highest (100+ points).
   - Author matches (60 points).
   - Category matches (40 points).
   - Keyword occurrences in description (10 points each).
5. **Grounded Explanation Generation**:
   The verified database records are supplied to Groq as explicit evidence with strict system prompt boundaries. If Groq is temporarily offline, a deterministic heuristic template generates the explanation seamlessly.

---

## 5. Security & Robustness

- **Authentication**: Administrative endpoints require the `X-Admin-Key` header verified with constant-time HMAC comparison (`hmac.compare_digest`).
- **CSV Injection Prevention (CWE-1236)**:
  During CSV export, cells beginning with dangerous spreadsheet formula triggers (`=`, `+`, `-`, `@`, `\t`, `\r`) are safely neutralized with a leading single quote (`'`).
- **Input Sanitization**:
  Pydantic V2 rigorously validates all input parameters, enforcing string bounds, copy count limits, and sanitized characters.
- **CORS Configuration**:
  Origins are strictly configured through environment settings (`ALLOWED_ORIGINS`).
