from services.config.repositories import SQLiteConfigRepository
from tests.core import BaseTestCase
from tests.fixtures.ftp_tasks import FTPTaskFixturesFactory


class TestSQLiteConfigRepository(BaseTestCase):
    DEFAULT_TASKS_QUANTITY = 5

    def setUp(self):
        super().setUp()

        self._config_repository = SQLiteConfigRepository()
        self._tasks_factory = FTPTaskFixturesFactory()

    def test_create_config(self):
        expected_tasks_quantity = self.DEFAULT_TASKS_QUANTITY
        expected_logins = {f'user{i:03d}' for i in range(1, expected_tasks_quantity + 1)}

        tasks_to_create = self._tasks_factory.batch(expected_tasks_quantity)

        for task in tasks_to_create:
            success = self._config_repository.create_task(task)
            self.assertTrue(success)

        retrieved_tasks = self._config_repository.get_tasks()

        self.assertEqual(expected_tasks_quantity, len(retrieved_tasks))
        self.assertEqual(expected_logins, {t.ftp_login for t in retrieved_tasks})

    def test_get_tasks_all(self):
        expected_tasks_quantity = self.DEFAULT_TASKS_QUANTITY

        tasks_to_create = self._tasks_factory.batch(expected_tasks_quantity)

        for task in tasks_to_create:
            success = self._config_repository.create_task(task)
            self.assertTrue(success)

        retrieved_tasks = self._config_repository.get_tasks()

        self.assertEqual(expected_tasks_quantity, len(retrieved_tasks))

    def test_get_tasks_by_id(self):
        task_to_create = self._tasks_factory.build()
        success = self._config_repository.create_task(task_to_create)
        self.assertTrue(success)

        retrieved_tasks = self._config_repository.get_tasks()
        created_task_id = retrieved_tasks[0].id

        retrieved_tasks = self._config_repository.get_tasks(task_id=created_task_id)

        self.assertEqual(1, len(retrieved_tasks))
        self.assertEqual(created_task_id, retrieved_tasks[0].id)
        self.assertEqual(task_to_create.ftp_login, retrieved_tasks[0].ftp_login)

    def test_get_tasks_non_existing_id(self):
        retrieved_tasks = self._config_repository.get_tasks(task_id=999999)
        self.assertEqual([], retrieved_tasks)

    def test_update_task_success(self):
        original_login = 'original-login'
        updated_login = 'updated-login'

        task_to_create = self._tasks_factory.build(
            ftp_login=original_login,
            is_enabled=True,
        )
        success = self._config_repository.create_task(task_to_create)
        self.assertTrue(success)

        retrieved_tasks = self._config_repository.get_tasks()
        created_task_id = retrieved_tasks[0].id

        task_to_update = task_to_create.model_copy(update={'id': created_task_id})
        task_to_update.ftp_login = updated_login
        task_to_update.is_enabled = False

        was_updated = self._config_repository.update_task(task_to_update)

        self.assertTrue(was_updated)

        retrieved_tasks = self._config_repository.get_tasks(task_id=created_task_id)
        self.assertEqual(1, len(retrieved_tasks))
        self.assertEqual(updated_login, retrieved_tasks[0].ftp_login)
        self.assertFalse(retrieved_tasks[0].is_enabled)

    def test_update_task_non_existing(self):
        non_existing_task = self._tasks_factory.build()
        non_existing_task.id = 777777

        was_updated = self._config_repository.update_task(non_existing_task)

        self.assertFalse(was_updated)

    def test_update_task_without_id(self):
        task_without_id = self._tasks_factory.build()
        task_without_id.id = None

        with self.assertRaises(ValueError):
            self._config_repository.update_task(task_without_id)

    def test_delete_task_success(self):
        task_to_delete = self._tasks_factory.build()
        success = self._config_repository.create_task(task_to_delete)
        self.assertTrue(success)

        retrieved_tasks = self._config_repository.get_tasks()
        created_task_id = retrieved_tasks[0].id

        was_deleted = self._config_repository.delete_task(task_id=created_task_id)

        self.assertTrue(was_deleted)

        remaining_tasks = self._config_repository.get_tasks(task_id=created_task_id)
        self.assertEqual([], remaining_tasks)

    def test_delete_task_non_existing(self):
        was_deleted = self._config_repository.delete_task(888888)
        self.assertFalse(was_deleted)
