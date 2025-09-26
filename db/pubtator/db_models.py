import enum
from datetime import datetime, timezone

from db.utils.enum_and_constants import ProcessingStageEnum
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

POSTGRESQL_FALSE = "false"

FALSE_SERVER_DEFAULT = POSTGRESQL_FALSE


Base = declarative_base()

article_genes = Table(
    "article_genes",
    Base.metadata,
    Column(
        "article_id",
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "gene_id", Integer, ForeignKey("genes.id", ondelete="CASCADE"), primary_key=True
    ),
)

article_diseases = Table(
    "article_diseases",
    Base.metadata,
    Column(
        "article_id",
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "disease_id",
        Integer,
        ForeignKey("diseases.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

article_variants = Table(
    "article_variants",
    Base.metadata,
    Column(
        "article_id",
        Integer,
        ForeignKey("articles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "variant_id",
        Integer,
        ForeignKey("variants.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    pm_id = Column(String, nullable=False, unique=True)
    pmc_id = Column(String, nullable=True, unique=True)

    genes = relationship("Gene", secondary=article_genes, back_populates="articles")
    diseases = relationship(
        "Disease", secondary=article_diseases, back_populates="articles"
    )
    variants = relationship(
        "Variant", secondary=article_variants, back_populates="articles"
    )

    download_status = relationship(
        "DownloadStatus", uselist=False, back_populates="article"
    )
    text_parse_status = relationship(
        "TextParseStatus", uselist=False, back_populates="article"
    )
    supplementary_parse_status = relationship(
        "SupplementaryParseStatus", uselist=False, back_populates="article"
    )
    search_status = relationship(
        "SearchStatus", uselist=False, back_populates="article"
    )
    w3c_status = relationship("W3CStatus", uselist=False, back_populates="article")
    submission_status = relationship(
        "SubmissionStatus", uselist=False, back_populates="article"
    )

    processing_stage = relationship(
        "ArticleProcessingStage", uselist=False, back_populates="article"
    )


class Gene(Base):
    __tablename__ = "genes"
    id = Column(Integer, primary_key=True)
    ncbi_id = Column(String, unique=True, nullable=False)
    hgnc_symbol = Column(String, unique=True, nullable=True)

    articles = relationship("Article", secondary=article_genes, back_populates="genes")

    def __repr__(self):
        return f"<Gene(id={self.id}, ncbi_id={self.ncbi_id}, hgnc_symbol={self.hgnc_symbol})>"

    def search_format(self):
        return [self.ncbi_id, self.hgnc_symbol]


class Disease(Base):
    __tablename__ = "diseases"
    id = Column(Integer, primary_key=True)
    original_ontology = Column(String, unique=True, nullable=False)
    mondo_id = Column(String, nullable=True)

    articles = relationship(
        "Article", secondary=article_diseases, back_populates="diseases"
    )

    def __repr__(self):
        return f"<Disease(id={self.id}, original_ontology={self.original_ontology}, mondo_id={self.mondo_id})>"

    def search_format(self):
        if self.mondo_id:
            return [self.original_ontology, self.mondo_id]
        return [self.original_ontology]

class Variant(Base):
    __tablename__ = "variants"
    id = Column(Integer, primary_key=True)
    exact_match = Column(String, unique=True, nullable=False)
    identified = Column(String, nullable=False)

    articles = relationship(
        "Article", secondary=article_variants, back_populates="variants"
    )

    def __repr__(self):
        return f"<Variant(id={self.id}, exact_match={self.exact_match}, identified={self.identified})>"

    def search_format(self):
        return [self.identified, self.exact_match]


class DownloadStatus(Base):
    __tablename__ = "download_statuses"
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    is_downloaded = Column(
        Boolean, default=False, server_default=FALSE_SERVER_DEFAULT, nullable=False
    )
    downloaded_date = Column(DateTime)

    article = relationship("Article", back_populates="download_status")


class TextParseStatus(Base):
    __tablename__ = "text_parse_statuses"
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    is_parsed = Column(
        Boolean, default=False, server_default=FALSE_SERVER_DEFAULT, nullable=False
    )
    parsed_date = Column(DateTime)
    parsed_path = Column(Text)

    article = relationship("Article", back_populates="text_parse_status")


class SupplementaryParseStatus(Base):
    __tablename__ = "supplementary_parse_statuses"
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    is_parsed = Column(
        Boolean, default=False, server_default=FALSE_SERVER_DEFAULT, nullable=False
    )
    parsed_date = Column(DateTime)
    parsed_path = Column(Text)

    article = relationship("Article", back_populates="supplementary_parse_status")


class SearchStatus(Base):
    __tablename__ = "search_statuses"
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    is_searched = Column(
        Boolean, default=False, server_default=FALSE_SERVER_DEFAULT, nullable=False
    )
    searched_date = Column(DateTime)
    searched_path = Column(Text)

    article = relationship("Article", back_populates="search_status")


class W3CStatus(Base):
    __tablename__ = "w3c_statuses"
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    is_w3c = Column(
        Boolean, default=False, server_default=FALSE_SERVER_DEFAULT, nullable=False
    )
    w3c_date = Column(DateTime)
    w3c_path = Column(Text)

    article = relationship("Article", back_populates="w3c_status")


class SubmissionStatus(Base):
    __tablename__ = "submission_statuses"
    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    is_submitted = Column(
        Boolean, default=False, server_default=FALSE_SERVER_DEFAULT, nullable=False
    )
    submitted_date = Column(DateTime)
    submitted_response = Column(Text)

    article = relationship("Article", back_populates="submission_status")


# class ProcessingStageEnum(enum.Enum):
#     pending_download = "pending_download"
#     pending_parse_text = "pending_parse_text"
#     pending_parse_supplementary = "pending_parse_supplementary"
#     pending_search = "pending_search"
#     pending_w3c = "pending_w3c"
#     pending_submission = "pending_submission"
#     complete = "complete"


class ArticleProcessingStage(Base):
    __tablename__ = "article_processing_stages"

    article_id = Column(
        Integer, ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True
    )
    current_stage = Column(Enum(ProcessingStageEnum), nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    last_error = Column(Text, nullable=True)

    article = relationship("Article", back_populates="processing_stage")


class ProcessingStageHistory(Base):
    __tablename__ = "processing_stage_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"))
    stage = Column(Enum(ProcessingStageEnum), nullable=False)
    status = Column(String, nullable=False)  # 'success', 'error', 'skipped'
    error_message = Column(Text, nullable=True)
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    article = relationship("Article", backref="stage_history")
