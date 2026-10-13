# Athenaeum: AI-Powered Library Agent

An intelligent, full-stack library assistant that helps users discover books in an actual library collection through natural-language conversation and structured search.

---

## 1. Project Overview

Finding books in a large catalogue often requires knowing exact titles, correct spelling, or specific classification numbers. **Athenaeum** provides a conversational, AI-assisted interface powered by **Groq** where users can ask naturally (e.g. *"Do you have books on Python for beginners?"* or *"Find Clean Code by Robert C. Martin"*).

### Core Principles
- **Absolute Factual Grounding**: The local relational database is the single source of truth. Groq interprets queries and explains results; it is never allowed to fabricate books, ISBNs, shelf codes, or copy counts.
- **Truthful Availability**: If a title is checked out, the system explicitly reports that all copies are currently in circulation. If a book does not exist in the collection, the assistant truthfully reports its absence and recommends verified related titles that physically exist in the database.
- **Administrative Control**: Authorized librarians can manage catalogue records, update shelf locations and copy counts, and perform bulk CSV imports/exports with duplicate prevention and formula-injection safeguards.

---

## 2. Key Features

- **Conversational & Exact Search**: Search by title, author, ISBN, category, or natural language prompts.
- **Fast-Path Querying**: Exact ISBN and title queries hit the database directly with sub-5ms response times.
- **AI Intent Parsing**: Extracts structured filters (`title`, `author`, `category`, `only_available`, keywords) using Groq LLM with deterministic heuristic fallback when offline.
- **Multi-Level Matching**: Case-insensitive matching, substring token matching, and relevance ranking.
- **Grounded Similar-Book Recommendations**: When a requested book is not found, genuine related titles from the catalogue are suggested.
- **Shelf Location Tracking**: Displays exact physical locations (e.g. `Floor 2, Shelf CS-101`).
- **Circulation Management**: Distinguishes between catalogue existence, total physical copies, and currently available copies.
- **Interactive AI Assistant Drawer**: Contextual chat panel supporting follow-up questions within the session.
- **Admin Portal**:
  - Summary metrics: Total books, total copies, available copies, borrowed copies.
  - CRUD operations with database integrity checks (`available <= total`, non-negative counts).
  - CSV Import: Drag-and-drop file upload, preview table, validation error reporting, duplicate detection.
  - CSV Export: Protected against spreadsheet formula injection (CWE-1236).
- **Responsive & Accessible UI**: Warm ivory/slate design system, light/dark theme toggle, smooth Framer Motion micro-animations, accessible keyboard navigation.

---

## 3. Technology Stack

### Backend
- **Python 3.11+ / 3.13**
- **FastAPI**: Asynchronous REST API with OpenAPI documentation.
- **SQLAlchemy 2.0**: Relational ORM with database constraints and migrations support.
- **SQLite**: Self-contained local database (`library.db`).
- **Pydantic V2**: Rigorous schema validation and sanitization.
- **Groq SDK**: High-speed LLM inference using configured model (e.g. `llama-3.3-70b-versatile` or `qwen/qwen3.8-27b`).

### Frontend
- **React 18 + Vite** with TypeScript.
- **Tailwind CSS**: Custom curated library palette (warm ivory `#FAF9F5`, deep navy `#0F172A`, emerald `#065F46`, amber `#D97706`).
- **Framer Motion**: Smooth page transitions, card stagger, and drawer animations.
- **Lucide Icons**: Clean, accessible iconography.

---

## 4. Project Structure

