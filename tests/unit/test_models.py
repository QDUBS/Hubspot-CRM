import pytest
from datetime import datetime
from app.models import User, GeneratedText


class TestUserModel:
    """Test the User model"""

    def test_user_creation(self, session):
        """Test creating a new user"""
        user = User(username="testuser123")
        user.set_password("securepassword")

        session.add(user)
        session.commit()

        # Query the user
        queried_user = session.query(User).filter_by(username="testuser123").first()

        assert queried_user is not None
        assert queried_user.username == "testuser123"
        assert queried_user.check_password("securepassword") is True
        assert queried_user.check_password("wrongpassword") is False
        assert isinstance(queried_user.created_at, datetime)

    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        user = User(username="passworduser")
        password = "mysecretpassword"
        user.set_password(password)

        # Password should be hashed, not stored in plaintext
        assert user.password_hash != password
        assert user.check_password(password) is True

    def test_user_representation(self):
        """Test the string representation of a user"""
        user = User(username="repuser")
        assert str(user) == "<User repuser>"
