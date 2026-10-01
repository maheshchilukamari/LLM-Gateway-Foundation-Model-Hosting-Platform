"""Initial platform metadata tables.

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-30
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key_hash", sa.String(length=128), nullable=False),
        sa.Column("owner", sa.String(length=128), nullable=False),
        sa.Column("scopes", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("key_hash"),
    )
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"])
    op.create_table(
        "models",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_id", sa.String(length=256), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("task_type", sa.String(length=64), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.UniqueConstraint("model_id"),
    )
    op.create_index("ix_models_model_id", "models", ["model_id"])
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_id", sa.String(length=256), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("artifact_source", sa.Text(), nullable=False),
        sa.Column("deployment_config", sa.JSON(), nullable=False),
    )
    op.create_table(
        "request_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("model_requested", sa.String(length=256), nullable=False),
        sa.Column("model_used", sa.String(length=256), nullable=False),
        sa.Column("routing_strategy", sa.String(length=64), nullable=False),
        sa.Column("prompt_hash", sa.String(length=128), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("estimated_cost", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("request_id"),
    )
    op.create_index("ix_request_logs_request_id", "request_logs", ["request_id"])
    op.create_table(
        "routing_decisions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.String(length=64), nullable=False),
        sa.Column("model_id", sa.String(length=256), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("strategy", sa.String(length=64), nullable=False),
        sa.Column("decision_metadata", sa.JSON(), nullable=False),
    )
    op.create_table(
        "model_health",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("model_id", sa.String(length=256), nullable=False),
        sa.Column("health_status", sa.String(length=32), nullable=False),
        sa.Column("p95_latency_ms", sa.Float(), nullable=True),
        sa.Column("error_rate", sa.Float(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "rag_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.String(length=256), nullable=False),
        sa.Column("collection", sa.String(length=128), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("rag_documents")
    op.drop_table("model_health")
    op.drop_table("routing_decisions")
    op.drop_index("ix_request_logs_request_id", table_name="request_logs")
    op.drop_table("request_logs")
    op.drop_table("model_versions")
    op.drop_index("ix_models_model_id", table_name="models")
    op.drop_table("models")
    op.drop_index("ix_api_keys_key_hash", table_name="api_keys")
    op.drop_table("api_keys")
