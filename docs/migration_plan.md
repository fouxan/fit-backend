# Database Migration Plan: Current → Science-Based Schema

## 🎯 Migration Strategy Overview

### Philosophy
- **Zero Downtime**: Each migration should be backward compatible
- **Data Preservation**: No existing data should be lost
- **Feature Flags**: New features hidden behind subscription gates
- **Incremental**: Small, focused migrations for easier rollback
- **Testing**: Each migration thoroughly tested before production

## 📋 Migration Phases

### **Phase 1: Foundation & Cleanup** (Weeks 1-2)
**Goal**: Fix current schema issues and prepare for advanced features

#### **Migration 1.1**: Fix Core Issues
```sql
-- Fix timestamp consistency
ALTER TABLE plans ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE plans ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE subscriptions ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
-- ... fix all timestamp inconsistencies

-- Add missing constraints
ALTER TABLE users ADD CONSTRAINT users_email_check CHECK (email ~* '^.+@.+\..+$');
ALTER TABLE users ADD CONSTRAINT users_training_frequency_check CHECK (training_frequency BETWEEN 1 AND 14);
```

#### **Migration 1.2**: Enhance User Profile
```sql
-- Add training context to users table
ALTER TABLE users ADD COLUMN training_experience VARCHAR(20);
ALTER TABLE users ADD COLUMN primary_goals TEXT[];
ALTER TABLE users ADD COLUMN injury_history JSONB;
ALTER TABLE users ADD COLUMN training_frequency INTEGER;

-- Create user preferences table
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    preferred_units VARCHAR(10) DEFAULT 'metric',
    default_rest_seconds INTEGER DEFAULT 120,
    track_rpe BOOLEAN DEFAULT true,
    track_rom BOOLEAN DEFAULT false,
    track_tempo BOOLEAN DEFAULT false,
    workout_reminders BOOLEAN DEFAULT true,
    progress_updates BOOLEAN DEFAULT true,
    insight_notifications BOOLEAN DEFAULT true,
    share_workouts BOOLEAN DEFAULT false,
    research_participation BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Migration 1.3**: Feature Usage Tracking
```sql
-- Create feature usage tracking for subscription limits
CREATE TABLE feature_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feature_name VARCHAR(50) NOT NULL,
    usage_date DATE NOT NULL,
    usage_count INTEGER DEFAULT 1,
    daily_limit INTEGER,
    monthly_limit INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, feature_name, usage_date)
);

