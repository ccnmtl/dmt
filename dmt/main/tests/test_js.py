from casper.tests import CasperTestCase
import os.path


class CasperIntegrationTestsAnonUser(CasperTestCase):
    def test_integration_tests_anon_user(self):
        path = os.path.join(
            os.path.dirname(__file__),
            'js/integration_tests_anon_user.js')
        self.assertTrue(self.casper(path))
