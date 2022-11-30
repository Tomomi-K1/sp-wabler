"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
#  we need to import exception otherwise we cannot use "with self.assertRaise(exc.IntegrityError) as context"
from sqlalchemy import exc

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

        #clear exisiting database info and create new table
        db.drop_all()
        db.create_all()

        user1 = User.signup('test1', 'email1@email.com', 'password', None)
        uid1 = 1111
        user1.id = uid1
        
        user2 = User.signup('test2', 'email2@email.com', 'password', None)
        uid2 =2222
        user2.id = uid2

        db.session.commit()

        user1 = User.query.get(uid1)
        user2 = User.query.get(uid2)


        # we are asigning self.user1 = user1 so that user1 & user2 could be used throughout the test

        self.user1 = user1
        self.uid1 = uid1

        self.user2 = user2
        self.uid2 = uid2
        
        self.client = app.test_client()

    # def tearDown(self):
    #     User.query.delete()

    def tearDown(self):
        """Clean up fouled transactions."""
        
        res = super().tearDown()
        db.session.rollback()
        return res

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

    ############
    #  following test
    # ############
    # def test_is_not_following(self):
    #     """Does is_following successfully detect when user1 is not following user2?"""
        # user1 = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        # )

        # user2 = User(
        #     email="test2@test.com",
        #     username="testuser2",
        #     password="HASHED_PASSWORD2"
        # )

        # db.session.add(user1)
        # db.session.add(user2)
        # db.session.commit()


        # self.assertEqual(False, user1.is_following(user2))

    def test_is_following(self):
        """Does is_following successfully detect when user1 is following user2?"""
        # user1 = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        # )

        # user2 = User(
        #     email="test2@test.com",
        #     username="testuser2",
        #     password="HASHED_PASSWORD2"
        # )

        self.user1.following.append(self.user2)
        # db.session.add(user1)
        db.session.commit()

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertTrue(self.user1.is_following(self.user2))
        # this is testing user is not following
        self.assertFalse(self.user2.is_following(self.user1))


    def test_is_followed_by(self):
        """Does is_following successfully detect when user1 is followed user2?"""
        # user1 = User(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD"
        # )

        # user2 = User(
        #     email="test2@test.com",
        #     username="testuser2",
        #     password="HASHED_PASSWORD2"
        # )

        self.user2.following.append(self.user1)
        db.session.commit()

        self.assertTrue(self.user1.is_followed_by(self.user2))
        # this is testing user is not followed by
        self.assertFalse(self.user2.is_followed_by(self.user1))

    # def test_is_not_followed_by(self):
    #     """Does is_following successfully detect when user1 not is followed user2?"""
    #     user1 = User(
    #         email="test@test.com",
    #         username="testuser",
    #         password="HASHED_PASSWORD"
    #     )

    #     user2 = User(
    #         email="test2@test.com",
    #         username="testuser2",
    #         password="HASHED_PASSWORD2"
    #     )

    #     db.session.add(user1)
    #     db.session.add(user2)
    #     db.session.commit()

    #     self.assertEqual(False, user1.is_followed_by(user2))

    ############
    # Signup tests
    ############

    def test_signup_with_valid_credentials(self):
        """Does User.signup successfully create a new user given valid credentials?"""

        user=User.signup("testuser", "test@test.com", "HASHED_PASSWORD", None) 
        uid = 99999
        user.id = uid
        user = User.query.get(uid)
        print(user)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertNotEqual(user.password, 'HASHED_PASSWORD')
        #Bcrypt string should start with $2b$
        self.assertTrue(user.password.startswith("$2b$"))

        # user_in_db = User.query.first() 

        # self.assertEqual(user, user_in_db)

    def test_invalid_username_signup(self):
        """Does User.signup fail to create a new user given valid credentials?"""
        
        invalid_user=User.signup(
            email='test@test.com',
            username=None,
            password="HASHED_PASSWORD",
            image_url=None
        )
        uid = 123456789
        invalid_user.id = uid

        # テスト自体でエラーが起きる状況をテストするにはどうしたらよいのか？
        with self.assertRaises(exc.IntegrityError) as context:
            # this is how we can test when something throws error ==> use context manager.
            # exc.IntegrityError is the error name with SQLalchemy
            db.session.commit()
        
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup('testuser', "email@email.com", "", None)

    ################
    # authentification
    ################
    
    def test_authenticate_success(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""
        u = User.authenticate(self.user1.username, "password")

        # if user is authenticated, this method will return user.
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)
     
    
    def test_authenticate_invalid_username(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
    
        # u = User.signup(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD",
        #     image_url=None
        # )

        # db.session.add(u)
        # db.session.commit()

        self.assertFalse(User.authenticate('wrongname', 'HASHED_PASSWORD'))

    def test_authenticate_invalid_password(self):
        """Does User.authenticate fail to return a user when the username is invalid?"""
    
        # u = User.signup(
        #     email="test@test.com",
        #     username="testuser",
        #     password="HASHED_PASSWORD",
        #     image_url=None
        # )

        # db.session.add(u)
        # db.session.commit()

        self.assertFalse(User.authenticate(self.user1.username, 'wrong_password'))
        