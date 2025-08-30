# app/models/enums.py
import enum


# Matches Postgres type: difficultylevel (plus 'expert')
class DifficultyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


# Matches Postgres type: mechanics_enum
class Mechanics(str, enum.Enum):
    compound = "compound"
    isolation = "isolation"


# Matches Postgres type: workoutdifficulty (values are UPPERCASE strings)
class WorkoutDifficulty(str, enum.Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


# Matches Postgres type: workoutstatus (values are UPPERCASE strings)
class WorkoutStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


# Matches Postgres type: set_type_enum
class SetType(str, enum.Enum):
    working = "working"
    warmup = "warmup"
    dropset = "dropset"
    superset = "superset"
    cluster = "cluster"
    rest_pause = "rest_pause"
    mechanical_drop = "mechanical_drop"
    amrap = "amrap"
    tempo = "tempo"
    isometric = "isometric"
    partial = "partial"
    assisted = "assisted"
    negative = "negative"


# Matches Postgres type: rpe_scale_enum
class RPEScale(str, enum.Enum):
    rpe_10 = "rpe_10"
    rpe_20 = "rpe_20"
    percentage = "percentage"


# Matches Postgres type: rom_quality_enum
class ROMQuality(str, enum.Enum):
    full = "full"
    three_quarter = "three_quarter"
    half = "half"
    quarter = "quarter"
    partial_top = "partial_top"
    partial_bottom = "partial_bottom"
    variable = "variable"
