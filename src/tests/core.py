import os
from unittest import TestCase

import settings


class BaseTestCase(TestCase):
    TEST_DB_PATH = '../test_config.sqlite'

    def setUp(self):
        self._remove_test_database_file()
        self._patch_test_database()

    def _patch_test_database(self):
        self._original_db_path = settings.CONFIG_DB_PATH
        settings.CONFIG_DB_PATH = self.TEST_DB_PATH

    def _remove_test_database_file(self):
        if os.path.exists(self.TEST_DB_PATH):
            os.remove(self.TEST_DB_PATH)

    def tearDown(self):
        self._restore_original_database()

    def _restore_original_database(self):
        settings.CONFIG_DB_PATH = self._original_db_path
