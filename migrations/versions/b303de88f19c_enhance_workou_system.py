"""Phase 3: Workout structure (blocks, block exercises, protocols)

Revision ID: b303de88f19c
Revises: b202c0a3e21e
Create Date: 2025-08-21 19:14:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b303de88f19c"
down_revision = "b202c0a3e21e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    wb_enum = postgresql.ENUM(
        "straight_sets",
        "superset",
        "giant_set",
        "circuit",
        "emom",
        "ladder",
        "complex",
        name="workout_block_type_enum",
        create_type=False,  # <-- reference existing type from Phase 1
    )

    set_type_enum = postgresql.ENUM(
        "working",
        "warmup",
        "dropset",
        "superset",
        "cluster",
        "rest_pause",
        "mechanical_drop",
        "amrap",
        "tempo",
        "isometric",
        "partial",
        "assisted",
        "negative",
        name="set_type_enum",
        create_type=False,
    )

    op.create_table(
        "workout_blocks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workout_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("block_order", sa.Integer(), nullable=False),
        sa.Column("block_name", sa.String(100), nullable=True),
        sa.Column(
            "block_type",
            wb_enum,
            nullable=False,
            server_default="straight_sets",
        ),
        sa.Column("rest_between_exercises", sa.Integer(), nullable=True),
        sa.Column("rounds", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("round_rest_seconds", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(["workout_id"], ["workouts.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "workout_id", "block_order", name="uq_block_order_per_workout"
        ),
    )

    op.create_table(
        "workout_block_exercises",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workout_block_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_order", sa.Integer(), nullable=False),
        sa.Column("target_sets", sa.Integer(), nullable=True),
        sa.Column("target_reps_min", sa.Integer(), nullable=True),
        sa.Column("target_reps_max", sa.Integer(), nullable=True),
        sa.Column("target_weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("target_rpe", sa.Numeric(3, 1), nullable=True),
        sa.Column("rest_after_seconds", sa.Integer(), nullable=True),
        sa.Column("tempo_prescription", sa.String(20), nullable=True),
        sa.Column("equipment_variant", postgresql.JSONB, nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["workout_block_id"], ["workout_blocks.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["exercise_id"], ["exercise_catalog.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint(
            "workout_block_id", "exercise_order", name="uq_ex_order_per_block"
        ),
    )

    op.create_table(
        "set_protocols",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "workout_block_exercise_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column(
            "protocol_type", set_type_enum, nullable=False
        ),
        sa.Column("set_order", sa.Integer(), nullable=False),
        sa.Column("protocol_data", postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["workout_block_exercise_id"],
            ["workout_block_exercises.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "workout_block_exercise_id", "set_order", name="uq_protocol_order_per_ex"
        ),
    )


def downgrade() -> None:
    op.drop_table("set_protocols")
    op.drop_table("workout_block_exercises")
    op.drop_table("workout_blocks")
