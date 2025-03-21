import pytest
import uuid
from sqlalchemy import func
from app.repository.user_repository import UserRepository
from app.models import User, GeneratedText


class TestUserRepository:
    """Test the User Repository"""

    def test_create_user(self, session):
        """Test creating a user through the repository"""
        # First clear all existing users named "newuser"
        session.query(User).filter(func.lower(User.username) == "newuser").delete()
        session.commit()

        repo = UserRepository()
        username = "newuser"
        password = "strongpassword"

        user = repo.create(username, password)

        assert user is not None
        assert user.username == username
        assert user.check_password(password) is True

        # Verify in database
        db_user = session.query(User).filter_by(username=username).first()
        assert db_user is not None
        assert db_user.id == user.id

    def test_get_by_username(self, session):
        """Test retrieving a user by username"""
        # Create user directly in DB
        user = User(username="findme")
        user.set_password("mypassword")
        session.add(user)
        session.commit()

        # Try to find with repository
        repo = UserRepository()
        found_user = repo.get_by_username("findme")

        assert found_user is not None
        assert found_user.id == user.id

        # Test with non-existent username
        nonexistent = repo.get_by_username("doesnotexist")
        assert nonexistent is None

    def test_username_case_insensitive(self, session):
        """Test that username lookups are case insensitive"""
        # Create user with mixed case
        user = User(username="MixedCase")
        user.set_password("password")
        session.add(user)
        session.commit()

        # Try to find with different cases
        repo = UserRepository()
        found1 = repo.get_by_username("mixedcase")
        found2 = repo.get_by_username("MIXEDCASE")
        found3 = repo.get_by_username("MixedCase")

        assert found1 is not None
        assert found2 is not None
        assert found3 is not None
        assert found1.id == user.id
        assert found2.id == user.id
        assert found3.id == user.id

    def test_duplicate_username(self, session):
        """Test that creating a duplicate username returns None"""
        # Create user with a unique name using UUID
        unique_name = f"duplicate_{uuid.uuid4().hex[:8]}"
        repo = UserRepository()
        user1 = repo.create(unique_name, "password1")

        # Try to create again with same username but different case
        user2 = repo.create(unique_name.upper(), "password2")

        assert user1 is not None
        assert user2 is None

    def test_get_by_id(self, session):
        """Test retrieving a user by ID"""
        # Create user
        user = User(username="iduser")
        user.set_password("password")
        session.add(user)
        session.commit()

        # Retrieve by ID
        repo = UserRepository()
        found_user = repo.get_by_id(user.id)

        assert found_user is not None
        assert found_user.username == "iduser"

        # Test with invalid ID
        nonexistent = repo.get_by_id(9999)
        assert nonexistent is None

    def test_update_password(self, session):
        """Test updating a user's password"""
        # Create user
        user = User(username="updatepw")
        user.set_password("oldpassword")
        session.add(user)
        session.commit()

        # Update password
        repo = UserRepository()
        success = repo.update_password(user.id, "newpassword")

        assert success is True

        # Verify password was changed
        updated_user = session.query(User).get(user.id)
        assert updated_user.check_password("oldpassword") is False
        assert updated_user.check_password("newpassword") is True

    def test_delete_user(self, session):
        """Test deleting a user"""
        # Create user
        user = User(username="deleteuser")
        user.set_password("password")
        session.add(user)
        session.commit()

        user_id = user.id

        # Delete user
        repo = UserRepository()
        success = repo.delete(user_id)

        assert success is True

        # Verify user was deleted
        deleted_user = session.query(User).get(user_id)
        assert deleted_user is None
