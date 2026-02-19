from loguru import logger

from services.config.repositories import get_config_repository
from services.tasks_processor import FTPTaskProcessor


@logger.catch(message='Exception on run task "process_ftp_tasks"')
def process_ftp_tasks():
    config_repository = get_config_repository()
    ftp_tasks = config_repository.get_tasks()

    FTPTaskProcessor.process_tasks(ftp_tasks)
