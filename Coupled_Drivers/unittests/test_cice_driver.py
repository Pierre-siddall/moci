'''
*****************************COPYRIGHT******************************
 (C) Crown copyright 2022 Met Office. All rights reserved.

 Use, duplication or disclosure of this code is subject to the restrictions
 as set forth in the licence. If no licence has been raised with this copy
 of the code, the use, duplication or disclosure of it is strictly
 prohibited. Permission to do so must first be obtained in writing from the
 Met Office Information Asset Owner at the following address:

 Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB, United Kingdom
*****************************COPYRIGHT******************************
NAME
    test_cice_driver.py

DESCRIPTION
    Contains unit tests for the cice_driver.py module.
'''
import unittest
import unittest.mock as mock
import os
import io
import pathlib

import cice_driver
import error

TEMPDIR = os.getenv('TMPDIR')


class TestVerifyFixRestart(unittest.TestCase):
    """Unit tests for the _verify_fix_rst function"""
    def setUp(self):
        self.pointer_file = os.path.join(TEMPDIR, 'ice.restart_file')
        self.task_start = '2019,03,17,0,0,0'
        self.restart_path = os.path.join(
            TEMPDIR, 'cplfci.restart.2019-03-17-00000.nc')

        with open(self.pointer_file, 'w') as handle:
            handle.write(self.restart_path)

        pathlib.Path(self.restart_path).touch()

    def tearDown(self):
        os.remove(self.pointer_file)
        os.remove(self.restart_path)

    def test_verify_fix_rst_dates_match(self):
        """Check that the function behaves as expected if the
        task start and file restart dates match."""
        expected_msg = '[INFO] Validated CICE restart date\n'

        with mock.patch('sys.stdout', new=io.StringIO()) as output:
            cice_driver._verify_fix_rst(self.pointer_file, self.task_start)

        self.assertEqual(output.getvalue(), expected_msg)

    def test_verify_fix_rst_dates_no_match(self):
        """Check that a warning error is thrown and that the pointer
        file is updated if the task start date and the restart file date do
        not match."""
        task_start = '2019,01,22,0,0,0'
        task_start_yyyymmdd = task_start.replace(',', '').replace('000', '')
        expected_restart_date = '20190317'
        expected_restart_path = self.restart_path.replace(
            '2019-03-17', '2019-01-22')

        expected_msg = '[WARN ]The CICE restart data does not match the ' \
            ' current task start time\n.' \
            '   Task start time is %s\n' \
            '   CICE restart time is %s\n' % (
                task_start_yyyymmdd, expected_restart_date)

        with mock.patch('sys.stderr', new=io.StringIO()) as output:
            cice_driver._verify_fix_rst(self.pointer_file, task_start)

        self.assertEqual(output.getvalue(), expected_msg)

        # Check that the date in the pointer file has been updated
        with open(self.pointer_file, 'r') as handle:
            restart_path = handle.read().strip()

        self.assertEqual(restart_path, expected_restart_path)

    def test_verify_fix_rst_no_pointer(self):
        """Check that an error is returned if the pointer file cannot
        be found."""
        restart_path = '/no/files/here'
        expected_msg = (
            f'[INFO] The CICE restart file {restart_path} can not be found\n'
            )

        with open(self.pointer_file, 'w') as handle:
            handle.write(restart_path)

        with mock.patch('sys.stderr', new=io.StringIO()) as output:
            with self.assertRaises(SystemExit) as context:
                cice_driver._verify_fix_rst(self.pointer_file, self.task_start)

        self.assertEqual(output.getvalue(), expected_msg)
        self.assertEqual(
            context.exception.code, error.MISSING_MODEL_FILE_ERROR)
