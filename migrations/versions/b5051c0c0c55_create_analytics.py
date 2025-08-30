"""Phase 5: Analytics (volume_analytics, strength_progressions, insights, usage, views)

Revision ID: b5051c0c0c55
Revises: b404e6b3a3a4
Create Date: 2025-08-21 19:22:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "b5051c0c0c55"
down_revision = "b404e6b3a3a4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # volume analytics
    op.create_table(
        "volume_analytics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("calculation_date", sa.Date(), nullable=False),
        sa.Column("period_type", sa.String(10), nullable=False),  # daily, weekly, monthly
        sa.Column("total_volume_kg", sa.Numeric(10,2), nullable=True),
        sa.Column("total_sets", sa.Integer(), nullable=True),
        sa.Column("total_reps", sa.Integer(), nullable=True),
        sa.Column("average_intensity", sa.Numeric(5,2), nullable=True),
        sa.Column("volume_by_muscle_group", postgresql.JSONB, nullable=True),
        sa.Column("volume_by_movement", postgresql.JSONB, nullable=True),
        sa.Column("volume_per_hour", sa.Numeric(8,2), nullable=True),
        sa.Column("sets_per_hour", sa.Numeric(6,2), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id","calculation_date","period_type",
                            name="uq_volume_unique_period")
    )
    op.create_index("idx_volume_analytics_user_period", "volume_analytics",
                    ["user_id","period_type","calculation_date"])

    # strength progressions
    op.create_table(
        "strength_progressions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exercise_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("measurement_date", sa.Date(), nullable=False),
        sa.Column("estimated_1rm_kg", sa.Numeric(6,2), nullable=True),
        sa.Column("estimation_method", sa.String(20), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3,2), nullable=True),
        sa.Column("base_weight_kg", sa.Numeric(6,2), nullable=True),
        sa.Column("base_reps", sa.Integer(), nullable=True),
        sa.Column("base_rpe", sa.Numeric(3,1), nullable=True),
        sa.Column("volume_pr", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("weight_pr", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("reps_pr", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["exercise_id"], ["exercise_catalog.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id","exercise_id","measurement_date",
                            name="uq_strength_progression_daily")
    )
    op.create_index("idx_strength_progressions_user_exercise", "strength_progressions",
                    ["user_id","exercise_id","measurement_date"])

    # insight data points
    op.create_table(
        "insight_data_points",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("data_type", sa.String(50), nullable=False),
        sa.Column("measurement_date", sa.Date(), nullable=False),
        sa.Column("numeric_value", sa.Numeric(10,4), nullable=True),
        sa.Column("text_value", sa.Text(), nullable=True),
        sa.Column("json_value", postgresql.JSONB, nullable=True),
        sa.Column("source_table", sa.String(50), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("confidence_score", sa.Numeric(3,2), nullable=True),
        sa.Column("calculation_method", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )
    op.create_index("idx_insight_data_points_user_type_date", "insight_data_points",
                    ["user_id","data_type","measurement_date"])

    # user insights
    op.create_table(
        "user_insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("insight_type", sa.String(50), nullable=False),
        sa.Column("insight_category", sa.String(30), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("confidence_score", sa.Numeric(3,2), nullable=False),
        sa.Column("recommendations", postgresql.JSONB, nullable=True),
        sa.Column("supporting_data_ids", postgresql.ARRAY(postgresql.UUID(as_uuid=True)), nullable=True),
        sa.Column("chart_data", postgresql.JSONB, nullable=True),
        sa.Column("is_read", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_dismissed", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("user_feedback", sa.Integer(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE")
    )

    # feature usage
    op.create_table(
        "feature_usage",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True,
                  server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("feature_name", sa.String(50), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("usage_count", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("daily_limit", sa.Integer(), nullable=True),
        sa.Column("monthly_limit", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id","feature_name","usage_date",
                            name="uq_feature_usage_day")
    )
    op.create_index("idx_feature_usage_user_feature_date", "feature_usage",
                    ["user_id","feature_name","usage_date"])

    # ---- Views ----
    op.execute("""
    CREATE OR REPLACE VIEW latest_strength_estimates AS
    SELECT DISTINCT ON (user_id, exercise_id)
        user_id, exercise_id, estimated_1rm_kg, measurement_date, confidence_score
    FROM strength_progressions
    ORDER BY user_id, exercise_id, measurement_date DESC;
    """)

    op.execute("""
    CREATE OR REPLACE VIEW weekly_volume_summary AS
    SELECT 
        user_id,
        DATE_TRUNC('week', calculation_date) AS week_start,
        SUM(total_volume_kg) AS weekly_volume,
        SUM(total_sets) AS weekly_sets,
        AVG(average_intensity) AS avg_weekly_intensity
    FROM volume_analytics
    WHERE period_type = 'daily'
    GROUP BY user_id, DATE_TRUNC('week', calculation_date);
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS weekly_volume_summary")
    op.execute("DROP VIEW IF EXISTS latest_strength_estimates")
    op.drop_index("idx_feature_usage_user_feature_date", table_name="feature_usage")
    op.drop_table("feature_usage")
    op.drop_index("idx_insight_data_points_user_type_date", table_name="insight_data_points")
    op.drop_table("user_insights")
    op.drop_table("insight_data_points")
    op.drop_index("idx_strength_progressions_user_exercise", table_name="strength_progressions")
    op.drop_table("strength_progressions")
    op.drop_index("idx_volume_analytics_user_period", table_name="volume_analytics")
    op.drop_table("volume_analytics")
