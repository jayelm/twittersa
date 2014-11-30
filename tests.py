"""
Tests for TwitterSA

These tests might be overkill, it's my first time messing around
with unit tests.

Jesse Mu
"""

import TwitterSA
import unittest


class TwitterSATestCase(unittest.TestCase):
    def setUp(self):
        TwitterSA.app.config['TESTING'] = True
        self.app = TwitterSA.app.test_client()

    def tearDown(self):
        pass

    def test_twitter_api(self):
        """Test to make sure the API is getting tweets"""
        tweets = TwitterSA.api.search(q='hello')
        assert tweets and len(tweets)

    def test_invalid_search_query(self):
        """Test for invalid search queries"""
        rv = self.app.get('/search?q=')
        assert 'Invalid search query' in rv.data
        rv = self.app.get('/search?nonsense=nonsense')
        assert 'Invalid search query' in rv.data

    def test_invalid_user_id(self):
        """Test for invalid user ids"""
        rv = self.app.get('/user?uid=')
        assert 'Invalid user id' in rv.data
        rv = self.app.get('/user?nonsense=nonsense')
        assert 'Invalid user id' in rv.data


if __name__ == '__main__':
    unittest.main()
