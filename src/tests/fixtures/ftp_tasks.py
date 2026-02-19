import itertools

from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory

from entities.ftp_tasks import FTPTask


class FTPTaskFixturesFactory(ModelFactory[FTPTask]):
    __model__ = FTPTask
    _id_counter = itertools.count(start=1)
    _login_counter = itertools.count(start=1)

    id = Use(lambda: next(FTPTaskFixturesFactory._id_counter))
    ftp_login = Use(lambda: f'user{next(FTPTaskFixturesFactory._login_counter):03d}')

    ftp_password = 'P@ssw0rd-default'
    ftp_host = 'test.ftp.local'
    local_dir = '/app/ftp/incoming'
    ftp_dir = '/uploads/tasks'
    ftp_port = 21
    signal_file_path = 'ready.signal'
    signal_text = 'TASK_READY'
    is_enabled = True
