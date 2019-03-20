#!/usr/bin/env python3
"""
Unit tests for methods in util.py.
Theses tests will be performed using the settings in config.py and secrets.py.
"""

import os
import logging
import unittest
from unittest.mock import MagicMock, patch

import git
import mysql.connector

import config
import util

# This user must both have a standard and PE home directory.
valid_chpc_user = "u0407846"


class TestUtilMethods(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Clean up any of the test files we might use before we
        begin our tests and mock the LOGGER so we don't push
        anything to syslog.
        """
        cls.clean_up_files()
        util.LOGGER = MagicMock(spec=logging.Logger)

    @classmethod
    def tearDownClass(cls):
        """
        Ensure we didn't keep any of the job information in bconsole.
        Also tests to ensure we can reload the bconsole.
        """
        cls.clean_up_files()
        util.reload_bconsole()

    @classmethod
    def clean_up_files(cls):
        """
        Ensuring we don't have any of our test files already
        existing.
        """
        if os.path.exists(f"{config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf"):
            os.remove(f"{config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf")

        if os.path.exists(f"{config.JOB_FILE_LOCATION}/TEST_DEF_JOB_FILE.conf"):
            os.remove(f"{config.JOB_FILE_LOCATION}/TEST_DEF_JOB_FILE.conf")

        if os.path.exists(f"{config.FILESET_FILE_LOCATION}/TEST_FILE_SET.conf"):
            os.remove(f"{config.FILESET_FILE_LOCATION}/TEST_FILE_SET.conf")

    def test_job_file(self):
        """
        Testing our write_job_file and remove_job_file methods.
        """

        # Test write.
        util.write_job_file(
            name="TEST_JOB_FILE",
            fileset="TEST_JOB_FILE_SET",
            client="TEST_JOB_CLIENT",
            jobdef="TEST_JOB_JOBDEF",
            storage="TEST_JOB_STORAGE",
        )

        # Ensure we logged properly.
        util.LOGGER.info.assert_called_with(
            f"Wrote new job file at {config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf with "
            f"name=TEST_JOB_FILE, fileset=TEST_JOB_FILE_SET, client=TEST_JOB_CLIENT, "
            f"jobdef=TEST_JOB_JOBDEF, storage=TEST_JOB_STORAGE"
        )

        # Sanity check: compare file contents.
        file_contents = ""
        expected_contents = ""

        with open(f"{config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf", "r") as f:
            file_contents = f.read()

        with open("templates/job.txt", "r") as f:
            expected_contents = f.read()

        expected_contents = expected_contents.format(
            name="TEST_JOB_FILE",
            fileset="TEST_JOB_FILE_SET",
            client="TEST_JOB_CLIENT",
            jobdef="TEST_JOB_JOBDEF",
            storage="TEST_JOB_STORAGE",
        )

        self.assertEqual(file_contents, expected_contents)

        # Ensure we get an exception when the file already exists.
        with self.assertRaises(FileExistsError):
            util.write_job_file(
                name="TEST_JOB_FILE",
                fileset="TEST_JOB_FILE_SET",
                client="TEST_JOB_CLIENT",
                jobdef="TEST_JOB_JOBDEF",
                storage="TEST_JOB_STORAGE",
            )

        # Assert that we have logged the error from above.
        util.LOGGER.error.assert_called_with(
            f"Job file for 'TEST_JOB_FILE' already exists at "
            f"{config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf"
        )

        # Test remove.
        util.remove_job_file("TEST_JOB_FILE")
        self.assertFalse(
            os.path.exists(f"{config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf")
        )

        # Ensure we logged properly.
        util.LOGGER.info.assert_called_with(
            f"Removed job file at {config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf"
        )

        # Ensure we get an exception when the file doesn't exist.
        with self.assertRaises(FileNotFoundError):
            util.remove_job_file("TEST_JOB_FILE")

        # Assert that we logged the error from above.
        util.LOGGER.error.assert_called_with(
            f"Job file for 'TEST_JOB_FILE' not found at "
            f"{config.JOB_FILE_LOCATION}/TEST_JOB_FILE.conf"
        )

    def test_write_file_set_file(self):
        """
        Testing the write and remove file set methods.
        """
        # Test write.
        util.write_file_set_file(
            "TEST_FILE_SET", "TEST_FILE_SET_DESCRIPTION", "/home/TEST_DIR", "TESTCOMP"
        )

        # Ensure we logged properly.
        util.LOGGER.info.assert_called_with(
            f"Wrote new FileSet file at "
            f"{config.FILESET_FILE_LOCATION}/TEST_FILE_SET.conf "
            f"with name=TEST_FILE_SET, description=TEST_FILE_SET_DESCRIPTION, "
            f"file_location=/home/TEST_DIR, compression=TESTCOMP"
        )

        # Sanity check: compare file contents.
        file_contents = ""
        expected_contents = ""

        with open(f"{config.FILESET_FILE_LOCATION}/TEST_FILE_SET.conf", "r") as f:
            file_contents = f.read()

        with open(f"templates/fileset.txt", "r") as f:
            expected_contents = f.read()

        expected_contents = expected_contents.format(
            name="TEST_FILE_SET",
            description="TEST_FILE_SET_DESCRIPTION",
            file_location="/home/TEST_DIR",
            compression="TESTCOMP",
        )

        self.assertEqual(file_contents, expected_contents)

        # Ensure we get an exception when the file already exists.
        with self.assertRaises(FileExistsError):
            util.write_file_set_file(
                "TEST_FILE_SET",
                "TEST_FILE_SET_DESCRIPTION",
                "/home/TEST_DIR",
                "TESTCOMP",
            )

        # Assert that we have logged the error from above.
        util.LOGGER.error.assert_called_with(
            f"FileSet file for 'TEST_FILE_SET' already exists at "
            f"{config.JOB_FILE_LOCATION}/TEST_FILE_SET.conf"
        )

        # Test remove.
        util.remove_file_set_file("TEST_FILE_SET")
        self.assertFalse(
            os.path.exists(f"{config.FILESET_FILE_LOCATION}/TEST_FILE_SET.conf")
        )

        # Ensure we logged properly.
        util.LOGGER.info.assert_called_with(
            f"Removed FileSet file at {config.FILESET_FILE_LOCATION}/TEST_FILE_SET.conf"
        )

        # Ensure we get an exception when the file doesn't exist.
        with self.assertRaises(FileNotFoundError):
            util.remove_file_set_file("TEST_FILE_SET")

        # Assert that we logged the error from above.
        util.LOGGER.error.assert_called_with(
            f"FileSet file for 'TEST_FILE_SET' not found at "
            f"{config.JOB_FILE_LOCATION}/TEST_FILE_SET.conf"
        )

    @patch("util.mysql.connector", autospec=mysql.connector)
    def test_get_dir_from_db(self, mock_cnx):
        """
        Testing get_dir_from_db method.
        """
        # Mock returned objects.
        cnx = mock_cnx.connect.return_value = MagicMock(
            autospec=mysql.connector.MySQLConnection
        )
        cur = cnx.cursor.return_value = MagicMock(
            autospec=mysql.connector.cursor.MySQLCursor
        )

        # Setting the return value for 'for name, homedir_source in cur'.
        cur.__iter__.return_value = (
            ("TEST_USER", "test.chpc.edu:/uufs/home/test_user"),
            ("TEST_USER1", "test.chpc.edu:/uufs/home/test_user1"),
        )

        res = util.get_dir_from_db(["TEST_USER", "TEST_USER1", "TEST_USER2"])

        # Compare returned results.
        self.assertEqual(
            res,
            {
                "TEST_USER": "test.chpc.edu:/uufs/home/test_user",
                "TEST_USER1": "test.chpc.edu:/uufs/home/test_user1",
                "TEST_USER2": None,
            },
        )

        # Ensure .execute was called correctly.
        cur.execute.assert_called_with(
            "SELECT name, homedir_source FROM accounts_user WHERE name in (%s,%s,%s)",
            ("TEST_USER", "TEST_USER1", "TEST_USER2"),
        )

        # Sanity check to ensure we closed resources.
        cur.close.assert_called()
        cnx.close.assert_called()

        # Test edge case with no directories retrieved from the DB.
        cur.__iter__.return_value = ()

        res = util.get_dir_from_db(["TEST_USER", "TEST_USER1", "TEST_USER2"])

        # Compare returned results.
        self.assertEqual(
            res, {"TEST_USER": None, "TEST_USER1": None, "TEST_USER2": None}
        )

    @patch("util.mysql.connector", autospec=mysql.connector)
    def test_get_pe_dir_from_db(self, mock_cnx):
        """
        Testing get_pe_dir_from_db method.
        """
        # Mock returned objects.
        cnx = mock_cnx.connect.return_value = MagicMock(
            autospec=mysql.connector.MySQLConnection
        )
        cur = cnx.cursor.return_value = MagicMock(
            autospec=mysql.connector.cursor.MySQLCursor
        )

        # Setting the return value for 'for name, homedir_source in cur'.
        cur.__iter__.return_value = (
            ("TEST_USER", "test.chpc.edu:/uufs/home/test_user"),
            ("TEST_USER1", "test.chpc.edu:/uufs/home/test_user1"),
        )

        res = util.get_pe_dir_from_db(["TEST_USER", "TEST_USER1", "TEST_USER2"])

        # Compare returned results.
        self.assertEqual(
            res,
            {
                "TEST_USER": "test.chpc.edu:/uufs/home/test_user",
                "TEST_USER1": "test.chpc.edu:/uufs/home/test_user1",
                "TEST_USER2": None,
            },
        )

        # Ensure .execute was called correctly.
        cur.execute.assert_called_with(
            (
                "SELECT name, pe_homedir_source FROM accounts_user WHERE name in "
                "(%s,%s,%s)"
            ),
            ("TEST_USER", "TEST_USER1", "TEST_USER2"),
        )

        # Sanity check to ensure we closed resources.
        cur.close.assert_called()
        cnx.close.assert_called()

        # Test edge case with no directories retrieved from the DB.
        cur.__iter__.return_value = ()

        res = util.get_pe_dir_from_db(["TEST_USER", "TEST_USER1", "TEST_USER2"])

        # Compare returned results.
        self.assertEqual(
            res, {"TEST_USER": None, "TEST_USER1": None, "TEST_USER2": None}
        )

    @patch("util.Repo", autospec=git.Repo)
    def test_push_to_gitlab(self, mock_repo):
        """
        Testing the 'push_to_gitlab' method.
        """
        mock_repo.return_value = MagicMock(autospec=git.Repo)

        # Test the bare exception.
        mock_repo.return_value.bare = True
        with self.assertRaises(FileNotFoundError):
            util.push_to_gitlab("test message")

        # Ensure this was logged.
        util.LOGGER.error.assert_called_with(
            f"{config.GIT_LOCATION} is not an initialized git repo."
        )

        # Reset bare flag.
        mock_repo.return_value.bare = False

        # Simulate .add throwing an exception.
        mock_repo.return_value.git.add.side_effect = Exception("TEST ERROR MSG")
        util.push_to_gitlab("test message")

        # Ensure this was logged.
        util.LOGGER.critical.assert_called_with(
            "Failed to push to GitLab due to: TEST ERROR MSG"
        )

        # Reset the exception side effect.
        mock_repo.return_value.git.add.side_effect = None

        # Full test.
        util.push_to_gitlab("test")
        mock_repo.return_value.git.push.assert_called_once()
        util.LOGGER.info.assert_called_with(
            "Pushing to GitLab with commit message: 'test'"
        )


class TestUtilMethodsConfig(unittest.TestCase):
    """
    Test actual configuration settings to ensure they work on the current
    host this script is located at (ex: checking to ensure we can connect
    to the specified database).
    """

    @classmethod
    def setUpClass(cls):
        util.LOGGER = MagicMock(spec=logging.Logger)

    def test_push_to_gitlab(self):
        """
        Test to ensure we're working with a valid git repository and can
        connect to GitLab (tested with git.pull())
        """
        util.push_to_gitlab("this is a blank commit")

        # Verifying the error message we should have gotten, indicating .pull()
        # worked.
        util.LOGGER.critical.assert_called_with(
            "Failed to push to GitLab due to: Cmd('git') failed due to: exit code(1)\n"
            "  cmdline: git commit -m this is a blank commit\n  stdout: '# On branch "
            "master\nnothing to commit, working directory clean'"
        )

    def test_get_dir_from_db(self):
        """
        Testing to ensure we can connect to the database.

        Usually it's bad practice to add connections to tests as tests
        are meant to be run frequently. I'm assuming these are going to
        be run infrequently.
        """
        # Checking the connection for the first attempted connection.
        try:
            res = util.get_dir_from_db([valid_chpc_user])
        except mysql.connector.errors.DatabaseError as e:
            self.fail(str(e))

        self.assertTrue(valid_chpc_user in res)
        self.assertTrue(res[valid_chpc_user] is not None)

        res = util.get_dir_from_db(["BRS_BACKUP_TEST_USER", valid_chpc_user])

        self.assertTrue("BRS_BACKUP_TEST_USER" in res)
        self.assertTrue(valid_chpc_user in res)

        self.assertTrue(res["BRS_BACKUP_TEST_USER"] is None)
        self.assertTrue(res[valid_chpc_user] is not None)

    def test_get_pe_dir_from_db(self):
        """
        Testing to ensure we can connect to the database and get PE results.

        Usually it's bad practice to add connections to tests as tests
        are meant to be run frequently. I'm assuming these are going to
        be run infrequently.
        """
        # Checking the connection for the first attempted connection.
        try:
            res = util.get_pe_dir_from_db([valid_chpc_user])
        except mysql.connector.errors.DatabaseError as e:
            self.fail(str(e))

        self.assertTrue(valid_chpc_user in res)
        self.assertTrue(res[valid_chpc_user] is not None)

        res = util.get_pe_dir_from_db(["BRS_BACKUP_TEST_USER", valid_chpc_user])

        self.assertTrue("BRS_BACKUP_TEST_USER" in res)
        self.assertTrue(valid_chpc_user in res)

        self.assertTrue(res["BRS_BACKUP_TEST_USER"] is None)
        self.assertTrue(res[valid_chpc_user] is not None)


if __name__ == "__main__":
    unittest.main()
