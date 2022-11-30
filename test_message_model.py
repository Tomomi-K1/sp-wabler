"""Message model tests."""

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
        #clear exisiting database info and create new table
        db.drop_all()
        db.create_all()

        # here we are creating user
        self.uid = 9999
        u=User.signup('testing', 'test@test.com', 'password', None)
        u.id = self.uid
        db.session.commit()
        # create user object using self.uid 9999
        self.u = User.query.get(self.uid)
        
        self.client = app.test_client()

    def tearDown(self):
        """Clean up fouled transactions."""
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Does basic message model work?"""

        msg = Message(
            text="this is test",
            user_id = self.uid
            )

        # self.u.messages.append(msg)
        db.session.add(msg)
        db.session.commit()

        # u should have 1 msg
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "this is test")

    def test_message_likes(self):
        
        m1 = Message(text='test1', user_id=self.uid)
        m2 = Message(text='test2', user_id=self.uid)

        u = User.signup("yetanothertest", "t@email.com", "password", None)
        uid = 888
        u.id = uid
        db.session.add_all([m1, m2, u])
        db.session.commit()

        u.likes.append(m1)
        db.session.commit()

        likes = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, m1.id)



    