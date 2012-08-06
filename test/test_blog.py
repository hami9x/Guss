import unittest
from google.appengine.ext import testbed
from guss import blog

class TestBlog(unittest.TestCase):
    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()

    def test_make_slug(self):
        blg = blog.BlogModel(title="Just Test")
        blg.make_slug()
        self.assertEqual(blg.slug, "just-test")
        blg.put()
        blg.make_slug()
        self.assertEqual(blg.slug, "just-test-2")