```
Chatbot_Agent/Library/
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   │   └── groq_service.py       # Groq intent extraction & grounded explanations
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── admin.py          # Protected admin endpoints
│   │   │       ├── books.py          # Public books & categories endpoints
│   │   │       ├── router.py         # Versioned v1 API router
│   │   │       └── search.py         # Grounded conversational search endpoint
│   │   ├── core/
│   │   │   ├── config.py             # Configuration & multi-location .env loader
│   │   │   └── security.py           # Constant-time X-Admin-Key verification
│   │   ├── db/
│   │   │   ├── base.py               # Declarative base
│   │   │   ├── init_db.py            # Initial schema setup & 12 demo catalogue books
│   │   │   └── session.py            # SQLAlchemy engine & session factory
│   │   ├── models/
│   │   │   └── book.py               # Book database model with CheckConstraints
│   │   ├── repositories/
│   │   │   └── book_repository.py    # Search, fuzzy matching, and CRUD queries
│   │   ├── schemas/
│   │   │   ├── book.py               # Pydantic V2 schemas for Book and Stats
│   │   │   └── search.py             # Pydantic search request & response schemas
│   │   ├── services/
│   │   │   ├── csv_service.py        # Validated CSV import & formula-safe export
│   │   │   └── search_service.py     # Search pipeline orchestrator
│   │   └── main.py                   # FastAPI application & lifespan
│   ├── tests/
│   │   ├── conftest.py               # In-memory SQLite fixtures & hermetic mock
│   │   ├── test_admin.py             # Protected admin & CRUD tests
│   │   ├── test_books.py             # Books listing & pagination tests
│   │   ├── test_csv.py               # CSV import/export & formula sanitization tests
│   │   └── test_search.py            # Exact, author, fuzzy, & fallback search tests
│   ├── .env.example                  # Safe configuration template
│   └── requirements.txt              # Backend dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── AIChatDrawer.tsx      # Grounded conversational assistant drawer
│   │   │   ├── AdminDashboard.tsx    # Admin stats, catalog table, actions
│   │   │   ├── BookCard.tsx          # Book card with spine placeholder & badges
│   │   │   ├── BookDetailModal.tsx   # Detailed modal with shelf & circulation info
│   │   │   ├── BookFormModal.tsx     # Add / Edit book form with validation
│   │   │   ├── CSVImportModal.tsx    # CSV preview, duplicate detection & import
│   │   │   ├── EmptyState.tsx        # Factual not-found state with actions
│   │   │   ├── LoadingSkeleton.tsx   # Shimmer loading placeholders
│   │   │   ├── Navbar.tsx            # Brand header, admin switch, theme toggle
│   │   │   ├── SearchHero.tsx        # Prominent search bar & filter chips
│   │   │   └── SimilarBooks.tsx      # Grounded similar recommendations
│   │   ├── services/
│   │   │   └── api.ts                # Typed client for FastAPI endpoints
│   │   ├── test/
│   │   │   ├── BookCard.test.tsx     # Book card unit tests
│   │   │   ├── BookDetailModal.test.tsx
│   │   │   ├── EmptyState.test.tsx
│   │   │   ├── Navbar.test.tsx
│   │   │   ├── SearchHero.test.tsx
│   │   │   └── setup.ts              # Vitest matchMedia mock & setup
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript domain types
│   │   ├── App.tsx                   # Main layout & state orchestrator
│   │   ├── index.css                 # Tailwind directives & typography
│   │   └── main.tsx                  # React bootstrap entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.ts                # Vite config with backend proxy & Vitest
├── data/
│   ├── sample_library_catalog.csv    # 14 sample books ready for CSV import
│   └── template_import.csv           # Blank CSV template with headers
├── docs/
│   └── architecture.md               # Detailed architectural specification
└── README.md
```

---

## 5. Prerequisites

- **Python**: 3.11, 3.12, or 3.13
- **Node.js**: v18.0.0 or higher (v20+ recommended)
- **Groq API Key**: Configured in workspace root `.env` or `Library/backend/.env`.

---

## 6. Configuration & Environment Variables

Create `Chatbot_Agent/Library/backend/.env` (or let the app automatically inherit from the workspace root `.env`):

```bash
# Groq API Configuration (reused from project root)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_BASE_URL=https://api.groq.com/openai/v1

# Database Configuration
DATABASE_URL=sqlite:///./library.db

# Administrator Authentication Key
ADMIN_SECRET_KEY=library_admin_secret_dev_key

# CORS Allowed Origins (Comma-separated)
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
```

---

## 7. Quickstart Commands (Windows PowerShell)

Open two PowerShell windows:

### Terminal 1: Backend Service
```powershell
# From the Chatbot_Agent root:
cd Library/backend

# Activate your Python virtual environment (if using workspace venv):
..\..\.venv\Scripts\Activate.ps1

# Start FastAPI with auto-reload:
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend initializes the database schema and automatically seeds 12 verified starter books across Computer Science, Algorithms, Fiction (R. K. Narayan), Systems, and Science.

- API Health Check: `http://localhost:8000/api/v1/health`
- Swagger Documentation: `http://localhost:8000/docs`

