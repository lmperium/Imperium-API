import unittest
import json

from app import create_app, db


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():
            db.drop_all()
            db.create_all()

        self.analyst_info = json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'TestUser123',
            'password': 'EWesWQ211',
            'email': 'test@mail.com'
        })

    def test_analyst_registration(self):
        """Test API analyst registration."""
        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)
        self.assertIn('John', str(response.data))

        # Test registering the same user.
        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 409)
        self.assertIn('Analyst already registered', str(response.data))

    def test_get_all_analysts(self):
        """Test API get all analysts."""
        response = self.client().get('api/analysts')
        self.assertEqual(response.status_code, 200)
        self.assertIn('analysts', str(response.data))

        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)

        response = self.client().get('api/analysts')
        self.assertEqual(response.status_code, 200)
        self.assertIn('John', str(response.data))

    def test_get_analyst(self):
        """Test API to get analyst based on ID."""

        # Specified analyst does not exist.
        response = self.client().get('api/analysts/3')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Resource not found', str(response.data))

        # Add analyst.
        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)

        res_json = json.loads(response.data.decode('utf-8').replace("'", "\'"))

        analyst_id = res_json['analyst_id']

        # Test for specified analyst.
        response = self.client().get(f'api/analysts/{analyst_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn('John', str(response.data))


if __name__ == '__main__':
    unittest.main()
