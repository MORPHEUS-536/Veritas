-- ============================================================================
-- VERITAS PLATFORM: PostgreSQL Schema
-- Production-grade RBAC, monitoring, and analytics system
-- ============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For full-text search on monitoring data

-- ============================================================================
-- CORE SCHEMA: USERS & AUTHENTICATION
-- ============================================================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    
    -- Account status
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_token VARCHAR(255),
    verification_token_expires_at TIMESTAMP,
    
    -- Authentication tracking
    last_login TIMESTAMP,
    last_login_ip VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    -- Metadata (JSONB for flexibility)
    metadata JSONB DEFAULT '{}' NOT NULL
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_email_role ON users(email, role);
CREATE INDEX idx_users_active_role ON users(is_active, role);
CREATE INDEX idx_users_created_at ON users(created_at);


CREATE TABLE student_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Academic info
    enrollment_id VARCHAR(50),
    cohort VARCHAR(100),
    
    -- Performance tracking (denormalized for fast queries)
    cumulative_integrity_score FLOAT DEFAULT 1.0 NOT NULL CHECK (cumulative_integrity_score >= 0 AND cumulative_integrity_score <= 1),
    cumulative_lmi FLOAT DEFAULT 0.0 NOT NULL CHECK (cumulative_lmi >= 0),
    total_exams_attempted INTEGER DEFAULT 0 NOT NULL,
    total_exams_passed INTEGER DEFAULT 0 NOT NULL,
    
    -- Risk assessment
    current_dropout_risk VARCHAR(50) DEFAULT 'safe' NOT NULL 
        CHECK (current_dropout_risk IN ('safe', 'incapable', 'copy', 'no_interest')),
    flagged_for_review BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_student_dropout_risk ON student_profiles(current_dropout_risk);
CREATE INDEX idx_student_flagged ON student_profiles(flagged_for_review);
CREATE INDEX idx_student_user_id ON student_profiles(user_id);


CREATE TABLE teacher_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Professional info
    department VARCHAR(100),
    subject_areas JSON DEFAULT '[]' NOT NULL,
    credentials VARCHAR(255),
    bio TEXT,
    
    -- Permissions & management
    can_create_exams BOOLEAN DEFAULT true NOT NULL,
    can_view_analytics BOOLEAN DEFAULT true NOT NULL,
    can_manage_students BOOLEAN DEFAULT false NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_teacher_user_id ON teacher_profiles(user_id);


-- ============================================================================
-- EXAM MANAGEMENT
-- ============================================================================

CREATE TABLE exams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    creator_id UUID NOT NULL REFERENCES users(id),
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    subject VARCHAR(100) NOT NULL,
    topic VARCHAR(100),
    
    -- Assessment parameters
    max_score FLOAT DEFAULT 100.0 NOT NULL CHECK (max_score > 0),
    duration_minutes INTEGER NOT NULL CHECK (duration_minutes > 0),
    passing_score FLOAT DEFAULT 60.0 NOT NULL CHECK (passing_score >= 0 AND passing_score <= max_score),
    
    -- Configuration
    is_published BOOLEAN DEFAULT false,
    enable_monitoring BOOLEAN DEFAULT true NOT NULL,
    enable_integrity_analysis BOOLEAN DEFAULT true NOT NULL,
    metadata JSONB DEFAULT '{}' NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_exam_creator_published ON exams(creator_id, is_published);
CREATE INDEX idx_exam_subject_topic ON exams(subject, topic);
CREATE INDEX idx_exam_is_published ON exams(is_published);
CREATE INDEX idx_exam_created_at ON exams(created_at);


CREATE TABLE teacher_exam_permissions (
    teacher_id UUID NOT NULL REFERENCES teacher_profiles(id) ON DELETE CASCADE,
    exam_id UUID NOT NULL REFERENCES exams(id) ON DELETE CASCADE,
    
    can_view BOOLEAN DEFAULT true NOT NULL,
    can_edit BOOLEAN DEFAULT true NOT NULL,
    can_view_analytics BOOLEAN DEFAULT true NOT NULL,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    PRIMARY KEY (teacher_id, exam_id)
);

