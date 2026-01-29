"""
Security utilities for authentication and authorization.
Password hashing, token generation, and RBAC checks.
"""

import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

import sys
sys.path.append(os.path.dirname(__file__))

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
BCRYPT_ROUNDS = 12


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password (bytes decoded to str)
    """
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        password: Plain text password to check
        password_hash: Stored hash to compare against
        
    Returns:
        True if password matches hash
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


# ============================================================================
# JWT TOKEN GENERATION & VALIDATION
# ============================================================================

def generate_token(user_id: str, email: str, role: str, expires_in_hours: int = JWT_EXPIRATION_HOURS) -> str:
    """
    Generate a JWT token for authenticated user.
    
    Args:
        user_id: UUID of the user
        email: User's email
        role: User's role (student/teacher/admin)
        expires_in_hours: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    payload = {
        "user_id": str(user_id),
        "email": email,
        "role": role,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=expires_in_hours)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded payload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token


def extract_token_from_header(auth_header: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.
    Expected format: "Bearer <token>"
    
    Args:
        auth_header: Authorization header value
        
    Returns:
        Token string or None
    """
    if not auth_header or not isinstance(auth_header, str):
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


# ============================================================================
# REFRESH TOKEN (for extended sessions)
# ============================================================================

def generate_refresh_token(user_id: str, expires_in_days: int = 7) -> str:
    """
    Generate a refresh token (longer expiration).
    
    Args:
        user_id: UUID of the user
        expires_in_days: Refresh token expiration time
        
    Returns:
        Encoded refresh token
    """
    payload = {
        "user_id": str(user_id),
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=expires_in_days),
        "type": "refresh"
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


# ============================================================================
# ROLE-BASED ACCESS CONTROL
# ============================================================================

ROLE_PERMISSIONS = {
    "student": {
        "view_own_profile": True,
        "view_own_exams": True,
        "view_own_attempts": True,
        "view_own_integrity_score": True,
        "view_other_student_data": False,
        "create_exam": False,
        "view_all_exams": False,
        "manage_students": False,
    },
    "teacher": {
        "view_own_profile": True,
        "view_own_exams": True,
        "view_own_attempts": False,
        "create_exam": True,
        "view_assigned_exams": True,
        "view_student_attempts": True,
        "view_student_integrity": True,
        "view_behavior_analysis": True,
        "manage_students": True,
        "export_analytics": True,
    },
    "admin": {
        "view_all_data": True,
        "manage_users": True,
        "manage_exams": True,
        "manage_permissions": True,
        "export_all": True,
    }
}


def has_permission(role: str, permission: str) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        role: User's role
        permission: Permission to check
        
    Returns:
        True if role has permission
    """
    permissions = ROLE_PERMISSIONS.get(role, {})
    return permissions.get(permission, False)


def can_access_exam(user_role: str, user_id: str, exam_id: str, db_session) -> bool:
    """
    Check if user can access a specific exam.
    
    Args:
        user_role: User's role
        user_id: User's UUID
        exam_id: Exam's UUID
        db_session: Database session
        
    Returns:
        True if user can access exam
    """
    if user_role == "admin":
        return True
    
    if user_role == "student":
        # Students can only see attempts for exams they've attempted
        from sqlalchemy import and_
        from orm_models import ExamAttempt
        
        attempt = db_session.query(ExamAttempt).filter(
            and_(
                ExamAttempt.exam_id == exam_id,
                ExamAttempt.student_id == user_id
            )
        ).first()
        return attempt is not None
    
    if user_role == "teacher":
        # Teachers can only see exams they created or are authorized for
        from sqlalchemy import or_, and_
        from orm_models import Exam, TeacherProfile, TeacherExamPermission
        
        teacher_profile = db_session.query(TeacherProfile).filter(
            TeacherProfile.user_id == user_id
        ).first()
        
        if not teacher_profile:
            return False
        
        permission = db_session.query(TeacherExamPermission).filter(
            and_(
                TeacherExamPermission.teacher_id == teacher_profile.id,
                TeacherExamPermission.exam_id == exam_id,
                TeacherExamPermission.can_view == True
            )
        ).first()
        
        return permission is not None
    
    return False


def can_access_student_data(accessor_role: str, accessor_id: str, target_student_id: str, db_session) -> bool:
    """
    Check if user can access another student's data.
    
    Args:
        accessor_role: Role of the user trying to access
        accessor_id: UUID of the user trying to access
        target_student_id: UUID of the student's data being accessed
        db_session: Database session
        
    Returns:
        True if access is allowed
    """
    if accessor_role == "admin":
        return True
    
    if accessor_role == "student":
        # Students can only view their own data
        return str(accessor_id) == str(target_student_id)
    
    if accessor_role == "teacher":
        # Teachers can view students for exams they manage
        from sqlalchemy import and_
        from orm_models import TeacherProfile, TeacherExamPermission, ExamAttempt
        
        teacher_profile = db_session.query(TeacherProfile).filter(
            TeacherProfile.user_id == accessor_id
        ).first()
        
        if not teacher_profile:
            return False
        
        # Check if teacher has view permission for any exam this student has attempted
        has_access = db_session.query(
            ExamAttempt
        ).join(
            TeacherExamPermission, ExamAttempt.exam_id == TeacherExamPermission.exam_id
        ).filter(
            and_(
                ExamAttempt.student_id == target_student_id,
                TeacherExamPermission.teacher_id == teacher_profile.id,
                TeacherExamPermission.can_view == True
            )
        ).first()
        
        return has_access is not None
    
    return False


# ============================================================================
# TOKEN REVOCATION (Blacklist)
# ============================================================================

# In production, use Redis for token blacklist
_token_blacklist = set()


def revoke_token(token: str):
    """Add token to blacklist (logout)."""
    _token_blacklist.add(token)


def is_token_revoked(token: str) -> bool:
    """Check if token has been revoked."""
    return token in _token_blacklist


def clear_revoked_tokens():
    """Clear blacklist (call periodically to prevent memory bloat)."""
    global _token_blacklist
    _token_blacklist.clear()
