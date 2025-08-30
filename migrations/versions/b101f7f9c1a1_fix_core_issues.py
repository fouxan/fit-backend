"""Phase 1: Foundation (enums, user prefs, user cols, pgcrypto, triggers)

Revision ID: b101f7f9c1a1
Revises: 88a6b0e55e58
Create Date: 2025-08-21 19:10:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b101f7f9c1a1"
down_revision = "88a6b0e55e58"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure pgcrypto for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # ---- Enums (llm/workout tracking) ----
    postgresql.ENUM(
        "working","warmup","dropset","superset","cluster","rest_pause","mechanical_drop",
        "amrap","tempo","isometric","partial","assisted","negative",
        name="set_type_enum"
    ).create(op.get_bind(), checkfirst=True)

    postgresql.ENUM(
        "straight_sets","superset","giant_set","circuit","emom","ladder","complex",
        name="workout_block_type_enum"
    ).create(op.get_bind(), checkfirst=True)

    postgresql.ENUM("rpe_10","rpe_20","percentage", name="rpe_scale_enum")\
        .create(op.get_bind(), checkfirst=True)

    postgresql.ENUM(
        "full","three_quarter","half","quarter","partial_top","partial_bottom","variable",
        name="rom_quality_enum"
    ).create(op.get_bind(), checkfirst=True)

    # ---- Users: add columns (idempotent, nullable) ----
    with op.batch_alter_table("users") as b:
        b.add_column(sa.Column("training_experience", sa.String(20), nullable=True))
        b.add_column(sa.Column("primary_goals", postgresql.ARRAY(sa.Text()), nullable=True))
        b.add_column(sa.Column("injury_history", postgresql.JSONB, nullable=True))
        b.add_column(sa.Column("training_frequency", sa.Integer(), nullable=True))

    # ---- Preferences table ----
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("preferred_units", sa.String(10), server_default=sa.text("'metric'"), nullable=False),
        sa.Column("default_rest_seconds", sa.Integer(), server_default=sa.text("120"), nullable=False),
        sa.Column("track_rpe", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("track_rom", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("track_tempo", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("workout_reminders", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("progress_updates", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("insight_notifications", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("share_workouts", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("research_participation", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", name="uq_user_preferences_user")
    )

    # ---- Utility: updated_at trigger (generic) ----
    op.execute("""
    CREATE OR REPLACE FUNCTION set_updated_at()
    RETURNS trigger AS $$
    BEGIN
      NEW.updated_at = now();
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    # Attach the trigger to tables that have updated_at and benefit from it
    for tbl in [
        "users", "user_preferences", "workout_plans", "workouts",
        "workout_exercises", "workout_sessions", "exercise_sets",
        "exercise_catalog", "exercise_categories", "equipment", "movement_patterns",
        "muscle_groups", "plans", "subscriptions", "device_connections"
    ]:
        op.execute(f"""
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name='{tbl}' AND column_name='updated_at'
          ) THEN
            DROP TRIGGER IF EXISTS {tbl}_set_updated_at ON {tbl};
            CREATE TRIGGER {tbl}_set_updated_at
            BEFORE UPDATE ON {tbl}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
          END IF;
        END;
        $$;
        """)


def downgrade() -> None:
    # drop trigger attachments
    for tbl in [
        "users", "user_preferences", "workout_plans", "workouts",
        "workout_exercises", "workout_sessions", "exercise_sets",
        "exercise_catalog", "exercise_categories", "equipment", "movement_patterns",
        "muscle_groups", "plans", "subscriptions", "device_connections"
    ]:
        op.execute(f"DROP TRIGGER IF EXISTS {tbl}_set_updated_at ON {tbl};")

    op.execute("DROP FUNCTION IF EXISTS set_updated_at()")

    op.drop_table("user_preferences")

    with op.batch_alter_table("users") as b:
        b.drop_column("training_frequency")
        b.drop_column("injury_history")
        b.drop_column("primary_goals")
        b.drop_column("training_experience")

    sa.Enum(name="rom_quality_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="rpe_scale_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="workout_block_type_enum").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="set_type_enum").drop(op.get_bind(), checkfirst=True)
