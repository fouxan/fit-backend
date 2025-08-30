# Current Schema Analysis & Issues

## 🔍 Current Tables Overview

### ✅ Well-Designed Tables
1. **users** (16 fields)
   - Good: UUID primary keys, timestamps, basic biometrics
   - Issues: Missing training experience level, injury history

2. **exercise_catalog** (22 fields) 
   - Good: Comprehensive exercise metadata
   - Issues: Overly complex, missing biomechanics data

3. **plans/subscriptions** (9/11 fields)
   - Good: Stripe integration, basic subscription model
   - Issues: No feature limit enforcement in schema

### 🚨 Problematic Areas

#### **workout_exercises** (12 fields)
**MAJOR ISSUES:**
- `sets` field assumes all sets are identical 
- No support for supersets, dropsets, clusters
- `rep_scheme` JSONB is unclear and not queryable
- Missing RPE, range of motion, tempo tracking
- No rest period tracking between sets

#### **exercise_sets** (11 fields) 
**MAJOR ISSUES:**
- Too simplistic for science-based tracking
- Missing: partial reps, cluster tracking, tempo phases
- No biomechanical data (ROM, muscle activation)
- Limited RPE tracking (1-10 only)
- No equipment variation tracking

#### **workout_sessions** (13 fields)
**ISSUES:**
- Missing environmental context
- No detailed performance metrics
- Oversimplified mood/difficulty ratings
- No recovery data correlation

## 🎯 Missing Critical Components

### For Science-Based Training
1. **Biomechanics Tracking**
   - Range of motion measurements
   - Tempo phase tracking (eccentric/concentric)
   - Muscle activation patterns
   - Joint angle data

2. **Advanced Set Types**
   - Supersets/Giant sets
   - Dropsets with weight reductions
   - Cluster sets with intra-set rest
   - Rest-pause sets
   - Mechanical advantage sets

3. **Performance Context**
   - Equipment variations (barbell vs dumbbell)
   - Grip width, stance width
   - Pre-fatigue status
   - Time of day effects

### For LLM Insights
1. **Aggregated Metrics**
   - Weekly volume progression
   - Intensity distribution
   - Recovery adaptation rates
   - Plateau identification markers

2. **Contextual Data**
   - Sleep quality correlation
   - Nutrition timing effects
   - Stress level impacts
   - Training environment factors

## 📊 Recommended Schema Changes

### Phase 1: Core Exercise & Set Redesign
1. **Redesign workout execution model**
2. **Add advanced set type support**
3. **Implement comprehensive metrics tracking**

### Phase 2: Biomechanics & Science
1. **Add biomechanical data tables**
2. **Implement tempo and ROM tracking**
3. **Add equipment variation support**

### Phase 3: Analytics & LLM Integration
1. **Create aggregation tables**
2. **Add performance calculation views**
3. **Implement insight data collection**

### Phase 4: Advanced Features
1. **Add recovery tracking**
2. **Implement plateau detection**
3. **Add research data collection**

## 🔥 Priority Issues to Fix

1. **CRITICAL**: workout_exercises table design is fundamentally flawed
2. **HIGH**: Missing RPE, ROM, tempo tracking
3. **HIGH**: No support for complex set structures
4. **MEDIUM**: Inconsistent timestamp handling
5. **MEDIUM**: Missing aggregation tables for insights

## Next Steps
1. Design new exercise execution schema
2. Create migration strategy
3. Implement advanced set type support
4. Add science-based metric tracking
