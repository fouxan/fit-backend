"""create exercise support tables

Revision ID: 8e44f69c59c5
Revises: a162706a1cd6
Create Date: 2025-08-14 17:57:42.575864

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8e44f69c59c5"
down_revision = "9d77c55283b2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # DifficultyLevel enum (scoped to exercise_catalog later)
    difficulty_enum = sa.Enum(
        "beginner", "intermediate", "advanced", name="difficultylevel"
    )
    difficulty_enum.create(op.get_bind(), checkfirst=True)

    # mechanics enum
    mechanics_enum = sa.Enum("compound", "isolation", name="mechanics_enum")
    mechanics_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "exercise_categories",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
    )

    op.create_table(
        "muscle_groups",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
    )

    op.create_table(
        "equipment",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
    )

    op.create_table(
        "movement_patterns",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
    )


def downgrade():
    op.drop_table("movement_patterns")
    op.drop_table("equipment")
    op.drop_table("muscle_groups")
    op.drop_table("exercise_categories")
    sa.Enum(name="mechanics_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="difficultylevel").drop(op.get_bind(), checkfirst=True)