CREATE INDEX idx_teacher_exams ON teacher_exam_permissions(teacher_id);
CREATE INDEX idx_exam_teachers ON teacher_exam_permissions(exam_id);


-- ============================================================================
-- EXAM ATTEMPTS & MONITORING
-- ============================================================================

CREATE TABLE exam_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_id UUID NOT NULL REFERENCES exams(id),
    student_id UUID NOT NULL REFERENCES users(id),
    
    -- Attempt status
    status VARCHAR(50) DEFAULT 'in_progress' NOT NULL 
        CHECK (status IN ('in_progress', 'completed', 'abandoned')),
    score FLOAT,
    max_score FLOAT NOT NULL CHECK (max_score > 0),
    percentage FLOAT CHECK (percentage >= 0 AND percentage <= 100),
    passed BOOLEAN,
    
    -- Integrity metrics (computed by analysis)
    integrity_score FLOAT DEFAULT 1.0 NOT NULL CHECK (integrity_score >= 0 AND integrity_score <= 1),
    lmi FLOAT DEFAULT 0.0 NOT NULL CHECK (lmi >= 0 AND lmi <= 100),
    dropout_label VARCHAR(50) DEFAULT 'safe' NOT NULL
        CHECK (dropout_label IN ('safe', 'incapable', 'copy', 'no_interest')),
    flagged BOOLEAN DEFAULT false,
    
    -- Timestamps
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds INTEGER CHECK (duration_seconds >= 0),
    
    -- Flexible storage
    submission_data JSONB DEFAULT '{}' NOT NULL,
    metadata JSONB DEFAULT '{}' NOT NULL
);

CREATE INDEX idx_attempt_exam_student ON exam_attempts(exam_id, student_id);
CREATE INDEX idx_attempt_student_status ON exam_attempts(student_id, status);
CREATE INDEX idx_attempt_dropout_risk ON exam_attempts(dropout_label);
CREATE INDEX idx_attempt_flagged ON exam_attempts(flagged);
CREATE INDEX idx_attempt_exam_status ON exam_attempts(exam_id, status);
CREATE INDEX idx_attempt_completed_at ON exam_attempts(completed_at);
CREATE CONSTRAINT ck_attempt_score_valid CHECK (score IS NULL OR (score >= 0 AND score <= max_score));


-- ============================================================================
-- REAL-TIME MONITORING EVENTS
-- ============================================================================

CREATE TABLE monitoring_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_attempt_id UUID NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id),
    
    -- Event classification
    event_type VARCHAR(100) NOT NULL,  -- eye_movement, window_focus, keystroke, etc.
    severity VARCHAR(50) DEFAULT 'normal' NOT NULL 
        CHECK (severity IN ('normal', 'warning', 'critical')),
    
    -- Event details
    description TEXT,
    data_payload JSONB NOT NULL,
    
    -- Analysis
    is_anomaly BOOLEAN DEFAULT false,
    anomaly_score FLOAT CHECK (anomaly_score IS NULL OR (anomaly_score >= 0 AND anomaly_score <= 1)),
    analysis_notes TEXT,
    
    -- Metadata
    client_timestamp TIMESTAMP,
    server_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_event_attempt ON monitoring_events(exam_attempt_id);
CREATE INDEX idx_event_student ON monitoring_events(student_id);
CREATE INDEX idx_event_type_severity ON monitoring_events(event_type, severity);
CREATE INDEX idx_event_is_anomaly ON monitoring_events(is_anomaly);
CREATE INDEX idx_event_server_timestamp ON monitoring_events(server_timestamp);
CREATE INDEX idx_event_severity ON monitoring_events(severity);

