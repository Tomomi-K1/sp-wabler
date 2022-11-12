"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does repr method work as expected?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertIn('testuser, test@test.com>', repr(u))

    def test_is_not_following(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertEqual(False, user1.is_following(user2))

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        user1.following.append(user2)
        db.session.add(user1)
        db.session.commit()

        self.assertEqual(True, user1.is_following(user2))


    def test_is_followed_by(self):
        """Does is_following successfully detect when user1 is followed user2?"""
        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        user2.following.append(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertEqual(True, user1.is_followed_by(user2))

    def test_is_not_followed_by(self):
        """Does is_following successfully detect when user1 not is followed user2?"""
        user1 = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        user2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2"
        )

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertEqual(False, user1.is_followed_by(user2))

    def test_signup_with_valid_credentials(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        user=User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None
        )

        user_in_db = User.query.first() 

        self.assertEqual(user, user_in_db)

    # def test_signup_with_invalid_credentials(self):
    #     """Does User.signup fail to create a new user given valid credentials?"""
    
    #         user=User.signup(
    #             email="test@test.com",
    #             username=None,
    #             password="HASHED_PASSWORD",
    #             image_url=None
    #         )
           
    #     user_in_db = User.query.first() 
    #  テスト自体でエラーが起きる状況をテストするにはどうしたらよいのか？
    #     self.assertNotEqual(user, user_in_db)

    def test_authenticate_success(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(u, User.authenticate('testuser','HASHED_PASSWORD'))
    
    def test_authenticate_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
    
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.add(u)
        db.session.commit()

        self.assertFalse(User.authenticate('wrongname', 'HASHED_PASSWORD'))

    def test_authenticate_invalid_password(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
    
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=None
        )

        db.session.add(u)
        db.session.commit()

        self.assertFalse(User.authenticate('wrongname', 'wrong_password'))
        