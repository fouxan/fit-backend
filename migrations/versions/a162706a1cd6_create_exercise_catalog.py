"""create exercise catalog

Revision ID: a162706a1cd6
Revises: 9d77c55283b2
Create Date: 2025-08-14 17:56:10.616948

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM


# revision identifiers, used by Alembic.
revision = "a162706a1cd6"
down_revision = "8e44f69c59c5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "exercise_catalog",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column(
            "difficulty",
            ENUM(name="difficultylevel", create_type=False),
            nullable=False,
        ),
        sa.Column(
            "is_custom", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "created_by_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column(
            "category_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_categories.id"),
            nullable=False,
        ),
        sa.Column("video_url", sa.String(), nullable=True),
        sa.Column(
            "image_urls", sa.dialects.postgresql.ARRAY(sa.String()), nullable=True
        ),
        sa.Column(
            "mechanics",
            ENUM(name="mechanics_enum", create_type=False),
            nullable=False,
            server_default="compound",
        ),
        sa.Column(
            "unilateral", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column("default_tempo", sa.String(), nullable=True),
        sa.Column(
            "is_bodyweight",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "supports_gps",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "supports_pool",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "supports_hr", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("cadence_metric", sa.String(), nullable=True),
        sa.Column("notes", sa.dialects.postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("default_sport_profile", sa.String(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
    )

    op.create_table(
        "exercise_muscle_groups",
        sa.Column(
            "exercise_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "muscle_group_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("muscle_groups.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "exercise_equipment",
        sa.Column(
            "exercise_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "equipment_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("equipment.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )

    op.create_table(
        "exercise_movement_patterns",
        sa.Column(
            "exercise_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exercise_catalog.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "movement_pattern_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("movement_patterns.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade():
    op.drop_table("exercise_movement_patterns")
    op.drop_table("exercise_equipment")
    op.drop_table("exercise_muscle_groups")
    op.drop_table("exercise_catalog")
