-- ===================================================================
-- SCIENCE-BASED FITNESS TRACKER DATABASE SCHEMA
-- Designed for LLM insights and advanced workout tracking
-- ===================================================================

-- ===================================================================
-- ENUMS & TYPES
-- ===================================================================

CREATE TYPE set_type_enum AS ENUM (
    'working',          -- Standard working set
    'warmup',           -- Warm-up set
    'dropset',          -- Drop set (multiple weight drops)
    'superset',         -- Part of a superset
    'cluster',          -- Cluster set (intra-set rest)
    'rest_pause',       -- Rest-pause set
    'mechanical_drop',  -- Mechanical advantage dropset
    'amrap',            -- As many reps as possible
    'tempo',            -- Tempo-focused set
    'isometric',        -- Isometric hold
    'partial',          -- Partial range of motion
    'assisted',         -- Assisted reps (forced reps)
    'negative'          -- Negative-only reps
);

CREATE TYPE workout_block_type_enum AS ENUM (
    'straight_sets',    -- Individual exercises
    'superset',         -- 2 exercises back-to-back
    'giant_set',        -- 3+ exercises back-to-back
    'circuit',          -- Timed circuit
    'emom',             -- Every minute on the minute
    'ladder',           -- Ascending/descending reps
    'complex'           -- Complex training (strength + power)
);

CREATE TYPE rpe_scale_enum AS ENUM (
    'rpe_10',          -- Traditional 1-10 RPE
    'rpe_20',          -- 1-20 scale for more precision
    'percentage'       -- % of 1RM
);

CREATE TYPE rom_quality_enum AS ENUM (
    'full',            -- Full range of motion
    'three_quarter',   -- 75% ROM
    'half',            -- 50% ROM  
    'quarter',         -- 25% ROM
    'partial_top',     -- Top portion only
    'partial_bottom',  -- Bottom portion only
    'variable'         -- Variable ROM within set
);

-- ===================================================================
-- USER MANAGEMENT (Enhanced)
-- ===================================================================

-- Enhanced user profile with training context
ALTER TABLE users ADD COLUMN IF NOT EXISTS training_experience VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS primary_goals TEXT[];
ALTER TABLE users ADD COLUMN IF NOT EXISTS injury_history JSONB;
ALTER TABLE users ADD COLUMN IF NOT EXISTS training_frequency INTEGER;

-- User training preferences
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Training preferences
    preferred_units VARCHAR(10) DEFAULT 'metric', -- metric/imperial
    default_rest_seconds INTEGER DEFAULT 120,
    track_rpe BOOLEAN DEFAULT true,
    track_rom BOOLEAN DEFAULT false,  -- Pro feature
    track_tempo BOOLEAN DEFAULT false, -- Pro feature
    
    -- Notification settings
    workout_reminders BOOLEAN DEFAULT true,
    progress_updates BOOLEAN DEFAULT true,
    insight_notifications BOOLEAN DEFAULT true,
    
    -- Privacy settings
    share_workouts BOOLEAN DEFAULT false,
    research_participation BOOLEAN DEFAULT false, -- Pro feature
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===================================================================
-- EXERCISE SYSTEM (Redesigned)
-- ===================================================================

-- Biomechanics data for exercises
CREATE TABLE exercise_biomechanics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exercise_id UUID NOT NULL REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    
    -- Muscle activation (0-100 scale)
    primary_muscles JSONB, -- {"quadriceps": 95, "glutes": 80}
    secondary_muscles JSONB,
    stabilizer_muscles JSONB,
    
    -- Joint involvement
    joints_involved TEXT[], -- ["knee", "hip", "ankle"]
    movement_plane VARCHAR(20), -- sagittal, frontal, transverse
    
    -- Biomechanical parameters
    optimal_rom_degrees INTEGER,
    joint_angles JSONB, -- {"knee_bottom": 90, "hip_bottom": 45}
    force_curve_type VARCHAR(20), -- ascending, descending, bell
    
    -- Tempo recommendations
    recommended_eccentric_seconds DECIMAL(3,1),
    recommended_pause_seconds DECIMAL(3,1),
    recommended_concentric_seconds DECIMAL(3,1),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Exercise variations and progressions
CREATE TABLE exercise_variations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_exercise_id UUID REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    variation_exercise_id UUID REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    
    variation_type VARCHAR(20), -- progression, regression, lateral
    difficulty_modifier DECIMAL(3,2), -- 1.0 = same, 1.2 = 20% harder
    
    -- What makes this a variation
    variation_factors JSONB, -- {"grip": "wide", "stance": "narrow", "tempo": "slow"}
    
    UNIQUE(parent_exercise_id, variation_exercise_id)
);

-- ===================================================================
-- WORKOUT STRUCTURE (Completely Redesigned)
-- ===================================================================

