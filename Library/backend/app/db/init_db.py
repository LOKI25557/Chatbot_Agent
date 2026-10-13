import logging
from sqlalchemy.orm import Session
from app.models.book import Book

logger = logging.getLogger(__name__)

# Clearly labelled development demo dataset
DEMO_BOOKS = [
    {
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "publisher": "Prentice Hall",
        "publication_year": 2008,
        "category": "Computer Science",
        "description": "Even bad code can function. But if code isn't clean, it can bring a development organization to its knees. A guide on writing maintainable, readable software.",
        "cover_image_url": "https://images.unsplash.com/photo-1516116211227-bbc03c1533ad?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 2, Shelf CS-101",
        "total_copies": 3,
        "available_copies": 2
    },
    {
        "title": "The Pragmatic Programmer: Your Journey to Mastery",
        "author": "David Thomas, Andrew Hunt",
        "isbn": "9780135957059",
        "publisher": "Addison-Wesley",
        "publication_year": 2019,
        "category": "Computer Science",
        "description": "Illustrates best practices and major pitfalls of many different aspects of software development.",
        "cover_image_url": "https://images.unsplash.com/photo-1532012164546-f432f2e3777f?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 2, Shelf CS-104",
        "total_copies": 2,
        "available_copies": 1
    },
    {
        "title": "Introduction to Algorithms",
        "author": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
        "isbn": "9780262033848",
        "publisher": "MIT Press",
        "publication_year": 2009,
        "category": "Data Structures & Algorithms",
        "description": "Comprehensive reference covering a broad range of algorithms in depth, making their design and analysis accessible.",
        "cover_image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 2, Shelf ALGO-201",
        "total_copies": 4,
        "available_copies": 0
    },
    {
        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "author": "Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
        "isbn": "9780201633610",
        "publisher": "Addison-Wesley",
        "publication_year": 1994,
        "category": "Computer Science",
        "description": "Captures 23 classic solutions to common problems in software design, written by the Gang of Four.",
        "cover_image_url": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 2, Shelf CS-109",
        "total_copies": 2,
        "available_copies": 2
    },
    {
        "title": "Artificial Intelligence: A Modern Approach",
        "author": "Stuart Russell, Peter Norvig",
        "isbn": "9780136042594",
        "publisher": "Pearson",
        "publication_year": 2020,
        "category": "Artificial Intelligence",
        "description": "The leading textbook in Artificial Intelligence, presenting a unified view of intelligent agents.",
        "cover_image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 3, Shelf AI-301",
        "total_copies": 3,
        "available_copies": 3
    },
    {
        "title": "Deep Learning",
        "author": "Ian Goodfellow, Yoshua Bengio, Aaron Courville",
        "isbn": "9780262035613",
        "publisher": "MIT Press",
        "publication_year": 2016,
        "category": "Artificial Intelligence",
        "description": "A comprehensive introduction to mathematical foundations, deep feedforward networks, convolutional networks, and generative models.",
        "cover_image_url": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 3, Shelf AI-305",
        "total_copies": 2,
        "available_copies": 1
    },
    {
        "title": "Database System Concepts",
        "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
        "isbn": "9780073523323",
        "publisher": "McGraw-Hill",
        "publication_year": 2019,
        "category": "Databases & SQL",
        "description": "Covers relational databases, transactions, indexing, SQL architecture, and distributed database concepts.",
        "cover_image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 2, Shelf DB-110",
        "total_copies": 3,
        "available_copies": 1
    },
    {
        "title": "Malgudi Days",
        "author": "R. K. Narayan",
        "isbn": "9780140103182",
        "publisher": "Penguin Classics",
        "publication_year": 1982,
        "category": "Fiction & Literature",
        "description": "A collection of short stories revolving around the fictional South Indian town of Malgudi, exploring human foibles and warmth.",
        "cover_image_url": "https://images.unsplash.com/photo-1476275466078-4007374efbbe?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 1, Shelf LIT-405",
        "total_copies": 5,
        "available_copies": 4
    },
    {
        "title": "The Guide",
        "author": "R. K. Narayan",
        "isbn": "9788185986074",
        "publisher": "Indian Thought Publications",
        "publication_year": 1958,
        "category": "Fiction & Literature",
        "description": "The transformation of Raju from a tour guide to a spiritual leader. Winner of the Sahitya Akademi Award.",
        "cover_image_url": "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 1, Shelf LIT-408",
        "total_copies": 2,
        "available_copies": 0
    },
    {
        "title": "Sapiens: A Brief History of Humankind",
        "author": "Yuval Noah Harari",
        "isbn": "9780062316097",
        "publisher": "Harper",
        "publication_year": 2015,
        "category": "History & Anthropology",
        "description": "Explores how Homo sapiens came to dominate planet Earth through cognitive, agricultural, and scientific revolutions.",
        "cover_image_url": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 1, Shelf HIST-202",
        "total_copies": 4,
        "available_copies": 3
    },
    {
        "title": "A Brief History of Time",
        "author": "Stephen Hawking",
        "isbn": "9780553380163",
        "publisher": "Bantam Books",
        "publication_year": 1988,
        "category": "Physics & Cosmology",
        "description": "Landmark volume in science writing discussing the origin, nature, and fate of the universe.",
        "cover_image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 3, Shelf SCI-501",
        "total_copies": 3,
        "available_copies": 2
    },
    {
        "title": "Fluent Python: Clear, Concise, and Effective Programming",
        "author": "Luciano Ramalho",
        "isbn": "9781491946008",
        "publisher": "O'Reilly Media",
        "publication_year": 2021,
        "category": "Computer Science",
        "description": "Hands-on guide that shows how to write effective, idiomatic Python code by leveraging its best features.",
        "cover_image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&q=80&w=600",
        "shelf_location": "Floor 2, Shelf PY-101",
        "total_copies": 2,
        "available_copies": 2
    }
]


def init_demo_catalogue(db: Session, force: bool = False):
    """Initializes the database with sample catalogue records if the catalog is empty."""
    count = db.query(Book).count()
    if count == 0 or force:
        logger.info("Initializing library catalogue with demo dataset...")
        for book_data in DEMO_BOOKS:
            existing = db.query(Book).filter(Book.isbn == book_data["isbn"]).first()
            if not existing:
                book = Book(**book_data)
                db.add(book)
        db.commit()
        logger.info(f"Loaded {len(DEMO_BOOKS)} demo catalogue records.")
