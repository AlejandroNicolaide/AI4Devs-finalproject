"""add hnsw index on document_chunks embedding

Revision ID: a1hnsw0001
Revises: 930158f5ca9e
Create Date: 2026-10-23

"""
from typing import Sequence, Union

from alembic import op

revision: str = "a1hnsw0001"
down_revision: Union[str, Sequence[str], None] = "930158f5ca9e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
