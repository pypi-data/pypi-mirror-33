
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
		IBMCloudEnv.init()

	def test_file_plain_text(self):
		self.assertEqual(IBMCloudEnv.getString("file_var1"), "plain-text-string")
		self.assertTrue(type(IBMCloudEnv.getDictionary("file_var1")), dict)
		self.assertTrue("value" in IBMCloudEnv.getDictionary("file_var1"))
		self.assertEqual(IBMCloudEnv.getDictionary("file_var1")["value"], "plain-text-string")

	def test_file_jsonpath(self):
		self.assertEqual(IBMCloudEnv.getString("file_var2"), "{\"level2\": 12345}")
		self.assertTrue(type(IBMCloudEnv.getDictionary("file_var2")), dict)
		self.assertTrue("level2" in IBMCloudEnv.getDictionary("file_var2"))
		self.assertEqual(IBMCloudEnv.getDictionary("file_var2")["level2"], 12345)

	def test_cf_service_instance(self):
		self.assertEqual(IBMCloudEnv.getString("cf_var1"), "{\"username\": \"service1-username1\"}")
		self.assertTrue(type(IBMCloudEnv.getDictionary("cf_var1")), dict)
		self.assertTrue("username" in IBMCloudEnv.getDictionary("cf_var1"))
		self.assertEqual(IBMCloudEnv.getDictionary("cf_var1")["username"], "service1-username1")

	def test_cf_jsonpath(self):
		self.assertEqual(IBMCloudEnv.getString("cf_var2"), "service1-username1")
		self.assertTrue(type(IBMCloudEnv.getDictionary("cf_var2")), dict)
		self.assertTrue("value" in IBMCloudEnv.getDictionary("cf_var2"))
		self.assertEqual(IBMCloudEnv.getDictionary("cf_var2")["value"], "service1-username1")

	def test_env_var_plain_text(self):
		self.assertEqual(IBMCloudEnv.getString("env_var1"), "test-12345")
		self.assertTrue(type(IBMCloudEnv.getDictionary("env_var1")), dict)
		self.assertTrue("value" in IBMCloudEnv.getDictionary("env_var1"))
		self.assertEqual(IBMCloudEnv.getDictionary("env_var1")["value"], "test-12345")

	def test_env_var_json(self):
		self.assertEqual(IBMCloudEnv.getString("env_var2"), "{\"credentials\": {\"username\": \"env-var-json-username\"}}")
		self.assertTrue(type(IBMCloudEnv.getDictionary("env_var2")), dict)
		self.assertTrue("credentials" in IBMCloudEnv.getDictionary("env_var2"))
		self.assertEqual(IBMCloudEnv.getDictionary("env_var2")["credentials"]["username"], "env-var-json-username")

	def test_env_var_jsonpath(self):
		self.assertEqual(IBMCloudEnv.getString("env_var3"), "env-var-json-username")
		self.assertTrue(type(IBMCloudEnv.getDictionary("env_var3")), dict)
		self.assertTrue("value" in IBMCloudEnv.getDictionary("env_var3"))
		self.assertEqual(IBMCloudEnv.getDictionary("env_var3")["value"], "env-var-json-username")

	def test_bad_values(self):
		self.assertEqual(IBMCloudEnv.getString("bad_var1"), "")
		self.assertEqual(IBMCloudEnv.getDictionary("bad_var2"), {})
		self.assertEqual(IBMCloudEnv.getString("bad_var3"), "")

if __name__ == '__main__':
	nose.run()
