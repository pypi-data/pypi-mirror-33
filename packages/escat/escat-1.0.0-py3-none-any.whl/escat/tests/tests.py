import unittest
from unittest.mock import patch

from escat import config
from escat.main import main


class ConfigTest(unittest.TestCase):

    @patch('getpass.getpass')
    def test_get_config_from_file(self, getpass):
        test_pass = 'somerandomlysetpassword'
        getpass.return_value = test_pass
        expected = {'hosts': ['http://localhost:9200'],
                    'auth': {'username': 'elastic',
                             'password': test_pass},
                    'ssl': {'enabled': False, 'cert': 'some_cer', 'ca': '', 'private_key': '', 'verify_certs': True},
                    'timeout': '30s'}
        self.assertDictEqual(expected, config.get_config_from_file('default', 'resources/config.yml'))


class MainTest(unittest.TestCase):
    @patch('getpass.getpass')
    def test_main(self, getpass):
        getpass.return_value  = 'thisismypassword'
        print(main(['nodes', '--config', 'resources/config.yml', '-f', 'json']))
