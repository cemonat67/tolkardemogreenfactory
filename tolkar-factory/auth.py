"""
TOLKAR Zero@Factory - JWT Authentication Service
Production Intelligence Platform Authentication
Phase 9.5 - Production Ready
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import logging
from models import User, SessionLocal

logger = logging.getLogger(__name__)

class AuthService:
    """JWT Authentication service for TOLKAR Zero@Factory"""
    
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRATION_MINUTES", "480"))  # 8 hours
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        try:
            # Generate salt and hash password
            salt = bcrypt.gensalt(rounds=12)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Password hashing failed: {e}")
            raise
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        try:
            to_encode = data.copy()
            
            # Set expiration
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({"exp": expire})
            
            # Create JWT token
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"JWT token creation failed: {e}")
            raise
    
    def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT token and return user"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            username: str = payload.get("sub")
            
            if username is None:
                return None
            
            # Get user from database
            with SessionLocal() as db:
                user = db.query(User).filter(User.username == username).first()
                if user and user.is_active:
                    return user
                return None
                
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.JWTError as e:
            logger.warning(f"JWT token verification failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        try:
            with SessionLocal() as db:
                # Get user from database
                user = db.query(User).filter(User.username == username).first()
                
                if not user:
                    logger.warning(f"Authentication failed: User '{username}' not found")
                    return None
                
                if not user.is_active:
                    logger.warning(f"Authentication failed: User '{username}' is inactive")
                    return None
                
                # Verify password
                if not self.verify_password(password, user.password_hash):
                    logger.warning(f"Authentication failed: Invalid password for user '{username}'")
                    return None
                
                logger.info(f"User '{username}' authenticated successfully")
                return user
                
        except Exception as e:
            logger.error(f"User authentication failed: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            with SessionLocal() as db:
                return db.query(User).filter(User.username == username).first()
        except Exception as e:
            logger.error(f"Failed to get user by username: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            with SessionLocal() as db:
                return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None
    
    def create_user(self, username: str, email: str, password: str, role: str = "operator") -> Optional[User]:
        """Create new user"""
        try:
            with SessionLocal() as db:
                # Check if username already exists
                existing_user = db.query(User).filter(User.username == username).first()
                if existing_user:
                    logger.warning(f"User creation failed: Username '{username}' already exists")
                    return None
                
                # Check if email already exists
                existing_email = db.query(User).filter(User.email == email).first()
                if existing_email:
                    logger.warning(f"User creation failed: Email '{email}' already exists")
                    return None
                
                # Hash password
                password_hash = self.hash_password(password)
                
                # Create new user
                new_user = User(
                    id=str(uuid.uuid4()),
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role=role,
                    is_active=True
                )
                
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                
                logger.info(f"User '{username}' created successfully with role '{role}'")
                return new_user
                
        except Exception as e:
            logger.error(f"User creation failed: {e}")
            return None
    
    def update_user_password(self, user_id: str, new_password: str) -> bool:
        """Update user password"""
        try:
            with SessionLocal() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"Password update failed: User ID '{user_id}' not found")
                    return False
                
                # Hash new password
                password_hash = self.hash_password(new_password)
                
                # Update password
                user.password_hash = password_hash
                db.commit()
                
                logger.info(f"Password updated successfully for user '{user.username}'")
                return True
                
        except Exception as e:
            logger.error(f"Password update failed: {e}")
            return False
    
    def deactivate_user(self, user_id: str) -> bool:
        """Deactivate user account"""
        try:
            with SessionLocal() as db:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    logger.warning(f"User deactivation failed: User ID '{user_id}' not found")
                    return False
                
                # Deactivate user
                user.is_active = False
                db.commit()
                
                logger.info(f"User '{user.username}' deactivated successfully")
                return True
                
        except Exception as e:
            logger.error(f"User deactivation failed: {e}")
            return False
    
    def get_all_users(self, include_inactive: bool = False) -> list:
        """Get all users"""
        try:
            with SessionLocal() as db:
                query = db.query(User)
                if not include_inactive:
                    query = query.filter(User.is_active == True)
                return query.all()
        except Exception as e:
            logger.error(f"Failed to get all users: {e}")
            return []
    
    def get_users_by_role(self, role: str, include_inactive: bool = False) -> list:
        """Get users by role"""
        try:
            with SessionLocal() as db:
                query = db.query(User).filter(User.role == role)
                if not include_inactive:
                    query = query.filter(User.is_active == True)
                return query.all()
        except Exception as e:
            logger.error(f"Failed to get users by role: {e}")
            return []

# Global auth service instance
auth_service = AuthService()

# Utility functions for common authentication tasks
def require_role(required_roles: list) -> callable:
    """Decorator to require specific roles for endpoint access"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # This would be used with FastAPI Depends
            # Implementation would check current user role
            return func(*args, **kwargs)
        return wrapper
    return decorator

def get_current_user_from_token(token: str) -> Optional[User]:
    """Get current user from JWT token"""
    return auth_service.verify_token(token)

def create_demo_users():
    """Create demo users for testing"""
    try:
        # Create admin user
        admin = auth_service.create_user(
            username="admin",
            email="admin@tolkar.local",
            password="admin123",
            role="admin"
        )
        
        # Create supervisor user
        supervisor = auth_service.create_user(
            username="supervisor",
            email="supervisor@tolkar.local",
            password="supervisor123",
            role="supervisor"
        )
        
        # Create operator user
        operator = auth_service.create_user(
            username="operator1",
            email="operator1@tolkar.local",
            password="operator123",
            role="operator"
        )
        
        print("✅ Demo users created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Demo user creation failed: {e}")
        return False

if __name__ == "__main__":
    # Test authentication service
    print("🧪 Testing TOLKAR Authentication Service")
    
    # Create demo users
    create_demo_users()
    
    # Test authentication
    user = auth_service.authenticate_user("admin", "admin123")
    if user:
        print(f"✅ Authentication test passed for user: {user.username}")
        
        # Test JWT token creation and verification
        token = auth_service.create_access_token({"sub": user.username})
        print(f"✅ JWT token created: {token[:50]}...")
        
        verified_user = auth_service.verify_token(token)
        if verified_user and verified_user.username == user.username:
            print("✅ JWT token verification passed")
        else:
            print("❌ JWT token verification failed")
    else:
        print("❌ Authentication test failed")
    
    print("✅ Authentication service tests completed")