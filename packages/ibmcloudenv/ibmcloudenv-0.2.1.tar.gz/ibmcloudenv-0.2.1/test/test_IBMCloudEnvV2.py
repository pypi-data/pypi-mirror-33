
import os
import unittest

from ibmcloudenv import IBMCloudEnv
import mock
import nose

class TestParser(unittest.TestCase):

	@mock.patch.dict(os.environ, {'VCAP_SERVICES': '{"service1": [{"name": "service1-name1","credentials": {"username": "service1-username1"}},{"name": "service1-name2","credentials": {"username": "service1-username2"}}],"user-provided": [{"name": "service2-name1", "credentials": {"username": "service2-username1"}}]}',
		'VCAP_APPLICATION': '{"application_name": "test-application"}',
		'ENV_VAR_STRING': 'test-12345',
		'ENV_VAR_JSON': '{"credentials": {"username": "env-var-json-username"}}' })
	def setUp(self):
		IBMCloudEnv.init("server/config/v2/mappings.json")

	def test_file_plain_text(self):
		self.assertTrue(type(IBMCloudEnv.getDictionary("var1")), dict)
		self.assertEqual(IBMCloudEnv.getDictionary("var1")["file_var1"], "plain-text-string")

	def test_file_jsonpath(self):
		self.assertTrue(type(IBMCloudEnv.getDictionary("var2")), dict)
		self.assertEqual(IBMCloudEnv.getDictionary("var2")["file_var2"], "{\"level2\": 12345}")

	def test_cf_service_instance(self):
		self.assertTrue(type(IBMCloudEnv.getDictionary("var1")), dict)
		self.assertEqual(IBMCloudEnv.getDictionary("var1")["cf_var1"], "{\"username\": \"service1-username1\"}")

	def test_cf_jsonpath(self):
		self.assertTrue(type(IBMCloudEnv.getDictionary("var2")), dict)
		self.assertEqual(IBMCloudEnv.getDictionary("var2")["cf_var2"], "service1-username1")

	def test_env_var_plain_text(self):
		self.assertTrue(type(IBMCloudEnv.getDictionary("var1")), dict)
		self.assertEqual(IBMCloudEnv.getDictionary("var1")["env_var1"], "test-12345")

	def test_env_var_json(self):
		self.assertTrue(type(IBMCloudEnv.getDictionary("var2")), dict)
		self.assertEqual(IBMCloudEnv.getDictionary("var2")["env_var2"], "{\"credentials\": {\"username\": \"env-var-json-username\"}}")

	def test_env_var_jsonpath(self):
		self.assertTrue(type(IBMCloudEnv.getDictionary("var3")), dict)
		self.assertEqual(IBMCloudEnv.getDictionary("var3")["env_var3"], "env-var-json-username")

	def test_bad_values(self):
		self.assertEqual(IBMCloudEnv.getDictionary("var1")["bad_var1"], "")
		self.assertEqual(IBMCloudEnv.getDictionary("var3")["bad_var3"], "")

if __name__ == '__main__':
	nose.run()
