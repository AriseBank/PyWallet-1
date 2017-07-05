import shutil
import unittest
from tempfile import mkdtemp

from pywalib import (NoTransactionFoundException, PyWalib,
                     UnknownEtherscanException)


class PywalibTestCase(unittest.TestCase):
    """
    Simple test cases, verifying pywalib works as expected.
    """

    @classmethod
    def setUpClass(cls):
        cls.keystore_dir = mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.keystore_dir, ignore_errors=True)

    def test_new_account(self):
        """
        Simple account creation test case.
        1) verifies the current account list is empty
        2) creates a new account and verify we can retrieve it
        3) tries to unlock the account
        """
        # 1) verifies the current account list is empty
        pywalib = PyWalib(PywalibTestCase.keystore_dir)
        account_list = pywalib.get_account_list()
        self.assertEqual(len(account_list), 0)
        # 2) creates a new account and verify we can retrieve it
        password = "password"
        # weak account, but fast creation
        security_ratio = 1
        account = pywalib.new_account(password, security_ratio)
        account_list = pywalib.get_account_list()
        self.assertEqual(len(account_list), 1)
        self.assertEqual(account, pywalib.get_main_account())
        # 3) tries to unlock the account
        # it's unlocked by default after creation
        self.assertFalse(account.locked)
        # let's lock it and unlock it back
        account.lock()
        self.assertTrue(account.locked)
        account.unlock(password)
        self.assertFalse(account.locked)

    def test_update_account_password(self):
        """
        Verifies updating account password works.
        """
        pywalib = PyWalib(PywalibTestCase.keystore_dir)
        current_password = "password"
        # weak account, but fast creation
        security_ratio = 1
        account = pywalib.new_account(current_password, security_ratio)
        # first try when the account is already unlocked
        self.assertFalse(account.locked)
        new_password = "new_password"
        # on unlocked account the current_password is optional
        pywalib.update_account_password(
            account, new_password, current_password=None)
        # verify it worked
        account.lock()
        account.unlock(new_password)
        self.assertFalse(account.locked)
        # now try when the account is first locked
        account.lock()
        current_password = "wrong password"
        with self.assertRaises(ValueError):
            pywalib.update_account_password(
                account, new_password, current_password)
        current_password = new_password
        pywalib.update_account_password(
            account, new_password, current_password)
        self.assertFalse(account.locked)

    def test_handle_etherscan_error(self):
        """
        Checks handle_etherscan_error() error handling.
        """
        response_json = {
            'message': 'No transactions found', 'result': [], 'status': '0'
        }
        with self.assertRaises(NoTransactionFoundException):
            PyWalib.handle_etherscan_error(response_json)
        response_json = {
            'message': 'Unknown error', 'result': [], 'status': '0'
        }
        with self.assertRaises(UnknownEtherscanException):
            PyWalib.handle_etherscan_error(response_json)

    def test_address_hex(self):
        """
        Checks handle_etherscan_error() error handling.
        """
        expected_addresss = "0xab5801a7d398351b8be11c439e05c5b3259aec9b"
        # no 0x prefix
        address = "ab5801a7d398351b8be11c439e05c5b3259aec9b"
        normalized = PyWalib.address_hex(address)
        self.assertEqual(normalized, expected_addresss)
        # uppercase
        address = "0xAB5801A7D398351B8BE11C439E05C5B3259AEC9B"
        normalized = PyWalib.address_hex(address)
        self.assertEqual(normalized, expected_addresss)


if __name__ == '__main__':
    unittest.main()
