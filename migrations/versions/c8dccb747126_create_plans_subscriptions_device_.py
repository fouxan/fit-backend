"""create plans, subscriptions, device connections

Revision ID: c8dccb747126
Revises: a162706a1cd6
Create Date: 2025-08-14 18:45:29.303688

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c8dccb747126"
down_revision = "a162706a1cd6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- plans ---
    op.create_table(
        "plans",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("type", sa.String(), nullable=False),  # using plain string per model
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),  # cents
        sa.Column("stripe_price_id", sa.String(), nullable=True),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
    )
    op.create_index("ix_plans_type", "plans", ["type"])
    op.create_index("ix_plans_name", "plans", ["name"])

    # --- subscriptions ---
    op.create_table(
        "subscriptions",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stripe_subscription_id", sa.String(), nullable=True),
        sa.Column("stripe_customer_id", sa.String(), nullable=True),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "cancel_at_period_end",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_subscriptions_user_id_users",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["plans.id"],
            name="fk_subscriptions_plan_id_plans",
            ondelete="RESTRICT",
        ),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_plan_id", "subscriptions", ["plan_id"])
    op.create_index("ix_subscriptions_active", "subscriptions", ["is_active"])

    # helpful uniqueness guardrails (optional but recommended):
    op.create_unique_constraint(
        "uq_subscriptions_user_active",
        "subscriptions",
        ["user_id", "is_active"],
        # Note: Postgres can't do partial unique here via Alembic in a portable way.
        # If you only allow ONE active sub per user, consider a partial unique index:
        # op.execute("CREATE UNIQUE INDEX uq_subscriptions_user_active_true ON subscriptions(user_id) WHERE is_active")
    )

    # --- device_connections ---
    op.create_table(
        "device_connections",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),  # e.g., Fitbit, Garmin
        sa.Column(
            "device_type", sa.String(), nullable=False
        ),  # smartwatch, fitness_tracker
        sa.Column("device_id", sa.String(), nullable=False),  # provider device id
        sa.Column("connected_at", sa.String(), nullable=False),  # per model: string
        sa.Column("scopes", sa.dialects.postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="active"),
        sa.Column("access_meta", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_device_connections_user_id_users",
            ondelete="CASCADE",
        ),
    )
    # A device_id may be reused across providers; enforce uniqueness per user+provider+device_id
    op.create_unique_constraint(
        "uq_device_connections_user_provider_device",
        "device_connections",
        ["user_id", "provider", "device_id"],
    )
    op.create_index(
        "ix_device_connections_provider", "device_connections", ["provider"]
    )
    op.create_index("ix_device_connections_status", "device_connections", ["status"])


def downgrade() -> None:
    op.drop_index("ix_device_connections_status", table_name="device_connections")
    op.drop_index("ix_device_connections_provider", table_name="device_connections")
    op.drop_constraint(
        "uq_device_connections_user_provider_device",
        "device_connections",
        type_="unique",
    )
    op.drop_table("device_connections")

    op.drop_constraint("uq_subscriptions_user_active", "subscriptions", type_="unique")
    op.drop_index("ix_subscriptions_active", table_name="subscriptions")
    op.drop_index("ix_subscriptions_plan_id", table_name="subscriptions")
    op.drop_index("ix_subscriptions_user_id", table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index("ix_plans_name", table_name="plans")
    op.drop_index("ix_plans_type", table_name="plans")
    op.drop_table("plans")
