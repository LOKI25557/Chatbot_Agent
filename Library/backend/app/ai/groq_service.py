import json
import logging
import re
from typing import List, Optional, Dict, Any
from app.core.config import settings
from app.schemas.search import SearchIntent

logger = logging.getLogger(__name__)


def clean_json_output(raw: str) -> str:
    """Strips markdown code fences from LLM responses."""
    cleaned = raw.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


class GroqService:
    """
    Orchestrates Groq LLM natural language understanding and grounded responses.
    Strictly observes grounding: never invents catalog items, shelf codes, or availability.
    """

    @classmethod
    def parse_intent(cls, query: str, context: Optional[str] = None) -> SearchIntent:
        """
        Parses user query into structured search parameters using Groq.
        Falls back to rule-based heuristic extraction if Groq is unavailable.
        """
        if not settings.is_groq_configured():
            return cls._heuristic_intent(query)

        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY, base_url=settings.clean_groq_base_url)

            system_prompt = (
                "You are an expert library catalog query parser. "
                "Analyze the user's natural language book request and output ONLY a valid JSON object. "
                "Do NOT invent or assume any book details that the user did not mention."
            )

            user_prompt = f"""Extract search criteria from this library request:
Query: "{query}"
{f'Context: {context}' if context else ''}

Return ONLY this JSON structure:
{{
  "intent": "search" | "availability" | "details" | "recommendation",
  "title": "extracted book title or null",
  "author": "extracted author name or null",
  "isbn": "extracted ISBN numbers or null",
  "category": "extracted topic, category, or genre or null",
  "only_available": true | false | null,
  "keywords": ["significant", "search", "tokens"]
}}"""

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            raw_content = response.choices[0].message.content or "{}"
            parsed = json.loads(clean_json_output(raw_content))

            return SearchIntent(
                intent=parsed.get("intent", "search"),
                title=parsed.get("title"),
                author=parsed.get("author"),
                isbn=parsed.get("isbn"),
                category=parsed.get("category"),
                only_available=parsed.get("only_available"),
                keywords=parsed.get("keywords", []),
                raw_query=query
            )
        except Exception as e:
            logger.warning(f"Groq intent parsing failed ({e}). Using heuristic extraction.")
            return cls._heuristic_intent(query)

    @classmethod
    def _heuristic_intent(cls, query: str) -> SearchIntent:
        """Deterministic heuristic extraction when Groq is offline."""
        q_lower = query.lower().strip()

        # Check for availability filters
        only_avail = bool(re.search(r"\b(only available|available books?|can i borrow|in stock)\b", q_lower))

        # Check for ISBN (978... or 10/13 digits)
        isbn_match = re.search(r"\b(?:97[89][-\s]?)?[0-9]{9}[0-9xX]\b", query)
        isbn = isbn_match.group(0).replace("-", "").replace(" ", "") if isbn_match else None

        # Check for 'by <author>' pattern
        by_match = re.search(r"\bby\s+([A-Za-z\.\s]+)", query, re.IGNORECASE)
        author = by_match.group(1).strip() if by_match else None

        # Clean title candidate
        clean_title = query
        for phrase in [
            "find book", "search for", "find", "do you have", "show me", "books about",
            "can you find", "i am looking for", "looking for"
        ]:
            if clean_title.lower().startswith(phrase):
                clean_title = clean_title[len(phrase):].strip()

        if by_match:
            clean_title = re.sub(r"\bby\s+[A-Za-z\.\s]+", "", clean_title, flags=re.IGNORECASE).strip()

        clean_title = re.sub(r"[^\w\s\-\:]", "", clean_title).strip()

        # Tokens
        stopwords = {"a", "an", "the", "in", "on", "of", "for", "by", "to", "and", "or", "is", "have", "do", "you", "me", "show"}
        tokens = [w for w in re.findall(r"\w+", query.lower()) if w not in stopwords and len(w) > 2]

        return SearchIntent(
            intent="search",
            title=clean_title if len(clean_title) >= 3 else None,
            author=author,
            isbn=isbn,
            only_available=only_avail,
            keywords=tokens,
            raw_query=query
        )

    @classmethod
    def generate_explanation(
        cls,
        query: str,
        status: str,
        books: List[Any],
        similar_books: List[Any]
    ) -> str:
        """
        Produces a grounded, polite conversational explanation of the search results.
        If Groq is offline or times out, uses deterministic, polished templates.
        """
        if settings.is_groq_configured():
            try:
                from groq import Groq
                client = Groq(api_key=settings.GROQ_API_KEY, base_url=settings.clean_groq_base_url)

                # Format verified database evidence for the prompt
                matched_summary = []
                for b in books:
                    avail_str = f"{b.available_copies} of {b.total_copies} copies available" if b.total_copies > 0 else "Availability not tracked"
                    shelf_str = f"Shelf: {b.shelf_location}" if b.shelf_location else "Shelf location: Not assigned"
                    matched_summary.append(f"- '{b.title}' by {b.author or 'Unknown'} ({avail_str}, {shelf_str})")

                similar_summary = [f"- '{b.title}' by {b.author or 'Unknown'} ({b.category or 'General'})" for b in similar_books]

                prompt = f"""You are an attentive, friendly AI Library Assistant.
User Query: "{query}"
Search Status: {status}

VERIFIED DATABASE CATALOG RESULTS (SOURCE OF TRUTH):
Matched in library catalogue:
{chr(10).join(matched_summary) if matched_summary else "No matching record found in the library."}

Similar books genuinely in database:
{chr(10).join(similar_summary) if similar_summary else "No similar catalogue suggestions available."}

STRICT GROUNDING RULES:
1. ONLY reference the books listed above. NEVER invent or hallucinate other books, shelf numbers, or copy counts.
2. If status is 'not_found', explicitly and politely explain that the requested book is not currently in the library catalogue, then introduce the genuinely available similar books.
3. If status is 'found', specify whether copies are currently available for borrowing and mention the shelf location if recorded.
4. Keep the explanation concise (2 to 4 sentences), welcoming, and natural.
"""

                response = client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a helpful library assistant that provides truthful, grounded explanations."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.4,
                    max_tokens=250
                )
                text = (response.choices[0].message.content or "").strip()
                if text:
                    return text
            except Exception as e:
                logger.warning(f"Groq explanation generation failed ({e}). Using deterministic template.")

        # Deterministic grounded templates
        return cls._fallback_explanation(query, status, books, similar_books)

    @staticmethod
    def _fallback_explanation(
        query: str,
        status: str,
        books: List[Any],
        similar_books: List[Any]
    ) -> str:
        if status == "found" and books:
            b = books[0]
            if b.available_copies > 0:
                loc = f" on {b.shelf_location}" if b.shelf_location else ""
                return f"Yes! We found '{b.title}' by {b.author or 'Unknown'}. There are currently {b.available_copies} of {b.total_copies} copies available{loc}."
            else:
                return f"'{b.title}' by {b.author or 'Unknown'} is listed in our catalogue, but all {b.total_copies} copies are currently checked out."

        elif status == "multiple_found" and books:
            return f"We found {len(books)} relevant books matching '{query}'. Please select a book to view its shelf location and availability."

        elif status == "not_found":
            if similar_books:
                titles = ", ".join([f"'{b.title}'" for b in similar_books[:3]])
                return f"We do not currently have '{query}' in our library catalogue. However, you might enjoy these related books available in our collection: {titles}."
            return f"I searched our library catalogue, but could not find any records matching '{query}'. An administrator can add it to the catalogue."

        return f"Here are the catalogue records matching your search."
