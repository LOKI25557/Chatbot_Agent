from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint, func
from app.db.base import Base


class Book(Base):
    """
    Relational catalog model for library books.
    Maintains actual existence, metadata, and circulation availability.
    """
    __tablename__ = "books"

    __table_args__ = (
        CheckConstraint("total_copies >= 0", name="check_positive_total_copies"),
        CheckConstraint("available_copies >= 0", name="check_positive_available_copies"),
        CheckConstraint("available_copies <= total_copies", name="check_available_lte_total"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=True, index=True)
    isbn = Column(String(32), nullable=True, index=True)
    publisher = Column(String(255), nullable=True)
    publication_year = Column(Integer, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    shelf_location = Column(String(100), nullable=True)
    total_copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    @property
    def is_available(self) -> bool:
        """Returns True if there is at least one physical copy available for borrowing."""
        return self.available_copies > 0

    @property
    def borrowed_copies(self) -> int:
        """Calculates copies currently on circulation/borrowed."""
        return max(0, self.total_copies - self.available_copies)
