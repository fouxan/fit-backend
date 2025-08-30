# Fitness Tracker Database Schema Design

## Overview
This document outlines the comprehensive database schema for a science-based fitness tracking application with LLM-ready insights data.

## Core Entities

### 1. User Management
- **users**: Core user profile with biometric data
- **user_profiles**: Extended profile for science-based recommendations
- **user_preferences**: Training preferences, notification settings

### 2. Exercise System
- **exercise_catalog**: Master exercise database
- **exercise_variations**: Exercise modifications and progressions  
- **exercise_biomechanics**: Muscle activation patterns, joint angles
- **custom_exercises**: User-created exercises
- **exercise_tags**: Flexible tagging system

### 3. Workout Structure
- **workouts**: Workout templates
- **workout_blocks**: Grouping exercises (supersets, circuits)
- **workout_exercises**: Individual exercises in workouts
- **advanced_set_schemas**: Complex set structures (dropsets, clusters)

### 4. Execution & Tracking
- **workout_sessions**: Individual workout performances
- **exercise_performances**: Per-exercise session data
- **set_executions**: Individual set data with full metrics
- **session_context**: Environmental factors, equipment used

### 5. Performance Analytics
- **volume_calculations**: Weekly/monthly volume tracking
- **strength_progressions**: 1RM estimates and strength curves
- **performance_metrics**: Aggregated performance data
- **recovery_metrics**: Sleep, HRV, subjective recovery

### 6. LLM Integration
- **insight_data_points**: Structured data for AI analysis
- **user_insights**: Generated insights and recommendations
- **pattern_analysis**: Identified training patterns

## Data Points for LLM Analysis

### Workout Quality Metrics
- Volume (sets × reps × weight)
- Intensity (RPE, %1RM)
- Density (volume/time)
- Range of Motion quality
- Tempo adherence
- Rest period compliance

### Recovery & Adaptation
- Session RPE vs planned
- DOMS progression
- Sleep quality correlation
- Performance variance
- Fatigue accumulation

### Biomechanical Data
- Muscle activation patterns
- Movement quality scores
- Joint angle measurements
- Force production curves
- Power output metrics

### Progressive Overload
- Volume progression rates
- Intensity progression
- Frequency adaptations
- Exercise selection changes
- Plateau identification

## Subscription Feature Gates

### Free Tier
- 5 custom exercises max
- Basic workout logging
- Simple progress charts
- 30-day data retention

### Plus Tier  
- Unlimited custom exercises
- Advanced set types
- RPE & ROM tracking
- 1-year data retention
- Basic insights

### Pro Tier
- All Plus features
- Full biomechanics tracking
- Advanced analytics
- LLM-powered insights
- Unlimited data retention
- Research participation
