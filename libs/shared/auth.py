"""
Shared Authentication Utilities
Centralized JWT token handling, user authentication, and security utilities
"""
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union
from passlib.context import CryptContext
from passlib.hash import bcrypt
from .config import get_security_config

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthUtils:
    """Authentication utilities class"""
    
    def __init__(self):
        self.config = get_security_config()
        self.secret_key = self.config["jwt_secret_key"]
        self.algorithm = self.config["jwt_algorithm"]
        self.expiration_hours = self.config["jwt_expiration_hours"]
    
    def create_access_token(self, user_id: str, email: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create JWT access token for user
        
        Args:
            user_id: User ID
            email: User email
            additional_claims: Additional claims to include in token
            
        Returns:
            JWT token string
        """
        try:
            # Base claims
            claims = {
                "user_id": user_id,
                "email": email,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=self.expiration_hours),
                "type": "access"
            }
            
            # Add additional claims if provided
            if additional_claims:
                claims.update(additional_claims)
            
            # Create token
            token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise ValueError(f"Failed to create access token: {e}")
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create JWT refresh token for user
        
        Args:
            user_id: User ID
            
        Returns:
            JWT refresh token string
        """
        try:
            claims = {
                "user_id": user_id,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=30),  # Refresh tokens last 30 days
                "type": "refresh"
            }
            
            token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise ValueError(f"Failed to create refresh token: {e}")
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            return None
    
    def get_user_id_from_token(self, token: str) -> Optional[str]:
        """
        Extract user ID from JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            User ID or None if token is invalid
        """
        payload = self.verify_token(token)
        if payload and "user_id" in payload:
            return payload["user_id"]
        return None
    
    def get_email_from_token(self, token: str) -> Optional[str]:
        """
        Extract email from JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Email or None if token is invalid
        """
        payload = self.verify_token(token)
        if payload and "email" in payload:
            return payload["email"]
        return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Check if token is expired
        
        Args:
            token: JWT token string
            
        Returns:
            True if expired, False otherwise
        """
        payload = self.verify_token(token)
        if not payload:
            return True
        
        exp = payload.get("exp")
        if not exp:
            return True
        
        return datetime.utcnow() > datetime.fromtimestamp(exp)
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against hash
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_password_reset_token(self, user_id: str) -> str:
        """
        Create password reset token
        
        Args:
            user_id: User ID
            
        Returns:
            Password reset token
        """
        try:
            claims = {
                "user_id": user_id,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(hours=1),  # Reset tokens expire in 1 hour
                "type": "password_reset"
            }
            
            token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise ValueError(f"Failed to create password reset token: {e}")
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """
        Verify password reset token and return user ID
        
        Args:
            token: Password reset token
            
        Returns:
            User ID or None if token is invalid
        """
        payload = self.verify_token(token)
        if payload and payload.get("type") == "password_reset":
            return payload.get("user_id")
        return None
    
    def create_email_verification_token(self, user_id: str, email: str) -> str:
        """
        Create email verification token
        
        Args:
            user_id: User ID
            email: Email to verify
            
        Returns:
            Email verification token
        """
        try:
            claims = {
                "user_id": user_id,
                "email": email,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=7),  # Verification tokens expire in 7 days
                "type": "email_verification"
            }
            
            token = jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
            return token
            
        except Exception as e:
            raise ValueError(f"Failed to create email verification token: {e}")
    
    def verify_email_verification_token(self, token: str) -> Optional[Dict[str, str]]:
        """
        Verify email verification token
        
        Args:
            token: Email verification token
            
        Returns:
            Dict with user_id and email or None if invalid
        """
        payload = self.verify_token(token)
        if payload and payload.get("type") == "email_verification":
            return {
                "user_id": payload.get("user_id"),
                "email": payload.get("email")
            }
        return None

# Global auth utilities instance
auth_utils = AuthUtils()

# Convenience functions
def create_access_token(user_id: str, email: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
    """Create JWT access token"""
    return auth_utils.create_access_token(user_id, email, additional_claims)

def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    return auth_utils.create_refresh_token(user_id)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token"""
    return auth_utils.verify_token(token)

def get_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token"""
    return auth_utils.get_user_id_from_token(token)

def get_email_from_token(token: str) -> Optional[str]:
    """Extract email from JWT token"""
    return auth_utils.get_email_from_token(token)

def is_token_expired(token: str) -> bool:
    """Check if token is expired"""
    return auth_utils.is_token_expired(token)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return auth_utils.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return auth_utils.verify_password(plain_password, hashed_password)

def create_password_reset_token(user_id: str) -> str:
    """Create password reset token"""
    return auth_utils.create_password_reset_token(user_id)

def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify password reset token and return user ID"""
    return auth_utils.verify_password_reset_token(token)

def create_email_verification_token(user_id: str, email: str) -> str:
    """Create email verification token"""
    return auth_utils.create_email_verification_token(user_id, email)

def verify_email_verification_token(token: str) -> Optional[Dict[str, str]]:
    """Verify email verification token"""
    return auth_utils.verify_email_verification_token(token)
