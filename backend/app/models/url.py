from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy import String, Integer, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

class URL(Base):
    __tablename__ = "urls"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid4,
        doc="Unique identifier for the shortened URL record."
    )

    original_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
        doc="The original long destination URL."
    )

    short_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
        doc="The unique short code used to resolve to the original URL."
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
        doc="The timestamp when the shortened URL was created."
    )

    click_count: Mapped[int] = mapped_column(
        Integer,
        server_default="0",
        nullable=False,
        doc="The number of times the shortened URL has been visited."
    )

    def __repr__(self) -> str:
        return f"<URL id={self.id} short_code={self.short_code!r} click_count={self.click_count}>"
