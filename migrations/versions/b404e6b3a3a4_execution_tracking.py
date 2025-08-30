"""Phase 4: Execution tracking (session_context, performances, set_executions, indexes)

Revision ID: b404e6b3a3a4
Revises: b303de88f19c
Create Date: 2025-08-21 19:18:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b404e6b3a3a4"
down_revision = "b303de88f19c"
branch_labels = None
depends_on = None


def upgrade() -> None:
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
    rpe_scale_enum = postgresql.ENUM(
        "rpe_10",
        "rpe_20",
        "percentage",
        name="rpe_scale_enum",
        create_type=False,
    )
    rom_quality_enum = postgresql.ENUM(
        "full",
        "three_quarter",
        "half",
        "quarter",
        "partial_top",
        "partial_bottom",
        "variable",
        name="rom_quality_enum",
        create_type=False,
    )

    op.create_table(
        "session_context",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workout_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("gym_location", sa.String(100), nullable=True),
        sa.Column("equipment_availability", postgresql.JSONB, nullable=True),
        sa.Column("crowd_level", sa.Integer(), nullable=True),
        sa.Column("temperature_celsius", sa.Integer(), nullable=True),
        sa.Column("sleep_hours", sa.Numeric(3, 1), nullable=True),
        sa.Column("sleep_quality", sa.Integer(), nullable=True),
        sa.Column("stress_level", sa.Integer(), nullable=True),
        sa.Column("energy_level", sa.Integer(), nullable=True),
        sa.Column("nutrition_timing", sa.String(20), nullable=True),
        sa.Column("caffeine_mg", sa.Integer(), nullable=True),
        sa.Column("other_supplements", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("time_of_day", sa.Time(), nullable=True),
        sa.Column("days_since_last_workout", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["workout_session_id"], ["workout_sessions.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("workout_session_id", name="uq_context_per_session"),
    )

    op.create_table(
        "exercise_performances",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("workout_session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "workout_block_exercise_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("performance_order", sa.Integer(), nullable=False),
        sa.Column("planned_sets", sa.Integer(), nullable=True),
        sa.Column("completed_sets", sa.Integer(), nullable=True),
        sa.Column("total_volume_kg", sa.Numeric(8, 2), nullable=True),
        sa.Column("total_reps", sa.Integer(), nullable=True),
        sa.Column("average_rpe", sa.Numeric(3, 1), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_rest_seconds", sa.Integer(), nullable=True),
        sa.Column("performance_notes", sa.Text(), nullable=True),
        sa.Column("technique_quality", sa.Integer(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["workout_session_id"], ["workout_sessions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["workout_block_exercise_id"],
            ["workout_block_exercises.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "workout_session_id",
            "performance_order",
            name="uq_performance_order_per_session",
        ),
    )

    op.create_table(
        "set_executions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "exercise_performance_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("set_protocol_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("set_number", sa.Integer(), nullable=False),
        sa.Column(
            "set_type",
            set_type_enum,
            server_default="working",
            nullable=False,
        ),
        sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True),
        sa.Column("reps_completed", sa.Integer(), nullable=True),
        sa.Column("reps_attempted", sa.Integer(), nullable=True),
        sa.Column("rpe_value", sa.Numeric(3, 1), nullable=True),
        sa.Column(
            "rpe_scale",
            rpe_scale_enum,
            server_default="rpe_10",
            nullable=False,
        ),
        sa.Column(
            "rom_quality",
            rom_quality_enum,
            server_default="full",
            nullable=False,
        ),
        sa.Column("eccentric_seconds", sa.Numeric(4, 2), nullable=True),
        sa.Column("pause_seconds", sa.Numeric(4, 2), nullable=True),
        sa.Column("concentric_seconds", sa.Numeric(4, 2), nullable=True),
        sa.Column(
            "partial_reps", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column(
            "assisted_reps", sa.Integer(), server_default=sa.text("0"), nullable=False
        ),
        sa.Column("range_of_motion_degrees", sa.Integer(), nullable=True),
        sa.Column("rest_before_seconds", sa.Integer(), nullable=True),
        sa.Column("rest_after_seconds", sa.Integer(), nullable=True),
        sa.Column("equipment_modifications", postgresql.JSONB, nullable=True),
        sa.Column("technique_breakdown_rep", sa.Integer(), nullable=True),
        sa.Column("pain_level", sa.Integer(), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("set_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["exercise_performance_id"],
            ["exercise_performances.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["set_protocol_id"], ["set_protocols.id"]),
        sa.UniqueConstraint(
            "exercise_performance_id", "set_number", name="uq_setnum_per_performance"
        ),
    )

    # ---- Indexes requested ----
    op.create_index(
        "idx_set_executions_performance",
        "set_executions",
        ["exercise_performance_id", "set_number"],
    )
    op.create_index(
        "idx_exercise_performances_session",
        "exercise_performances",
        ["workout_session_id", "performance_order"],
    )

    # Existing table index improvement: user/date on workout_sessions
    op.create_index(
        "idx_workout_sessions_user_date", "workout_sessions", ["user_id", "start_time"]
    )


def downgrade() -> None:
    op.drop_index("idx_workout_sessions_user_date", table_name="workout_sessions")
    op.drop_index(
        "idx_exercise_performances_session", table_name="exercise_performances"
    )
    op.drop_index("idx_set_executions_performance", table_name="set_executions")
    op.drop_table("set_executions")
    op.drop_table("exercise_performances")
    op.drop_table("session_context")
