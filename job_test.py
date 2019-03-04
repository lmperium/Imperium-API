import json
import unittest

from app import create_app, db


class JobApiTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client

        with self.app.app_context():
            db.drop_all()
            db.create_all()

        self.job = {
                'name': 'test mq',
                'target': 'imp.wk.DESKTOP-RR5VV32',
                'description': [
                    {
                        'module': 'file',
                        'file_target': 'hash12354',
                        'parameters': {
                            'is_hash': True,
                            'paths': []
                        }
                    }
                ]
            }

        self.analyst_info = json.dumps({
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'TestUser123',
            'password': 'EWesWQ211',
            'email': 'test@mail.com'
        })

        self.email = 'test@mail.com'
        self.password = 'EWesWQ211'

    def _login(self):
        response = self.client().post('api/analysts', data=self.analyst_info)
        self.assertEqual(201, response.status_code)

        analyst_id = json.loads(response.data.decode('utf-8').replace("'", "\'"))['analyst_id']

        response = self.client().post('api/login', data=json.dumps(dict(email=self.email, password=self.password)))
        self.assertEqual(200, response.status_code)

        res_json = json.loads(response.data.decode('utf-8').replace("'", "\'"))
        access_token = 'Bearer ' + res_json['access_token']

        return access_token, analyst_id

    def test_create_job(self):

        access_token, analyst_id = self._login()

        self.job['analyst_id'] = analyst_id

        response = self.client().post('api/jobs', headers=dict(Authorization=access_token), data=json.dumps(self.job))
        self.assertEqual(201, response.status_code)
        self.assertIn('job_id', str(response.data))


if __name__ == '__main__':
    unittest.main()
