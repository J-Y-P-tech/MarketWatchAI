"""
Test custom Django management commands.
"""
from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """
    Test commands.

    @patch('core.management.commands.wait_for_db.Command.check')
    is a Python decorator that uses the patch function from the
    unittest.mock library to temporarily replace the check method
    of the Command class in the core.management.commands.wait_for_db
    module with a mock object.
    """

    def test_wait_for_db_ready(self, patched_check):
        """
        Test waiting for database if database ready.

        patched_check parameter is the mock object that was created
        by the @patch decorator, and is passed to the test method automatically.

        """
        patched_check.return_value = True
        call_command('wait_for_db')
        """
        Inside the test method, we configure the patched_check mock object 
        to return True when it is called. We then call the wait_for_db command 
        using the call_command function provided by Django, which simulates 
        calling the command from the command line.
        """

        patched_check.assert_called_once_with(databases=['default'])

        """
        Finally, we use the assert_called_once_with method of the patched_check 
        mock object to assert that the check method was called once with the 
        database argument set to ['default']. This allows us to check that the 
        wait_for_db command is correctly calling the check method with the 
        expected arguments.
        """

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """
        Test waiting for database when getting OperationalError.

        @patch('time.sleep') will simulate (mock) waiting without
        actually waiting.

        The way we make mock to raise an exception is to use
        side_effect method. In the given example below:
        the 1-st 2 times we call Psycopg2Error
        the 2-nd 3 times we call OperationalError
        finaly return True
        """
        patched_check.side_effect = [Psycopg2Error] * 2 + \
                                    [OperationalError] * 3 + [True]

        call_command('wait_for_db')

        self.assertEqual(patched_check.call_count, 6)
        """ 6 is the total number of exceptions """
        patched_check.assert_called_with(databases=['default'])
