# Subscription Tiers & Feature Limits

## 🎯 Subscription Tiers Overview

### 🆓 **Free Tier** - $0/month
**Target**: Casual fitness enthusiasts, trial users

**Limits:**
- 5 custom exercises maximum
- 10 workout templates maximum  
- Basic set logging only (weight, reps)
- 30-day data retention
- Standard exercise catalog access
- Basic progress charts
- 100 API requests/hour

**Features:**
- ✅ Basic workout logging
- ✅ Exercise catalog access
- ✅ Simple progress tracking
- ✅ Basic workout templates
- ❌ No RPE tracking
- ❌ No range of motion tracking
- ❌ No advanced set types
- ❌ No insights/analytics
- ❌ No biomechanics data

### 💪 **Plus Tier** - $9.99/month
**Target**: Serious fitness enthusiasts, regular gym-goers

**Limits:**
- Unlimited custom exercises
- Unlimited workout templates
- 1-year data retention
- 1,000 API requests/hour
- 5 concurrent devices
- Basic insights (weekly summaries)

**Features:**
- ✅ All Free features
- ✅ RPE tracking (1-10 scale)
- ✅ Range of motion quality tracking
- ✅ Advanced set types (supersets, dropsets)
- ✅ Tempo tracking
- ✅ Rest period optimization
- ✅ Volume progression tracking
- ✅ Strength progression estimates
- ✅ Weekly/monthly analytics
- ✅ Export workout data
- ✅ Exercise variation suggestions
- ❌ No full biomechanics tracking
- ❌ No LLM-powered insights
- ❌ No research participation

### 🏆 **Pro Tier** - $24.99/month
**Target**: Athletes, coaches, fitness professionals, research participants

**Limits:**
- Unlimited everything
- Permanent data retention
- 5,000 API requests/hour
- 10 concurrent devices
- Priority support

**Features:**
- ✅ All Plus features
- ✅ Full biomechanics tracking
- ✅ Advanced RPE scales (1-20, %1RM)
- ✅ Measured ROM in degrees
- ✅ Technique quality scoring
- ✅ Environmental context tracking
- ✅ Recovery metrics correlation
- ✅ LLM-powered insights & recommendations
- ✅ Plateau detection & solutions
- ✅ Advanced analytics dashboard
- ✅ Research data contribution
- ✅ API access for third-party apps
- ✅ Coach/trainer sharing features
- ✅ Custom insight requests

## 🔒 Feature Implementation Strategy

### Feature Gates in Code
```python
class FeatureGate:
    @staticmethod
    def check_feature_access(user: User, feature: str) -> bool:
        subscription = user.active_subscription
        plan_features = PLAN_FEATURES[subscription.plan.type]
        return plan_features.get(feature, False)
    
    @staticmethod  
    def check_usage_limit(user: User, feature: str) -> bool:
        # Check daily/monthly limits
        usage = get_feature_usage(user.id, feature, today())
        limit = get_feature_limit(user.subscription.plan.type, feature)
        return usage.usage_count < limit
```

### Database-Enforced Limits
```sql
-- Feature usage tracking with automatic limit enforcement
CREATE OR REPLACE FUNCTION check_feature_limit()
RETURNS TRIGGER AS $$
DECLARE
    current_usage INTEGER;
    user_plan_type VARCHAR;
    feature_limit INTEGER;
BEGIN
    -- Get user's plan type
    SELECT p.type INTO user_plan_type 
    FROM subscriptions s 
    JOIN plans p ON s.plan_id = p.id 
    WHERE s.user_id = NEW.user_id AND s.is_active = true;
    
    -- Get current usage count for today
    SELECT COALESCE(usage_count, 0) INTO current_usage
    FROM feature_usage 
    WHERE user_id = NEW.user_id 
      AND feature_name = NEW.feature_name 
      AND usage_date = CURRENT_DATE;
    
    -- Get limit for this plan
    feature_limit := get_plan_feature_limit(user_plan_type, NEW.feature_name);
    
    -- Enforce limit
    IF current_usage >= feature_limit THEN
        RAISE EXCEPTION 'Feature limit exceeded for plan %', user_plan_type;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## 📊 Feature Limit Examples

### Custom Exercises
- **Free**: 5 maximum
- **Plus**: Unlimited
- **Pro**: Unlimited + advanced biomechanics

### Data Retention  
- **Free**: 30 days (auto-delete older data)
- **Plus**: 1 year
- **Pro**: Permanent

### Set Tracking Complexity
- **Free**: Basic (weight, reps, rest)
- **Plus**: + RPE, ROM quality, tempo
- **Pro**: + measured ROM, technique scores, biomechanics

### Analytics & Insights
- **Free**: None
- **Plus**: Weekly/monthly summaries, basic trends
- **Pro**: LLM insights, plateau detection, personalized recommendations

## 🎯 Progressive Feature Unlocking

### Onboarding Flow
1. **Free Trial**: 7-day Pro trial for all new users
2. **Feature Discovery**: Show locked features with upgrade prompts
3. **Usage-Based Upgrades**: Suggest upgrades when hitting limits
4. **Value Demonstration**: Show what insights they'd get with more data

### Upgrade Incentives
- **Data Richness**: "Unlock advanced tracking to get better insights"
- **Plateau Breaking**: "Pro users see 23% faster strength gains"
- **Injury Prevention**: "Advanced biomechanics tracking reduces injury risk"
- **Time Efficiency**: "AI-powered insights save 2 hours of workout planning per week"

## 🔧 Technical Implementation

### Feature Flag System
```python
PLAN_FEATURES = {
    "free": {
        "custom_exercises_limit": 5,
        "workout_templates_limit": 10,
        "data_retention_days": 30,
        "track_rpe": False,
        "track_rom": False,
        "track_tempo": False,
        "advanced_set_types": False,
        "insights_enabled": False,
        "api_rate_limit": 100,
    },
    "plus": {
        "custom_exercises_limit": -1,  # unlimited
        "workout_templates_limit": -1,
        "data_retention_days": 365,
        "track_rpe": True,
        "track_rom": True,
        "track_tempo": True,
        "advanced_set_types": True,
        "insights_enabled": "basic",
        "api_rate_limit": 1000,
    },
    "pro": {
        # All unlimited
        "custom_exercises_limit": -1,
        "workout_templates_limit": -1,
        "data_retention_days": -1,  # permanent
        "track_rpe": "advanced",
        "track_rom": "measured",
        "track_tempo": True,
        "track_biomechanics": True,
        "advanced_set_types": True,
        "insights_enabled": "llm_powered",
        "research_participation": True,
        "api_rate_limit": 5000,
    }
}
```

### Automatic Data Cleanup
```sql
-- Scheduled job for free tier data retention
CREATE OR REPLACE FUNCTION cleanup_expired_data()
RETURNS void AS $$
BEGIN
    -- Delete old workout sessions for free users
    DELETE FROM workout_sessions ws
    USING subscriptions s, plans p
    WHERE ws.user_id = s.user_id
      AND s.plan_id = p.id
      AND p.type = 'free'
      AND ws.created_at < NOW() - INTERVAL '30 days';
      
    -- Similar cleanup for other tables...
END;
$$ LANGUAGE plpgsql;
```

This creates a clear value hierarchy that encourages upgrades while providing meaningful value at each tier.
