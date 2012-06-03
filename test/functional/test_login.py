from selenium import selenium
import unittest, time, re

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*firefox", "http://localhost:8080/")
        self.selenium.start()

    def test_login(self):
        sel = self.selenium
        sel.open("/")
        sel.open("/user/login")
        sel.wait_for_page_to_load("60000")
        sel.type("name=nickname", "admin")
        sel.type("name=password", "admin")
        sel.click("xpath=//form/input[4]")
        sel.wait_for_page_to_load("60000")
        for i in range(60):
            try:
                if sel.is_text_present("You successfully signed in, welcome back!"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        for i in range(60):
            try:
                if sel.is_text_present("Logout"): break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        sel.click("xpath=//html")
        sel.click("link=Logout")
        sel.wait_for_page_to_load("60000")
        try: self.assertEqual("http://localhost:8080/", sel.get_location())
        except AssertionError, e: self.verificationErrors.append(str(e))

    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