-- For high-volume queries: GIN index on JSONB payload
CREATE INDEX idx_event_payload ON monitoring_events USING GIN (data_payload);


-- ============================================================================
-- BEHAVIOR ANALYSIS & LLM OUTPUT
-- ============================================================================

CREATE TABLE behavior_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    exam_attempt_id UUID UNIQUE NOT NULL REFERENCES exam_attempts(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id),
    
    -- Aggregated metrics
    total_monitoring_events INTEGER DEFAULT 0 NOT NULL,
    anomaly_count INTEGER DEFAULT 0 NOT NULL,
    critical_events INTEGER DEFAULT 0 NOT NULL,
    
    -- Thinking quality & originality
    integrity_score FLOAT NOT NULL CHECK (integrity_score >= 0 AND integrity_score <= 1),
    originality_indicators JSON DEFAULT '[]' NOT NULL,
    
    -- Learning progress
    lmi_score FLOAT NOT NULL CHECK (lmi_score >= 0 AND lmi_score <= 100),
    improvement_trend VARCHAR(50),  -- improving, stagnant, declining
    
    -- Dropout classification
    dropout_label VARCHAR(50) NOT NULL 
        CHECK (dropout_label IN ('safe', 'incapable', 'copy', 'no_interest')),
    dropout_confidence FLOAT NOT NULL CHECK (dropout_confidence >= 0 AND dropout_confidence <= 1),
    
    -- LLM Analysis output
    llm_summary TEXT,
    llm_recommendations JSON DEFAULT '[]' NOT NULL,
    llm_model_version VARCHAR(50),
    
    -- Flags
    requires_instructor_attention BOOLEAN DEFAULT false,
    requires_recap BOOLEAN DEFAULT false NOT NULL,
    
    analysis_completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata JSONB DEFAULT '{}' NOT NULL
);

CREATE INDEX idx_behavior_attempt ON behavior_analysis(exam_attempt_id);
CREATE INDEX idx_behavior_student ON behavior_analysis(student_id);
CREATE INDEX idx_behavior_dropout ON behavior_analysis(dropout_label);
CREATE INDEX idx_behavior_flagged ON behavior_analysis(requires_instructor_attention);
CREATE INDEX idx_behavior_completed_at ON behavior_analysis(analysis_completed_at);


-- ============================================================================
-- PERFORMANCE METRICS (DENORMALIZED FOR ANALYTICS)
-- ============================================================================

CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID UNIQUE NOT NULL REFERENCES users(id),
    
    -- Cumulative scores
    total_attempts INTEGER DEFAULT 0 NOT NULL,
    total_passed INTEGER DEFAULT 0 NOT NULL,
    avg_score FLOAT,
    
    -- Subject performance
    strengths JSON DEFAULT '[]' NOT NULL,
    weaknesses JSON DEFAULT '[]' NOT NULL,
    subject_scores JSONB DEFAULT '{}' NOT NULL,
    
    -- Integrity
    avg_integrity_score FLOAT,
    integrity_trend VARCHAR(50),  -- improving, stable, declining
    
    -- Learning momentum
    avg_lmi FLOAT,
    lmi_trend VARCHAR(50),
    
    -- Overall risk
    current_risk_label VARCHAR(50) DEFAULT 'safe' NOT NULL 
        CHECK (current_risk_label IN ('safe', 'incapable', 'copy', 'no_interest')),
    flagged_for_intervention BOOLEAN DEFAULT false,
    
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    last_attempt_date TIMESTAMP
);

CREATE INDEX idx_perf_student_risk ON performance_metrics(student_id, current_risk_label);
CREATE INDEX idx_perf_flagged ON performance_metrics(flagged_for_intervention);
CREATE INDEX idx_perf_student_id ON performance_metrics(student_id);


