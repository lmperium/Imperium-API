import unittest

from app import create_app, db


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():
            db.create_all()

        self.analyst_info = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'TestUser123',
            'password': 'EWesWQ211',
        }

    def test_analyst_registration(self):
        """Test API analyst registration"""
        response = self.client().post('/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Analyst Registered', str(response.data))

    def test_get_all_analysts(self):
        response = self.client().post('/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)

        # Check for duplicates
        response = self.client().get('/analysts')
        self.assertEqual(response.status_code, 200)
        self.assertIn('John', str(response.data))

    # def test_get_analyst(self):
    #     response = self.client().get('/analayst')


if __name__ == '__main__':
    unittest.main()
