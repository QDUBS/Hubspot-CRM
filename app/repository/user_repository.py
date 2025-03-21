from sqlalchemy import func
from ..models import db, User
import logging


class UserRepository:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    # Convert username to lowercase for proper checks
    def convert_username(self, username):
        return username.lower() if username else None

    # Get a user
    def get_user(self, username):
        try:
            username = self.convert_username(username)
            return User.query.filter(func.lower(User.username) == username).first()
        except Exception as e:
            self.logger.error(
                f"Error retrieving user '{username}': {str(e)}")
            return None

    # Create a new user
    def create(self, username, password):
        try:
            # Convert the username before checking for duplicates
            converted_username = self.convert_username(username)

            # Check if user already exists
            existing_user = self.get_user(converted_username)
            if existing_user:
                self.logger.warning(
                    f"Not allowed to create duplicate user: {username}")
                return None

            # Create a new user
            new_user = User(username=username)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            self.logger.info(f"New user created: {username}")
            return new_user

        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Error creating user '{username}': {str(e)}")
            raise