-- ============================================================================
-- AUDIT & COMPLIANCE
-- ============================================================================

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,  -- login, view_student_data, modify_exam
    resource_type VARCHAR(100) NOT NULL,  -- user, exam_attempt, behavior_analysis
    resource_id VARCHAR(100),
    
    details JSONB DEFAULT '{}' NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX idx_audit_user_action ON audit_logs(user_id, action);
CREATE INDEX idx_audit_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at);


-- ============================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ============================================================================

-- Exam-level performance summary
CREATE MATERIALIZED VIEW exam_performance_summary AS
SELECT 
    e.id,
    e.title,
    e.subject,
    COUNT(DISTINCT ea.student_id) as unique_students,
    COUNT(ea.id) as total_attempts,
    AVG(ea.score) as avg_score,
    SUM(CASE WHEN ea.passed = true THEN 1 ELSE 0 END)::float / COUNT(ea.id) as pass_rate,
    AVG(ea.integrity_score) as avg_integrity,
    SUM(CASE WHEN ea.dropout_label IN ('copy', 'incapable') THEN 1 ELSE 0 END) as high_risk_count,
    MAX(ea.completed_at) as last_attempt
FROM exams e
LEFT JOIN exam_attempts ea ON e.id = ea.exam_id AND ea.status = 'completed'
GROUP BY e.id, e.title, e.subject;

CREATE INDEX idx_exam_perf_subject ON exam_performance_summary(subject);


-- Student risk summary
CREATE MATERIALIZED VIEW student_risk_summary AS
SELECT 
    sp.user_id,
    sp.current_dropout_risk,
    sp.cumulative_integrity_score,
    sp.cumulative_lmi,
    COUNT(DISTINCT ea.id) as attempt_count,
    SUM(CASE WHEN ea.flagged = true THEN 1 ELSE 0 END) as flagged_count,
    MAX(ea.completed_at) as last_attempt
FROM student_profiles sp
LEFT JOIN exam_attempts ea ON sp.user_id = ea.student_id
GROUP BY sp.user_id, sp.current_dropout_risk, sp.cumulative_integrity_score, sp.cumulative_lmi;

CREATE INDEX idx_student_risk ON student_risk_summary(current_dropout_risk);


-- ============================================================================
-- TRIGGERS & AUTOMATIC MAINTENANCE
-- ============================================================================

-- Auto-update users.updated_at
CREATE OR REPLACE FUNCTION update_users_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_update_timestamp
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_users_timestamp();


-- Auto-update student_profiles.updated_at
CREATE OR REPLACE FUNCTION update_student_profiles_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER student_profiles_update_timestamp
BEFORE UPDATE ON student_profiles
FOR EACH ROW
EXECUTE FUNCTION update_student_profiles_timestamp();


-- ============================================================================
-- MAINTENANCE & CLEANUP PROCEDURES
-- ============================================================================

-- Refresh materialized views
CREATE OR REPLACE PROCEDURE refresh_analytics_views()
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY exam_performance_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY student_risk_summary;
    RAISE NOTICE 'Analytics views refreshed at %', NOW();
END;
$$;

-- Archive old monitoring events (older than 90 days)
CREATE OR REPLACE PROCEDURE archive_old_monitoring_events()
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM monitoring_events
    WHERE server_timestamp < NOW() - INTERVAL '90 days';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RAISE NOTICE 'Archived % monitoring events', deleted_count;
END;
$$;


-- ============================================================================
-- PERFORMANCE TUNING: STATISTICS & ANALYZE
-- ============================================================================

ANALYZE users;
ANALYZE student_profiles;
ANALYZE exam_attempts;
ANALYZE monitoring_events;
ANALYZE behavior_analysis;
ANALYZE performance_metrics;

-- Enable autovacuum for high-turnover tables
ALTER TABLE monitoring_events SET (
    autovacuum_vacuum_scale_factor = 0.01,
    autovacuum_analyze_scale_factor = 0.005,
    autovacuum_vacuum_cost_delay = 10
);

ALTER TABLE exam_attempts SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
