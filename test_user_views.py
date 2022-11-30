"""user view function tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, connect_db, User, Message, Follows, Likes
from bs4 import BeautifulSoup

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewFunctionTestCase(TestCase):
    """test views for users"""

    def setUp(self):
        """create test client and add sample data"""
        #delete db and create again
        db.drop_all()
        db.create_all()
        
        # name app.test_client() as self.client so less typing
        # ???what do we set this as self.client??? to just shorten it?
        self.client = app.test_client()    
        
        #create the sample user
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        # set user id to randam id set by testuser_id
        self.testuser_id =8989
        self.testuser.id = self.testuser_id

        # create several users as u1, u2, u3, u4
        self.u1 = User.signup('abc', 'test1@test.com', 'password', None)
        self.u1_id = 778
        # ??? why do we set id#? I thought this is automatically assigned???
        self.u1.id=self.u1_id

        self.u2 = User.signup("efg", "test2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id

        self.u3 = User.signup("hij", "test3@test.com", "password", None)

        self.u4 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
    #    ????what  does this do??????
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        """does list of all users come up?"""
        with self.client as c:
            response=c.get('/users')
            # response.data is the bytes returned by the view so you need make it into text by either using response.text or response.get_data(as_text = True) or make response.data into string with str() python method.
           
        self.assertIn('@testuser', str(response.data))
        self.assertIn('@abc', str(response.data))
        self.assertIn('@efg', str(response.data))
        self.assertIn('@hij', str(response.data))
        self.assertIn('@testing', str(response.data))

    def test_users_search(self):
        """Does Search function work correctly?"""
        with self.client as c:
            response = c.get('/users?q=test')
        
        self.assertIn('@testuser', str(response.data))
        self.assertIn('@testing', str(response.data))

        self.assertNotIn('@efg', str(response.data))
        self.assertNotIn('@hij', str(response.data))

    def test_user_show(self):
        """does each user's page show?"""
        with self.client as c:
            response = c.get(f'/users/{self.testuser_id}')

            self.assertEqual(response.status_code, 200)
            self.assertIn('@testuser', str(response.data))

    def setup_likes(self):
        """this function is not a test itself. It is used in the next test to set up to test likes. Notice that this function does not start with "test_" """

        m1 = Message(text="trending warble", user_id=self.testuser_id)
        m2 = Message(text="Eating some lunch", user_id=self.testuser_id)
        m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 = Likes(user_id = self.testuser_id, message_id=9876)
        db.session.add(l1)
        db.session.commit()

    def test_user_show_with_likes(self):
        self.setup_likes()

        with self.client as c:
            response = c.get(f'/users/{self.testuser_id}')

            self.assertEqual(response.status_code, 200)

            self.assertIn('@testuser', str(response.data))
            
            # It is indeed just grabbing your html and making assertions about what it finds:
            # It's saying you should have four “li” tags that have a class of “stat”.
            # The first li from that group should have a “2” in it, etc.
            # So in this case, they are just using it as another way to parse your html and analyze it.
            # It can be used for things like going to a page with a list of items, and getting the price, description, and img src of each item.
            soup = BeautifulSoup(response.data, 'html.parser')
            # check detail.html to find 4 of <li class='stat'> 
            found=soup.find_all('li', {'class': 'stat'})
            self.assertEqual(len(found), 4)
  
            self.assertIn('2', found[0].text)
            self.assertIn('0', found[1].text)
            self.assertIn('0', found[2].text)
            self.assertIn('1', found[3].text)

    def test_add_likes(self):

        m = Message(id=1984, text="hello test", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            response = c.post(f'/users/add_like/1984', follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == 1984).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_likes(self):

        self.setup_likes()

        m = Message.query.filter(Message.text == "likable warble").one()

        # tjhis is checking there is a message with text "likable warble"
        self.assertIsNotNone(m)
        # this is checking message's writer is not testuser(writer is u1)
        self.assertNotEqual(m.user_id, self.testuser_id)

        # selecting the msg liked in the Setup_likes()
        l = Likes.query.filter(Likes.user_id == self.testuser_id and Likes.message_id == m.id).one()

        # Now we are sure that testuser likes the message "likable warble"
        self.assertIsNotNone(l)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            response = c.post(f'/users/add_like/{m.id}', follow_redirects=True)

            self.assertEqual(response.status_code, 200)

            # get liked message m from Likes table if there is, but there should not be since like is removed
            likes = Likes.query.filter(Likes.message_id == m.id).all()

            self.assertEqual(len(likes), 0)
    
    def test_unauthenticated_likes(self):
        self.setup_likes()

        m = Message.query.filter(Message.text =="likable warble").one()
        self.assertIsNotNone(m)

        like_count = Likes.query.count()
        # self.assertEqual(likes_count, 1)
        with self.client as c:
            response = c.post(f'/users/add_like/{m.id}', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            
            # here we are trying to prove. 
            # if not g.user:
            # flash("Access unauthorized.", "danger")
            # return redirect("/") 
            # is in effect since we didn't use with c.session_transaction() as sess to set g.user

            self.assertIn("Access unauthorized", str(response.data))

             # The number of likes has not changed since making the request
            self.assertEqual(like_count, Likes.query.count())

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()

    def test_user_show_with_follows(self):
        """this is testing how user's details page show number of message, likes, followers and following"""
        self.setup_followers()

        with self.client as c:
            response = c.get(f'/users/{self.testuser_id}')

            self.assertEqual(response.status_code, 200)

            self.assertIn('@testuser', str(response.data))
            soup = BeautifulSoup(str(response.data), 'html.parser')
            found = soup.find_all('li', {'class':'stat'})
            self.assertEqual(len(found), 4)

             # test for a count of 0 messages
            self.assertIn("0", found[0].text)

            # Test for a count of 2 following
            self.assertIn("2", found[1].text)

            # Test for a count of 1 follower
            self.assertIn("1", found[2].text)

            # Test for a count of 0 likes
            self.assertIn("0", found[3].text)

    def test_show_following(self):
        """test if it shows the list of poeple user is following"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            response = c.get(f'/users/{self.testuser_id}/following')

            self.assertEqual(response.status_code, 200)
            self.assertIn('@abc', str(response.data))
            self.assertIn('@efg', str(response.data))
            self.assertNotIn('@hij', str(response.data))
            self.assertNotIn('@testing', str(response.data))

    def test_show_followers(self):
        """testing page to show user's followers"""

        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            response = c.get(f'/users/{self.testuser_id}/followers')

        self.assertEqual(response.status_code, 200)
        self.assertIn('@abc', str(response.data))
        self.assertNotIn('@efg', str(response.data))
        self.assertNotIn('@testing', str(response.data))
        self.assertNotIn('@hij', str(response.data))

    def test_unauthorized_following_page_access(self):
        self.setup_followers()

        with self.client as c:
            response = c.get(f'/users/{self.testuser_id}/following', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertNotIn('@abc', str(response.data))
            self.assertIn('Access unauthorized', str(response.data))






    


# You should also be testing authentication and authorization. Here are some examples of questions your view function tests should answer regarding these ideas:
# When you’re logged in, can you see the follower / following pages for any user?
# When you’re logged out, are you disallowed from visiting a user’s follower / following pages?
# When you’re logged in, can you add a message as yourself?
# When you’re logged in, can you delete a message as yourself?
# When you’re logged out, are you prohibited from adding messages?
# When you’re logged out, are you prohibited from deleting messages?
# When you’re logged in, are you prohibiting from adding a message as another user?
# When you’re logged in, are you prohibiting from deleting a message as another user?