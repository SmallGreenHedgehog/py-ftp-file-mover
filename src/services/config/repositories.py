from abc import ABC, abstractmethod
from pydoc import locate
from typing import Optional, Type, cast

import settings
from entities.ftp_tasks import FTPTransferMethod, FTPTask
from services.config.drivers import SQLDriver


class ConfigRepository(ABC):
    @abstractmethod
    def create_task(self, task: FTPTask) -> int:
        pass

    @abstractmethod
    def get_tasks(self, task_id: Optional[int] = None) -> list[FTPTask]:
        pass

    @abstractmethod
    def update_task(self, task: FTPTask) -> bool:
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> bool:
        pass


class SQLiteConfigRepository(ConfigRepository):
    _driver_class_path: str = 'services.config.drivers.SQLiteDriver'

    def __init__(self, *args, **kwargs):
        self.__initialize_driver()
        self.__init_config()

    def __initialize_driver(self):
        driver_class: Type[SQLDriver] = cast(Type[SQLDriver], locate(self._driver_class_path))
        self._driver = driver_class(db_path=settings.CONFIG_DB_PATH)

    def __init_config(self):
        self._driver.send_request(
            sql_query='''
                      CREATE TABLE IF NOT EXISTS ftp_tasks
                      (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          local_dir        TEXT    NOT NULL,
                          ftp_host         TEXT    NOT NULL,
                          ftp_port         INTEGER NOT NULL,
                          ftp_dir          TEXT    NOT NULL,
                          ftp_login        TEXT    NOT NULL,
                          ftp_password     TEXT    NOT NULL,
                          transfer_method  TEXT    NOT NULL,
                          signal_file_path TEXT    NOT NULL,
                          signal_text      TEXT    NOT NULL,
                          is_enabled       BOOLEAN NOT NULL
                      )'''
        )

    def create_task(self, task: FTPTask) -> bool:
        response = self._driver.send_request(
            sql_query='''
                      INSERT INTO ftp_tasks(
                        local_dir,
                        ftp_host,
                        ftp_port,
                        ftp_dir,
                        ftp_login,
                        ftp_password,
                        transfer_method,
                        signal_file_path,
                        signal_text,
                        is_enabled
                      )
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                      ''',
            params=(
                task.local_dir,
                task.ftp_host,
                task.ftp_port,
                task.ftp_dir,
                task.ftp_login,
                task.ftp_password,
                task.transfer_method.value,
                task.signal_file_path,
                task.signal_text,
                task.is_enabled,
            ),
            write=True,
        )
        result = bool(response['rowcount'])
        return result

    def get_tasks(self, task_id: Optional[int] = None) -> list[FTPTask]:
        if task_id is not None:
            sql_query = 'SELECT * FROM ftp_tasks WHERE id = ?'
            params = (task_id,)
        else:
            sql_query = 'SELECT * FROM ftp_tasks'
            params = ()

        response = self._driver.send_request(
            sql_query=sql_query,
            params=params,
            write=False,
        )
        result = [self.__row_to_task(row) for row in response['rows']]
        return result

    @staticmethod
    def __row_to_task(row) -> FTPTask:
        task_from_row = FTPTask(
            id=row['id'],
            local_dir=row['local_dir'],
            ftp_host=row['ftp_host'],
            ftp_port=row['ftp_port'],
            ftp_dir=row['ftp_dir'],
            ftp_login=row['ftp_login'],
            ftp_password=row['ftp_password'],
            transfer_method=FTPTransferMethod(row['transfer_method']),
            signal_file_path=row['signal_file_path'],
            signal_text=row['signal_text'],
            is_enabled=bool(row['is_enabled']),
        )
        return task_from_row

    def update_task(self, task: FTPTask) -> bool:
        if task.id is None:
            raise ValueError('Task ID must be set for update')

        response = self._driver.send_request(
            sql_query='''
                      UPDATE ftp_tasks
                      SET local_dir        = ?,
                          ftp_host         = ?,
                          ftp_port         = ?,
                          ftp_dir          = ?,
                          ftp_login        = ?,
                          ftp_password     = ?,
                          transfer_method  = ?,
                          signal_file_path = ?,
                          signal_text      = ?,
                          is_enabled       = ?
                      WHERE id = ?
                      ''',
            params=(
                task.local_dir,
                task.ftp_host,
                task.ftp_port,
                task.ftp_dir,
                task.ftp_login,
                task.ftp_password,
                task.transfer_method.value,
                task.signal_file_path,
                task.signal_text,
                task.is_enabled,
                task.id,
            ),
            write=True,
        )
        result = response['rowcount'] > 0
        return result

    def delete_task(self, task_id: int) -> bool:
        response = self._driver.send_request(
            sql_query='DELETE FROM ftp_tasks WHERE id = ?',
            params=(task_id,),
            write=True,
        )
        result = response['rowcount'] > 0
        return result


def get_config_repository() -> ConfigRepository:
    return SQLiteConfigRepository()
