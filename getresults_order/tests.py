from getresults.tests.base_selenium_test import BaseSeleniumTest


class TestSelenium(BaseSeleniumTest):

    def test_admin(self):
        self.navigate_to_admin()
        self.login()
