import unittest
import json

from app import create_app, db


class AnalystTest(unittest.TestCase):

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

        self.email = 'test@mail.com'
        self.password = 'EWesWQ211'

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

        # Test with no authorization
        response = self.client().get('api/analysts')
        self.assertEqual(response.status_code, 401)

        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)
        self.assertIn('John', str(response.data))

        # Login
        response = self.client().post('api/login', data=json.dumps(dict(email=self.email, password=self.password)))
        self.assertEqual(response.status_code, 200)

        res_json = json.loads(response.data.decode('utf-8').replace("'", "\'"))
        access_token = 'Bearer ' + res_json['access_token']

        # Test with authorization
        response = self.client().get('api/analysts', headers=dict(Authorization=access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('John', str(response.data))

    def test_get_analyst_no_authorization(self):
        """Test API to get analyst based on ID."""

        # Specified analyst does not exist.
        response = self.client().get('api/analysts/1')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Missing Authorization Header', str(response.data))

    def test_get_analyst_with_authorization(self):
        # Add analyst.
        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)

        res_json = json.loads(response.data.decode('utf-8').replace("'", "\'"))
        analyst_id = res_json['analyst_id']

        # Login
        response = self.client().post('api/login', data=json.dumps(dict(email=self.email, password=self.password)))
        self.assertEqual(response.status_code, 200)

        res_json = json.loads(response.data.decode('utf-8').replace("'", "\'"))
        access_token = 'Bearer ' + res_json['access_token']

        # Test for specified analyst.
        response = self.client().get(f'api/analysts/{analyst_id}', headers=dict(Authorization=access_token))
        self.assertEqual(response.status_code, 200)
        self.assertIn('John', str(response.data))

    def test_analyst_login(self):
        """ Test API analyst login with JWT."""
        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(response.status_code, 201)

        # Test missing values
        response = self.client().post('api/login', data=json.dumps(dict(password='pass')))
        self.assertEqual(response.status_code, 400)
        self.assertIn('Must include', str(response.data))

        # Test incorrect password or email
        response = self.client().post('api/login', data=json.dumps(dict(email=self.email, password='incorrect')))
        self.assertEqual(response.status_code, 401)
        self.assertIn('Incorrect Email or password', str(response.data))

        # Test successful login
        response = self.client().post('api/login', data=json.dumps(dict(email=self.email, password=self.password)))
        self.assertEqual(response.status_code, 200)

        res_json = json.loads(response.data.decode('utf-8').replace("'", "\'"))

        self.assertIn('access_token', str(res_json))
        self.assertIn('refresh_token', str(res_json))
        self.assertIsNotNone(res_json['access_token'])
        self.assertIsNotNone(res_json['refresh_token'])


if __name__ == '__main__':
    unittest.main()