-- Workout blocks for organizing exercises
CREATE TABLE workout_blocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_id UUID NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    
    block_order INTEGER NOT NULL,
    block_name VARCHAR(100),
    block_type workout_block_type_enum NOT NULL DEFAULT 'straight_sets',
    
    -- Block-level parameters
    rest_between_exercises INTEGER, -- seconds
    rounds INTEGER DEFAULT 1, -- for circuits
    round_rest_seconds INTEGER, -- rest between rounds
    
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Exercises within workout blocks
CREATE TABLE workout_block_exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_block_id UUID NOT NULL REFERENCES workout_blocks(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    
    exercise_order INTEGER NOT NULL,
    
    -- Set planning
    target_sets INTEGER,
    target_reps_min INTEGER,
    target_reps_max INTEGER,
    target_weight_kg DECIMAL(6,2),
    target_rpe DECIMAL(3,1),
    
    -- Timing
    rest_after_seconds INTEGER,
    tempo_prescription VARCHAR(20), -- "3-1-2-1" format
    
    -- Equipment specifications
    equipment_variant JSONB, -- {"grip": "wide", "stance": "shoulder_width"}
    
    notes TEXT
);

-- Advanced set schemas for complex protocols
CREATE TABLE set_protocols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_block_exercise_id UUID NOT NULL REFERENCES workout_block_exercises(id) ON DELETE CASCADE,
    
    protocol_type set_type_enum NOT NULL,
    set_order INTEGER NOT NULL,
    
    -- Protocol-specific parameters
    protocol_data JSONB, -- Flexible storage for different protocols
    -- Examples:
    -- Dropset: {"drops": [{"weight_kg": 80, "reps": 8}, {"weight_kg": 60, "reps": 12}]}
    -- Cluster: {"mini_sets": 3, "reps_per_mini": 3, "intra_rest_seconds": 15}
    -- Rest-pause: {"initial_reps": 8, "pause_reps": [3, 2, 2]}
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===================================================================
-- WORKOUT EXECUTION (Science-Based Tracking)
-- ===================================================================

-- Session context for environmental factors
CREATE TABLE session_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_session_id UUID NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    
    -- Environmental
    gym_location VARCHAR(100),
    equipment_availability JSONB,
    crowd_level INTEGER, -- 1-5 scale
    temperature_celsius INTEGER,
    
    -- Pre-workout state
    sleep_hours DECIMAL(3,1),
    sleep_quality INTEGER, -- 1-5 scale
    stress_level INTEGER, -- 1-5 scale
    energy_level INTEGER, -- 1-5 scale
    nutrition_timing VARCHAR(20), -- fasted, 1h_post_meal, etc.
    
    -- Supplements
    caffeine_mg INTEGER,
    other_supplements TEXT[],
    
    -- Time context
    time_of_day TIME,
    days_since_last_workout INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Exercise performance within a session
CREATE TABLE exercise_performances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_session_id UUID NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    workout_block_exercise_id UUID NOT NULL REFERENCES workout_block_exercises(id) ON DELETE CASCADE,
    
    performance_order INTEGER NOT NULL,
    
    -- Overall exercise performance
    planned_sets INTEGER,
    completed_sets INTEGER,
    total_volume_kg DECIMAL(8,2),
    total_reps INTEGER,
    average_rpe DECIMAL(3,1),
    
    -- Timing
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    total_rest_seconds INTEGER,
    
    -- Performance notes
    performance_notes TEXT,
    technique_quality INTEGER, -- 1-5 scale
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Individual set execution (The Core Data)
CREATE TABLE set_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exercise_performance_id UUID NOT NULL REFERENCES exercise_performances(id) ON DELETE CASCADE,
    set_protocol_id UUID REFERENCES set_protocols(id), -- NULL for basic sets
    
    set_number INTEGER NOT NULL,
    set_type set_type_enum NOT NULL DEFAULT 'working',
    
    -- Basic metrics
    weight_kg DECIMAL(6,2),
    reps_completed INTEGER,
    reps_attempted INTEGER, -- for failed reps
    
    -- Advanced metrics (Pro features)
    rpe_value DECIMAL(3,1),
    rpe_scale rpe_scale_enum DEFAULT 'rpe_10',
    rom_quality rom_quality_enum DEFAULT 'full',
    
    -- Tempo tracking
    eccentric_seconds DECIMAL(4,2),
    pause_seconds DECIMAL(4,2),
    concentric_seconds DECIMAL(4,2),
    
    -- Biomechanical data (Pro features)
    partial_reps INTEGER DEFAULT 0,
    assisted_reps INTEGER DEFAULT 0,
    range_of_motion_degrees INTEGER, -- Measured ROM
    
    -- Set-specific context
    rest_before_seconds INTEGER,
    rest_after_seconds INTEGER,
    equipment_modifications JSONB,
    
    -- Performance quality
    technique_breakdown_rep INTEGER, -- Rep where technique deteriorated
    pain_level INTEGER, -- 0-10 scale
    
    -- Timing
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    
    -- Notes
    set_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===================================================================
