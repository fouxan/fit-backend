"""finalize exercise schema

Revision ID: 525d23801613
Revises: c8dccb747126
Create Date: 2025-08-16 02:55:35.213006

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "525d23801613"
down_revision = "c8dccb747126"
branch_labels = None
depends_on = None


CATEGORIES = [
    "powerlifting",
    "strength",
    "stretching",
    "cardio",
    "olympic weightlifting",
    "strongman",
    "plyometrics",
]

EQUIPMENT = [
    "medicine ball",
    "dumbbell",
    "body only",
    "bands",
    "kettlebells",
    "foam roll",
    "cable",
    "machine",
    "barbell",
    "exercise ball",
    "e-z curl bar",
    "other",
]

MUSCLE_GROUPS = [
    "abdominals",
    "abductors",
    "adductors",
    "biceps",
    "calves",
    "chest",
    "forearms",
    "glutes",
    "hamstrings",
    "lats",
    "lower back",
    "middle back",
    "neck",
    "quadriceps",
    "shoulders",
    "traps",
    "triceps",
]


def upgrade() -> None:
    bind = op.get_bind()

    # 1) add 'expert' to existing difficultylevel (idempotent)
    # Postgres: can't drop enum labels; we extend it.
    op.execute("ALTER TYPE difficultylevel ADD VALUE IF NOT EXISTS 'expert'")

    # 2) create force_enum and add 'force' column (nullable)
    force_enum = sa.Enum("static", "pull", "push", name="force_enum")
    force_enum.create(bind, checkfirst=True)

    op.add_column(
        "exercise_catalog",
        sa.Column(
            "force", sa.Enum(name="force_enum", create_type=False), nullable=True
        ),
    )

    # 3) add external_id with regex check + unique index (nullable to start)
    #    pattern: ^[0-9a-zA-Z_-]+$
    op.add_column(
        "exercise_catalog",
        sa.Column("external_id", sa.String(), nullable=True),
    )
    op.create_check_constraint(
        "ck_exercise_catalog_external_id_format",
        "exercise_catalog",
        "external_id IS NULL OR external_id ~ '^[0-9A-Za-z_-]+$'",
    )
    op.create_index(
        "ix_exercise_catalog_external_id",
        "exercise_catalog",
        ["external_id"],
        unique=True,
        postgresql_where=sa.text("external_id IS NOT NULL"),
    )

    # 4) seed lookup tables to match schema enums (idempotent UPSERTs)
    # exercise_categories
    for name in CATEGORIES:
        bind.execute(
            sa.text(
                """
                INSERT INTO exercise_categories (id, name)
                VALUES (gen_random_uuid(), :name)
                ON CONFLICT (name) DO NOTHING
                """
            ),
            {"name": name},
        )

    # equipment
    for name in EQUIPMENT:
        bind.execute(
            sa.text(
                """
                INSERT INTO equipment (id, name)
                VALUES (gen_random_uuid(), :name)
                ON CONFLICT (name) DO NOTHING
                """
            ),
            {"name": name},
        )

    # muscle_groups
    for name in MUSCLE_GROUPS:
        bind.execute(
            sa.text(
                """
                INSERT INTO muscle_groups (id, name)
                VALUES (gen_random_uuid(), :name)
                ON CONFLICT (name) DO NOTHING
                """
            ),
            {"name": name},
        )


def downgrade() -> None:
    bind = op.get_bind()

    # 1) drop index & check, then external_id column
    op.drop_index("ix_exercise_catalog_external_id", table_name="exercise_catalog")
    op.drop_constraint(
        "ck_exercise_catalog_external_id_format",
        "exercise_catalog",
        type_="check",
    )
    op.drop_column("exercise_catalog", "external_id")

    # 2) drop force column then force_enum type
    op.drop_column("exercise_catalog", "force")
    sa.Enum(name="force_enum").drop(bind, checkfirst=True)

    # 3) We do NOT remove 'expert' from difficultylevel; Postgres enums
    #    cannot drop enum labels without complex hacks. This part is irreversible.
    # 4) We keep the seeded lookup rows; safe to leave them.
