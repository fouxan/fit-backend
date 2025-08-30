"""Phase 2: Exercise system (biomechanics, variations)

Revision ID: b202c0a3e21e
Revises: b101f7f9c1a1
Create Date: 2025-08-21 19:12:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b202c0a3e21e"
down_revision = "b101f7f9c1a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # biomechanics
    op.create_table(
        "exercise_biomechanics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("primary_muscles", postgresql.JSONB, nullable=True),
        sa.Column("secondary_muscles", postgresql.JSONB, nullable=True),
        sa.Column("stabilizer_muscles", postgresql.JSONB, nullable=True),
        sa.Column("joints_involved", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("movement_plane", sa.String(20), nullable=True),
        sa.Column("optimal_rom_degrees", sa.Integer(), nullable=True),
        sa.Column("joint_angles", postgresql.JSONB, nullable=True),
        sa.Column("force_curve_type", sa.String(20), nullable=True),
        sa.Column("recommended_eccentric_seconds", sa.Numeric(3,1), nullable=True),
        sa.Column("recommended_pause_seconds", sa.Numeric(3,1), nullable=True),
        sa.Column("recommended_concentric_seconds", sa.Numeric(3,1), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise_catalog.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("exercise_id", name="uq_biomech_exercise_id")
    )

    # variations
    op.create_table(
        "exercise_variations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("parent_exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("variation_exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("variation_type", sa.String(20), nullable=True),  # progression/regression/lateral
        sa.Column("difficulty_modifier", sa.Numeric(3,2), nullable=True),
        sa.Column("variation_factors", postgresql.JSONB, nullable=True),
        sa.ForeignKeyConstraint(["parent_exercise_id"], ["exercise_catalog.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variation_exercise_id"], ["exercise_catalog.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("parent_exercise_id", "variation_exercise_id",
                            name="uq_exercise_variation_pair")
    )


def downgrade() -> None:
    op.drop_table("exercise_variations")
    op.drop_table("exercise_biomechanics")
