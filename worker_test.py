import json
import unittest

from app import create_app, db


class WorkerApiTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():
            db.drop_all()
            db.create_all()

        self.start_up_info = json.dumps({
            'hostname': 'DESKTOP-RR5VV32',
            'startup_info': {
                'system_name': 'DESKTOP-RR5VV32',
                'system_type': 'x64-based-pc',
                'os_name': 'Microsoft Windows 10 Pro',
                'ip_address': ['192.168.0.1', 'ipv6']
            }
        })

        self.analyst_info = json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'TestUser123',
            'password': 'EWesWQ211',
            'email': 'test@mail.com'
        })

        self.email = 'test@mail.com'
        self.password = 'EWesWQ211'

    def test_worker_registration(self):
        """ Test worker registration through the API."""

        # Successful registration
        response = self.client().post('/api/workers', data=self.start_up_info)
        self.assertEqual(201, response.status_code)
        self.assertIn('target_queue', str(response.data))

        # Test existing worker
        response = self.client().post('/api/workers', data=self.start_up_info)
        self.assertEqual(409, response.status_code)
        self.assertIn('Worker already registered', str(response.data))

    def test_get_worker_list(self):
        """ Test get all registered workers."""
        access_token = self._login()

        response = self.client().post('/api/workers', data=self.start_up_info)
        self.assertEqual(201, response.status_code)
        self.assertIn('target_queue', str(response.data))

        response = self.client().get('/api/workers', headers=dict(Authorization=access_token))
        self.assertEqual(200, response.status_code)
        self.assertIn('DESKTOP-RR5VV32', str(response.data))

    def test_get_worker_by_id(self):
        """ Test get worker by id."""
        response = self.client().post('/api/workers', data=self.start_up_info)
        self.assertEqual(201, response.status_code)
        self.assertIn('target_queue', str(response.data))

        access_token = self._login()
        body = json.loads(response.data.decode('utf-8').replace("'", "\'"))
        worker_id = body['worker_id']

        response = self.client().get(f'/api/workers/{worker_id}', headers=dict(Authorization=access_token))
        self.assertEqual(200, response.status_code)
        self.assertIn('DESKTOP-RR5VV32', str(response.data))

    def _login(self):
        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(201, response.status_code)
        response = self.client().post('api/login', data=json.dumps(dict(email=self.email, password=self.password)))
        self.assertEqual(200, response.status_code)

        res_json = json.loads(response.data.decode('utf-8').replace("'", "\'"))
        access_token = 'Bearer ' + res_json['access_token']

        return access_token


if __name__ == '__main__':
    unittest.main()
