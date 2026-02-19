from entities.ftp_tasks import FTPTask


class FTPTaskProcessor:
    def __init__(self, ftp_task):
        self._ftp_task = ftp_task

    def process(self):
        # TODO: implement logic for ftp_tasks' processing
        pass

    @classmethod
    def process_tasks(cls, ftp_tasks: list[FTPTask]):
        for current_ftp_task in ftp_tasks:
            cls(current_ftp_task).process()