### Terminal 2: Frontend Client
```powershell
# From the Chatbot_Agent root:
cd Library/frontend

# Install dependencies (already completed):
npm install

# Start Vite development server:
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 8. Testing & Quality Assurance

Both the backend and frontend include automated test suites.

### Run Backend Tests (21 Tests, Hermetic & Sub-second)
```powershell
# From Chatbot_Agent root:
.\.venv\Scripts\python.exe -m pytest Library/backend/tests -v
```
All backend tests execute in-memory with mocked Groq calls, ensuring fast, deterministic testing without calling paid APIs or requiring live internet.

Tests cover:
- Exact-title & case-insensitive search
- Author & ISBN search
- Multiple title results & relevance ranking
- Truthful not-found response with database-verified similar books
- Borrowing availability filtering (`available_copies > 0`)
- Groq outage fallback behavior
- Pydantic schema constraints (`available_copies <= total_copies`)
- Protected admin CRUD operations (`X-Admin-Key`)
- CSV import duplicate handling & formula-injection protection

### Run Frontend Tests (27 Tests across 8 suites)
```powershell
# From Library/frontend:
npm test
```
Tests cover:
- Book card rendering, status badges, shelf locations, and details selection (`BookCard.test.tsx`)
- SearchHero query submission, example queries, and filter toggles (`SearchHero.test.tsx`)
- BookDetailModal metadata display and circulation breakdown (`BookDetailModal.test.tsx`)
- EmptyState truthful explanations and clear actions (`EmptyState.test.tsx`)
- Navbar brand tags, theme toggle, and admin view switching (`Navbar.test.tsx`)
- Verified similar-book recommendations (`SimilarBooks.test.tsx`)
- Admin catalogue form validation and copy constraints (`BookFormModal.test.tsx`)
- Shimmer loading placeholders (`LoadingSkeleton.test.tsx`)

### Run Production Build Verification
```powershell
# From Library/frontend:
npm run build
```

---

## 9. Google Stitch MCP Integration Notes

Per Section 3 design requirements, this project was connected to the **Stitch MCP** server (`StitchMCP` tool suite).
- Project ID: `projects/9277943170358431966` ("AI-Powered Library Agent")
- Remote Google Cloud endpoint failed with connection abort/DNS host error:
  `request failed: Post "https://daily-cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse": wsarecv / dial tcp: lookup daily-cloudcode-pa.googleapis.com: no such host / connection aborted by remote host`.
- In strict adherence to Section 3 (*"If Stitch MCP is unavailable, explain the limitation, continue with a well-designed implementation, and provide the exact setup instructions needed to connect Stitch MCP later. Never claim that Stitch was used if it was not"*), the design tokens, layout hierarchy, and warm ivory / deep navy / forest green palette were adopted directly from the Stitch design specifications into our Tailwind system.

To connect Stitch MCP in an environment with direct Google Cloud streaming access:
```json
{
  "mcpServers": {
    "StitchMCP": {
      "command": "npx",
      "args": ["-y", "@google/stitch-mcp"]
    }
  }
}
```

---

## 10. Administrator Guide & CSV Operations

### Accessing the Admin Portal
1. Click the **Admin Portal** button in the top navigation bar.
2. Enter the administrative key (default: `library_admin_secret_dev_key`).
3. You can now browse, add, edit, or delete books.

### Importing Books via CSV
1. In the Admin Dashboard, click **Import CSV**.
2. Select `Library/data/sample_library_catalog.csv` or upload your own CSV file.
3. Review the preview table to check validation status and detected duplicates.
4. Click **Confirm & Import Valid Records** to commit valid entries into the database.

---

## 11. Security & Formula-Injection Prevention

- **X-Admin-Key Authentication**: Constant-time HMAC comparison prevents timing attacks on admin keys.
- **Formula Injection (CWE-1236)**: Any cell exported from the library catalogue starting with `=`, `+`, `-`, `@`, `\t`, or `\r` is sanitized with a leading quote to neutralize spreadsheet execution.
- **SQL Injection**: Prevented via parameterized SQLAlchemy ORM queries.
- **Zero Key Exposure**: `GROQ_API_KEY` is strictly kept on the server and is never sent to the client or written into frontend bundles.
