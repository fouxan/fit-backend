# app/schemas/enums.py
from enum import Enum


# DB: difficultylevel (plus 'expert')
class DifficultyLevel(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


# DB: mechanics_enum
class Mechanics(str, Enum):
    compound = "compound"
    isolation = "isolation"


# DB: workoutdifficulty (UPPERCASE)
class WorkoutDifficulty(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


# DB: workoutstatus (UPPERCASE)
class WorkoutStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


# DB: set_type_enum
class SetType(str, Enum):
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


# DB: rpe_scale_enum
class RPEScale(str, Enum):
    rpe_10 = "rpe_10"
    rpe_20 = "rpe_20"
    percentage = "percentage"


# DB: rom_quality_enum
class ROMQuality(str, Enum):
    full = "full"
    three_quarter = "three_quarter"
    half = "half"
    quarter = "quarter"
    partial_top = "partial_top"
    partial_bottom = "partial_bottom"
    variable = "variable"


# DB: workout_block_type_enum
class WorkoutBlockType(str, Enum):
    straight_sets = "straight_sets"
    superset = "superset"
    giant_set = "giant_set"
    circuit = "circuit"
    emom = "emom"
    ladder = "ladder"
    complex = "complex"
