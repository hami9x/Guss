from guss import utest, post

class PostTest(utest.TestCase):
    def setUp(self):
        self.init_db_stub()

    def test_slave_count(self):
        master = post.MasterPostModel()
        master.put()
        self.assertEqual(master.slave_count, 0)
        for i in range(1, 4):
            slave = post.SlavePostModel(parent=master.key)
            slave.put(force_validation=False)
            master=master.key.get()
            self.assertEqual(master.slave_count, i)