-- PERFORMANCE ANALYTICS (LLM-Ready)
-- ===================================================================

-- Pre-calculated volume metrics
CREATE TABLE volume_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    calculation_date DATE NOT NULL,
    period_type VARCHAR(10) NOT NULL, -- daily, weekly, monthly
    
    -- Volume calculations
    total_volume_kg DECIMAL(10,2),
    total_sets INTEGER,
    total_reps INTEGER,
    average_intensity DECIMAL(5,2), -- Average RPE or %1RM
    
    -- Muscle group breakdown
    volume_by_muscle_group JSONB,
    
    -- Movement pattern breakdown  
    volume_by_movement JSONB,
    
    -- Training density
    volume_per_hour DECIMAL(8,2),
    sets_per_hour DECIMAL(6,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, calculation_date, period_type)
);

-- Strength progression tracking
CREATE TABLE strength_progressions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    
    measurement_date DATE NOT NULL,
    
    -- Strength estimates
    estimated_1rm_kg DECIMAL(6,2),
    estimation_method VARCHAR(20), -- epley, brzycki, measured
    confidence_score DECIMAL(3,2), -- 0-1 confidence in estimate
    
    -- Supporting data
    base_weight_kg DECIMAL(6,2),
    base_reps INTEGER,
    base_rpe DECIMAL(3,1),
    
    -- Progression metrics
    volume_pr BOOLEAN DEFAULT false,
    weight_pr BOOLEAN DEFAULT false,
    reps_pr BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, exercise_id, measurement_date)
);

-- LLM insight data points
CREATE TABLE insight_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    data_type VARCHAR(50) NOT NULL,
    measurement_date DATE NOT NULL,
    
    -- Flexible data storage
    numeric_value DECIMAL(10,4),
    text_value TEXT,
    json_value JSONB,
    
    -- Context
    source_table VARCHAR(50), -- Which table generated this data
    source_id UUID, -- ID of source record
    
    -- Metadata
    confidence_score DECIMAL(3,2),
    calculation_method VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated insights from LLM
CREATE TABLE user_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    insight_type VARCHAR(50) NOT NULL,
    insight_category VARCHAR(30), -- progress, plateau, form, recovery
    
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    
    -- Action recommendations
    recommendations JSONB,
    
    -- Supporting data
    supporting_data_ids UUID[],
    chart_data JSONB,
    
    -- Status
    is_read BOOLEAN DEFAULT false,
    is_dismissed BOOLEAN DEFAULT false,
    user_feedback INTEGER, -- 1-5 usefulness rating
    
    -- Timing
    valid_until DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===================================================================
-- SUBSCRIPTION & FEATURE LIMITS
-- ===================================================================

-- Feature usage tracking
CREATE TABLE feature_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    feature_name VARCHAR(50) NOT NULL,
    usage_date DATE NOT NULL,
    usage_count INTEGER DEFAULT 1,
    
    -- Limit tracking
    daily_limit INTEGER,
    monthly_limit INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, feature_name, usage_date)
);

-- ===================================================================
-- INDEXES FOR PERFORMANCE
-- ===================================================================

-- Core performance indexes
CREATE INDEX idx_set_executions_performance ON set_executions(exercise_performance_id, set_number);
CREATE INDEX idx_exercise_performances_session ON exercise_performances(workout_session_id, performance_order);
CREATE INDEX idx_workout_sessions_user_date ON workout_sessions(user_id, start_time);

-- Analytics indexes
CREATE INDEX idx_volume_analytics_user_period ON volume_analytics(user_id, period_type, calculation_date);
CREATE INDEX idx_strength_progressions_user_exercise ON strength_progressions(user_id, exercise_id, measurement_date);
CREATE INDEX idx_insight_data_points_user_type_date ON insight_data_points(user_id, data_type, measurement_date);

-- Feature limit indexes
CREATE INDEX idx_feature_usage_user_feature_date ON feature_usage(user_id, feature_name, usage_date);

-- ===================================================================
-- VIEWS FOR COMMON QUERIES
-- ===================================================================

-- Latest strength estimates per exercise
CREATE VIEW latest_strength_estimates AS
SELECT DISTINCT ON (user_id, exercise_id)
    user_id,
    exercise_id,
    estimated_1rm_kg,
    measurement_date,
    confidence_score
FROM strength_progressions
ORDER BY user_id, exercise_id, measurement_date DESC;

-- Weekly training volume summary
CREATE VIEW weekly_volume_summary AS
SELECT 
    user_id,
    DATE_TRUNC('week', calculation_date) as week_start,
    SUM(total_volume_kg) as weekly_volume,
    SUM(total_sets) as weekly_sets,
    AVG(average_intensity) as avg_weekly_intensity
FROM volume_analytics 
WHERE period_type = 'daily'
GROUP BY user_id, DATE_TRUNC('week', calculation_date);
