from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.database.base import Base

class Article(Base):
    __tablename__ = "articles"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(300),
        unique=True,
    )
    url: Mapped[str] = mapped_column(
        String(1000),
    )
    content: Mapped[str] = mapped_column(
        Text,
    )
    featured_image: Mapped[str] = mapped_column(
        String(1000),
    )
    published_at: Mapped[DateTime]
    author: Mapped[str] = mapped_column(
        String(200),
    )