CREATE INDEX idx_feature_usage_user_feature_date ON feature_usage(user_id, feature_name, usage_date);
```

---

### **Phase 2: Exercise System Enhancement** (Weeks 3-4)
**Goal**: Add biomechanics and scientific exercise data

#### **Migration 2.1**: Exercise Biomechanics
```sql
-- Add biomechanics data for exercises
CREATE TABLE exercise_biomechanics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exercise_id UUID NOT NULL REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    primary_muscles JSONB,
    secondary_muscles JSONB,
    stabilizer_muscles JSONB,
    joints_involved TEXT[],
    movement_plane VARCHAR(20),
    optimal_rom_degrees INTEGER,
    joint_angles JSONB,
    force_curve_type VARCHAR(20),
    recommended_eccentric_seconds DECIMAL(3,1),
    recommended_pause_seconds DECIMAL(3,1),
    recommended_concentric_seconds DECIMAL(3,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Migration 2.2**: Exercise Variations System
```sql
-- Exercise variations and progressions
CREATE TABLE exercise_variations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_exercise_id UUID REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    variation_exercise_id UUID REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    variation_type VARCHAR(20),
    difficulty_modifier DECIMAL(3,2),
    variation_factors JSONB,
    UNIQUE(parent_exercise_id, variation_exercise_id)
);
```

---

### **Phase 3: Workout Structure Redesign** (Weeks 5-7)
**Goal**: Replace current workout system with advanced set support

#### **Migration 3.1**: Create New Enums
```sql
-- Create enums for advanced workout features
CREATE TYPE set_type_enum AS ENUM (
    'working', 'warmup', 'dropset', 'superset', 'cluster', 
    'rest_pause', 'mechanical_drop', 'amrap', 'tempo', 
    'isometric', 'partial', 'assisted', 'negative'
);

CREATE TYPE workout_block_type_enum AS ENUM (
    'straight_sets', 'superset', 'giant_set', 'circuit', 
    'emom', 'ladder', 'complex'
);

CREATE TYPE rpe_scale_enum AS ENUM ('rpe_10', 'rpe_20', 'percentage');
CREATE TYPE rom_quality_enum AS ENUM (
    'full', 'three_quarter', 'half', 'quarter', 
    'partial_top', 'partial_bottom', 'variable'
);
```

#### **Migration 3.2**: Workout Blocks System
```sql
-- Create workout blocks for organizing exercises
CREATE TABLE workout_blocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_id UUID NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    block_order INTEGER NOT NULL,
    block_name VARCHAR(100),
    block_type workout_block_type_enum NOT NULL DEFAULT 'straight_sets',
    rest_between_exercises INTEGER,
    rounds INTEGER DEFAULT 1,
    round_rest_seconds INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Migration script to convert existing workouts
INSERT INTO workout_blocks (workout_id, block_order, block_name, block_type)
SELECT id, 1, 'Main Block', 'straight_sets' FROM workouts;
```

#### **Migration 3.3**: New Exercise Structure
```sql
-- Replace workout_exercises with workout_block_exercises
CREATE TABLE workout_block_exercises (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_block_id UUID NOT NULL REFERENCES workout_blocks(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    exercise_order INTEGER NOT NULL,
    target_sets INTEGER,
    target_reps_min INTEGER,
    target_reps_max INTEGER,
    target_weight_kg DECIMAL(6,2),
    target_rpe DECIMAL(3,1),
    rest_after_seconds INTEGER,
    tempo_prescription VARCHAR(20),
    equipment_variant JSONB,
    notes TEXT
);

-- Migration script to transfer existing data
INSERT INTO workout_block_exercises (
    workout_block_id, exercise_id, exercise_order,
    target_sets, target_reps_min, target_reps_max
)
SELECT 
    wb.id, we.exercise_id, we.order,
    we.sets, we.reps, we.reps
FROM workout_exercises we
JOIN workout_blocks wb ON we.workout_id = wb.workout_id;
```

#### **Migration 3.4**: Advanced Set Protocols
```sql
-- Advanced set protocols for complex training
CREATE TABLE set_protocols (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_block_exercise_id UUID NOT NULL REFERENCES workout_block_exercises(id) ON DELETE CASCADE,
    protocol_type set_type_enum NOT NULL,
    set_order INTEGER NOT NULL,
    protocol_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

### **Phase 4: Execution Tracking Upgrade** (Weeks 8-10)
**Goal**: Replace basic set tracking with science-based execution data

#### **Migration 4.1**: Session Context
```sql
-- Environmental and contextual data for sessions
CREATE TABLE session_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_session_id UUID NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    gym_location VARCHAR(100),
    equipment_availability JSONB,
    crowd_level INTEGER,
    temperature_celsius INTEGER,
    sleep_hours DECIMAL(3,1),
    sleep_quality INTEGER,
    stress_level INTEGER,
    energy_level INTEGER,
    nutrition_timing VARCHAR(20),
    caffeine_mg INTEGER,
    other_supplements TEXT[],
    time_of_day TIME,
    days_since_last_workout INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Migration 4.2**: Exercise Performance Tracking
```sql
-- Per-exercise performance within sessions
CREATE TABLE exercise_performances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workout_session_id UUID NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    workout_block_exercise_id UUID NOT NULL REFERENCES workout_block_exercises(id) ON DELETE CASCADE,
    performance_order INTEGER NOT NULL,
    planned_sets INTEGER,
    completed_sets INTEGER,
    total_volume_kg DECIMAL(8,2),
    total_reps INTEGER,
    average_rpe DECIMAL(3,1),
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    total_rest_seconds INTEGER,
    performance_notes TEXT,
    technique_quality INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### **Migration 4.3**: Advanced Set Execution** 
```sql
-- Replace exercise_sets with comprehensive set_executions
CREATE TABLE set_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exercise_performance_id UUID NOT NULL REFERENCES exercise_performances(id) ON DELETE CASCADE,
    set_protocol_id UUID REFERENCES set_protocols(id),
    set_number INTEGER NOT NULL,
    set_type set_type_enum NOT NULL DEFAULT 'working',
    
    -- Basic metrics (all tiers)
    weight_kg DECIMAL(6,2),
    reps_completed INTEGER,
    reps_attempted INTEGER,
    
    -- Advanced metrics (Plus/Pro only)
    rpe_value DECIMAL(3,1),
    rpe_scale rpe_scale_enum DEFAULT 'rpe_10',
    rom_quality rom_quality_enum DEFAULT 'full',
    
    -- Pro-only features
    eccentric_seconds DECIMAL(4,2),
    pause_seconds DECIMAL(4,2),
    concentric_seconds DECIMAL(4,2),
    partial_reps INTEGER DEFAULT 0,
    assisted_reps INTEGER DEFAULT 0,
    range_of_motion_degrees INTEGER,
    
    -- Context
    rest_before_seconds INTEGER,
    rest_after_seconds INTEGER,
    equipment_modifications JSONB,
    technique_breakdown_rep INTEGER,
    pain_level INTEGER,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    set_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Migration script from old exercise_sets
INSERT INTO set_executions (
    exercise_performance_id, set_number, weight_kg, 
    reps_completed, rpe_value
)
SELECT 
    ep.id, es.set_number, es.weight, es.reps, es.rpe
FROM exercise_sets es
JOIN exercise_performances ep ON ... -- mapping logic
```

---

### **Phase 5: Analytics & LLM Integration** (Weeks 11-13)
**Goal**: Add performance analytics and LLM-ready data structures

#### **Migration 5.1**: Volume Analytics
```sql
-- Pre-calculated volume metrics for performance
CREATE TABLE volume_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    calculation_date DATE NOT NULL,
    period_type VARCHAR(10) NOT NULL,
    total_volume_kg DECIMAL(10,2),
    total_sets INTEGER,
    total_reps INTEGER,
    average_intensity DECIMAL(5,2),
    volume_by_muscle_group JSONB,
    volume_by_movement JSONB,
    volume_per_hour DECIMAL(8,2),
    sets_per_hour DECIMAL(6,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, calculation_date, period_type)
);
```

#### **Migration 5.2**: Strength Progressions
```sql
-- Strength progression tracking and 1RM estimates
CREATE TABLE strength_progressions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercise_catalog(id) ON DELETE CASCADE,
    measurement_date DATE NOT NULL,
    estimated_1rm_kg DECIMAL(6,2),
    estimation_method VARCHAR(20),
    confidence_score DECIMAL(3,2),
    base_weight_kg DECIMAL(6,2),
    base_reps INTEGER,
    base_rpe DECIMAL(3,1),
    volume_pr BOOLEAN DEFAULT false,
    weight_pr BOOLEAN DEFAULT false,
    reps_pr BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, exercise_id, measurement_date)
);
```

#### **Migration 5.3**: LLM Data & Insights
```sql
-- Structured data points for LLM analysis
CREATE TABLE insight_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    data_type VARCHAR(50) NOT NULL,
    measurement_date DATE NOT NULL,
    numeric_value DECIMAL(10,4),
    text_value TEXT,
    json_value JSONB,
    source_table VARCHAR(50),
    source_id UUID,
    confidence_score DECIMAL(3,2),
    calculation_method VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Generated insights from LLM
