import schedule
from loguru import logger

from tasks import process_ftp_tasks

if __name__ == '__main__':
    logger.info('Start run_service module')
    schedule.every(10).minutes.do(process_ftp_tasks)