CREATE TABLE user_insights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    insight_type VARCHAR(50) NOT NULL,
    insight_category VARCHAR(30),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    recommendations JSONB,
    supporting_data_ids UUID[],
    chart_data JSONB,
    is_read BOOLEAN DEFAULT false,
    is_dismissed BOOLEAN DEFAULT false,
    user_feedback INTEGER,
    valid_until DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

### **Phase 6: Cleanup & Optimization** (Week 14)
**Goal**: Remove old tables and optimize performance

#### **Migration 6.1**: Create Performance Views
```sql
-- Optimized views for common queries
CREATE VIEW latest_strength_estimates AS
SELECT DISTINCT ON (user_id, exercise_id)
    user_id, exercise_id, estimated_1rm_kg, measurement_date, confidence_score
FROM strength_progressions
ORDER BY user_id, exercise_id, measurement_date DESC;

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
```

#### **Migration 6.2**: Add Performance Indexes
```sql
-- Optimize for common query patterns
CREATE INDEX idx_set_executions_performance ON set_executions(exercise_performance_id, set_number);
CREATE INDEX idx_exercise_performances_session ON exercise_performances(workout_session_id, performance_order);
CREATE INDEX idx_volume_analytics_user_period ON volume_analytics(user_id, period_type, calculation_date);
CREATE INDEX idx_strength_progressions_user_exercise ON strength_progressions(user_id, exercise_id, measurement_date);
CREATE INDEX idx_insight_data_points_user_type_date ON insight_data_points(user_id, data_type, measurement_date);
```

#### **Migration 6.3**: Deprecate Old Tables (Optional)**
```sql
-- After successful migration and testing, optionally remove old tables
-- This should be done carefully with full backups
-- DROP TABLE IF EXISTS workout_exercises CASCADE;
-- DROP TABLE IF EXISTS exercise_sets CASCADE;
-- (Only after confirming all data migrated successfully)
```

## 🔄 Data Migration Scripts

### Example Migration Script Template
```python
def migrate_workout_exercises_to_blocks():
    """
    Migrate existing workout_exercises to new workout_blocks structure
    """
    # 1. Create workout blocks for all existing workouts
    # 2. Migrate exercises to workout_block_exercises  
    # 3. Preserve all existing data
    # 4. Validate migration success
    # 5. Update application code to use new structure
```

## ✅ Migration Validation

### Pre-Migration Checklist
- [ ] Database backup completed
- [ ] Migration tested on staging environment
- [ ] Application feature flags configured
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured

### Post-Migration Validation
- [ ] All existing data preserved
- [ ] New features working correctly
- [ ] Performance benchmarks met
- [ ] User workflows unaffected
- [ ] Analytics data flowing correctly

This migration plan transforms your basic workout logging into a comprehensive, science-based fitness tracking system while preserving all existing data and maintaining backward compatibility.
